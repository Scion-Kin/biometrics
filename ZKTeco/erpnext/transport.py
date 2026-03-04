import requests
from datetime import datetime
from erpnext.config import urls, api_url, frappe_api_key, frappe_secret_key
from erpnext.exceptions import AttendanceFetchError, NetworkError, UnknownResponseError
from logger import logger


default_headers = {
    'Content-Type': 'application/json',
    'Accept': 'application/json',
    'User-Agent': 'Mozilla/5.0 (compatible; AttendanceBot/1.0; +https://bufferpunk.com/)',
    'Authorization': f'token {frappe_api_key}:{frappe_secret_key}'
}

def get_time(dt: str|datetime, reverse=False) -> datetime | str:
    """
    Converts a datetime object to a string in the format 'YYYY-MM-DD HH:MM:SS'.

    :param dt: The datetime object to convert
    :return: A datetime object
    """
    try:
        return datetime.strptime(dt, '%Y-%m-%dT%H:%M:%S') if not reverse else dt.strftime('%Y-%m-%dT%H:%M:%S')
    except ValueError:
        return datetime.strptime(dt, '%Y-%m-%d %H:%M:%S') if not reverse else dt.strftime('%Y-%m-%d %H:%M:%S')


def get_last_checkin(uid) -> dict:
    """
    Fetches attendance data for a specific user from the erpnext API.

    :param uid: The unique identifier for the user
    :param auth: A dictionary containing authentication details (access token)
    :return: A dictionary containing the attendance data
    """
    url = "{}{}?filters={}&limit_page_length=1&order_by={}&fields={}".format(
        api_url, urls['checkin'], {'employee': uid},
        'max(time) desc', ["employee", "max(time) as time", "log_type"]
    )
    response = requests.get(url, headers=default_headers)

    if response.status_code == 200:
        data = response.json()["data"] if isinstance(response.json()["data"], dict) else {}
        return data[0]

    else:
        raise AttendanceFetchError(f"Failed to fetch attendance data for user {uid}: {response.text}")


def get_all_checkins(ids: list = []) -> list:
    """
    Fetches attendance data for a list of users from the erpnext API.

    :param ids: A list of user identifiers
    :return: A list of dictionaries containing the attendance data
    """
    url = "{}{}?filters={}&group_by='employee'&order_by={}&fields={}".format(
        api_url, urls['checkin'], {'employee': ["in", ids]} if ids else {},
        'max(time) desc', ["employee", "max(time) as time", "log_type"]
    )
    response = requests.get(url, headers=default_headers)
    if response.status_code == 200:
        data = response.json().get("data", [])
        return data
    else:
        raise AttendanceFetchError(f"Failed to fetch attendance data for users {ids}: {response.text}")


def get_users(filters: dict={}, fields: list=[]) -> dict:
    """
    Fetches employee data from the erpnext API.

    :param user: The user identifier (optional, defaults to None)
    :return: Employee data as a dictionary
    """

    filters = {"attendance_device_id": filters.get('user')} if filters.get('user') else filters
    url = "{}{}?filters={}&fields={}".format(api_url, urls['employee'], {**filters, "status": "Active"}, ["employee", "employee_name", "attendance_device_id"])
    response = requests.get(url, headers=default_headers)

    if response.status_code == 200:
        data = response.json().get("data")
        return data
    else:
        raise UnknownResponseError(f"Failed to fetch employee data: {response.text}")


def bulk_submit(records: list, ids: list=[]) -> requests.Response:
    """
    Sends a bulk request to the erpnext API to process checkin logs.

    :param records: A list of checkin logs to be processed
    :param attendances: A list of checkin logs to be checked against
    :return: The response from the API
    """
    url = "{}{}".format(api_url, urls['bulk_submit'])
    employees = get_users(filters={"attendance_device_id": ["in", ids]})
    employees = { i.get('attendance_device_id'): i.get("employee") for i in employees }
    last_attendances_dict = { i.employee: i for i in get_all_checkins() }
    collected = []
    for record in records:
        sep = employees.get(record.get('attendance_device_id'))
        try:
            record['attendance_device_id'] = record.get('attendance_device_id')
            record.update({'timestamp': get_time(record.get('timestamp'), True), "employee": sep})
            last = last_attendances_dict.get(sep, {})
            res = decide(record, False, last)
            if res:
                collected.append(res)
                if sep not in last_attendances_dict:
                    last_attendances_dict[sep] = record
                else:
                    last_attendances_dict[sep].update(record)

        except Exception as error:
            logger.error(f'Error processing record {sep}: {error}')

    if len(collected) == 0:
        return requests.Response()

    response = requests.post(url, json={"docs": collected}, headers=default_headers)
    if response.status_code == 200:
        logger.info(response.json())
        return response
    else:
        raise UnknownResponseError(f"Failed to send bulk attendance records: {response.text}")


def decide(d, submit=True, last=None) -> requests.Response | dict | None:
    """
    Logic to handle check-in/check-out based on the provided data.
    This function checks the current attendance status of the user and decides whether to clock in or clock out.

    :param data: A dictionary containing the check-in data
    :return: The response from the API
    """
    rt = get_time(d.get('timestamp'))
    employee = d.get("employee") or get_users(filters={"user": d.get("attendance_device_id")}).get('employee')
    prev = last or get_last_checkin(employee)
    if prev:
        time: datetime = get_time(prev.get("time"))
        if rt <= time:
            return requests.Response() if submit else None
        else:
            log = {
                "employee": employee,
                "time": get_time(rt, True),
                "log_type": ("OUT" if prev.get("status") == "IN" else "IN") if prev.get("status") else None, # If we don't get a status, that might mean that hr shift type is using "Alternating entries as IN and OUT during the same shift" for "determine_check_in_and_check_out" setting
            }
            return send_checkin(log) if submit else log
    else:
        log = {
            "employee": employee,
            "time": get_time(rt, True),
            "log_type": "IN", # The HR user will have to correct this status if it was OUT instead, but we can assume that if there is no previous attendance record, then this is a check-in
        }
        return send_checkin(log) if submit else log


def send_checkin(data: dict) -> requests.Response:
    """
    Sends a checkin log to the erpnext API.

    :param data: A dictionary containing the checkin data
    :return: The response from the API
    """
    try:
        if data.get('timestamp'):
            data['time'] = data.pop('timestamp')
        else:
            raise ValueError("Timestamp is required for checkin data.")

        url = f"{api_url}{urls['checkin']}"
        response = requests.post(url, json=data, headers=default_headers)

        if response.status_code == 200:
            return response
        else:
            raise UnknownResponseError(f"Failed to send checkin: {response.text}")

    except requests.RequestException as e:
        raise NetworkError(f"Network error occurred while clocking out: {str(e)}")
