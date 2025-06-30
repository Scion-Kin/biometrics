import requests
from datetime import datetime
from milmall.utils import load_storage, format_data, try_auth
from milmall.config import urls, business_id, api_url
from milmall.exceptions import AttendanceFetchError, AuthenticationError, NetworkError, AuthenticationError, UnknownResponseError, TokenRefreshError

default_headers = {
    'Content-Type': 'application/json',
    'Accept': 'application/json',
    'User-Agent': 'Mozilla/5.0 (compatible; MilMallBot/1.0; +https://milmall.rw/bot)'
}

def get_attendance(uid, auth) -> dict:
    """
    Fetches attendance data for a specific user from the MilMall API.

    :param uid: The unique identifier for the user
    :param auth: A dictionary containing authentication details (access token)
    :return: A dictionary containing the attendance data
    """
    if 'access_token' not in auth:
        raise AuthenticationError("Access token is missing. Please login or refresh the token.")

    headers = { 'Authorization': f"Bearer {auth['access_token']}", **default_headers }

    url = f"{api_url}{urls['attendance']}/{uid}?business_id={business_id}"

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        data = response.json()["data"] if isinstance(response.json()["data"], dict) else {'id': None}
        del data['id']  # Remove the 'id' field from the data since it references an attendance record in the MilMall API rather than a user ID.
        data = format_data(data, True)
        return data

    else:
        raise AttendanceFetchError(f"Failed to fetch attendance data for user {uid}: {response.text}")


def get_users(filters: dict={}, fields: list=[]) -> dict:
    """
    Fetches employee data from the MilMall API.

    :param user: The user identifier (optional, defaults to None)
    :return: Employee data as a dictionary
    """

    auth = load_storage()
    if not auth or 'access_token' not in auth:
        auth = try_auth()

    headers = { 'Authorization': f"Bearer {auth['access_token']}", **default_headers }

    user = f'/{filters.get('user')}' if filters.get('user') else ''
    url = f"{api_url}{urls['employee']}{user}?business_id={business_id}"

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        data = response.json().get("data")
        data = [format_data(item, True, fields) for item in data] if isinstance(data, list) else format_data(data, True, fields)
        return data
    else:
        raise UnknownResponseError(f"Failed to fetch employee data: {response.text}")


def decide(data) -> requests.Response:
    """
    Logic to handle check-in/check-out based on the provided data.
    This function checks the current attendance status of the user and decides whether to clock in or clock out.

    :param data: A dictionary containing the check-in data
    :return: The response from the API
    """
    auth = load_storage()

    if not auth:
        auth = try_auth()

    d = format_data(data)
    d['timestamp'] = datetime.strptime(d.get('timestamp'), '%Y-%m-%dT%H:%M:%S')
    attendance = get_attendance(d.get('user_id', data.get('attendance_device_id')), auth)

    prev = attendance.get('check_out', None)
    if prev:
        time = datetime.strptime(prev, '%Y-%m-%d %H:%M:%S')
        if d.get('timestamp') <= time:
            return requests.Response()

        else:
            return clock_in(d, auth)

    else:
        prev = attendance.get('check_in')
        if prev:
            time = datetime.strptime(prev, '%Y-%m-%d %H:%M:%S')
            if d.get('timestamp') <= time:
                return requests.Response()
            else:
                return clock_out(d, auth)

        else:
            return clock_in(d, auth)


def clock_in(data, auth) -> requests.Response:
    """
    Sends a clock-in request to the MilMall API.

    :param data: A dictionary containing the clock-in data
    :param auth: A dictionary containing authentication details (access token)
    :return: The response from the API
    """
    try:
        if 'access_token' not in auth:
            raise AuthenticationError("Access token is missing. Please login or refresh the token.")

        headers = { 'Authorization': f"Bearer {auth['access_token']}", **default_headers }

        # Ensure data is formatted correctly (Compatible with MilMall API)
        if data.get('timestamp'):
            data['clock_in_time'] = data.pop('timestamp')

        else:
            raise ValueError("Timestamp is required for clock-in data.")

        url = f"{api_url}{urls['clockin']}?business_id={business_id}"

        response = requests.post(url, json=data, headers=headers)

        if response.status_code == 200:
            return response
        else:
            if response.status_code == 400 and "Already clocked in" in response.text:
                data['check_out'] = data.pop('clock_in_time')
                return clock_out(data, auth)  # If already clocked in, clock out first.
            else:
                raise UnknownResponseError(f"Failed to clock in: {response.text}")

    except requests.RequestException as e:
        raise NetworkError(f"Network error occurred while clocking in: {str(e)}")


def clock_out(data, auth) -> requests.Response:
    """
    Sends a clock-out request to the MilMall API.

    :param data: A dictionary containing the clock-out data
    :param auth: A dictionary containing authentication details (access token)
    :return: The response from the API
    """
    try:
        if 'access_token' not in auth:
            raise AuthenticationError("Access token is missing. Please login or refresh the token.")

        headers = { 'Authorization': f"Bearer {auth['access_token']}", **default_headers }

        # Ensure data is formatted correctly (Compatible with MilMall API)
        if data.get('timestamp') or data.get('check_out'):
            data['clock_out_time'] = data.pop('timestamp') if 'timestamp' in data else data.get('check_out')

        else:
            raise ValueError("Timestamp is required for clock-out data.")

        url = f"{api_url}{urls['clockout']}?business_id={business_id}"

        response = requests.post(url, json=data, headers=headers)

        if response.status_code == 200:
            return response
        else:
            raise UnknownResponseError(f"Failed to clock out: {response.text}")

    except requests.RequestException as e:
        raise NetworkError(f"Network error occurred while clocking out: {str(e)}")
