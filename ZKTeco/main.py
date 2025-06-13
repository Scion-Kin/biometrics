#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''
    Copyright (c) 2024-2025 Buffer Park Technologies Pvt. Ltd.
    This module will be open-sourced under the GNU General Public License v3.0.
    Before that, under no circumstances should this module be used by non-licensed users.
    To obtain a license, please see license information at the top level of this repository.

    This module is used to integrate ZKTeco biometric devices with ERPNext or other ERPs.
    It provides functions to fetch attendance data from the device and
    update the attendance records in ERPNext.
'''

import sys, importlib
from logger import logger
from datetime import datetime
from bio_config import devices
from db import db

def handleExit(type, code=0):
    if (type == 'error'): logger.log('MGS exit on error. Exiting...', 'ERROR')
    else: logger.log('MGS graceful exit. Shutting down. Please wait...', 'INFO')
    """if '--no-cache' not in sys.argv and cache_source == 'redis': redis_client.close()"""

    db.close_connection()
    logger.close()
    exit(code)


def gISOl(date):
    return date.strftime('%Y-%m-%dT%H:%M:%S')


supported_erps = {'ERPNext', 'MilMall'}

if '-m' in sys.argv or '--module' in sys.argv:
    try:
        module_index = sys.argv.index('-m') if '-m' in sys.argv else sys.argv.index('--module')
        module_name = sys.argv[module_index + 1]
        if module_name not in supported_erps:
            raise ValueError(f"Unsupported module: {module_name}. Supported modules are: {', '.join(supported_erps)}")
        
        else:
            module = importlib.import_module(module_name.lower())

    except (IndexError, ValueError, ImportError) as e:
        logger.log(f"Error loading module: {e}", 'ERROR')
        handleExit('error', 1)

else:
    logger.close()
    print(f"Usage: {sys.argv[0]} -m <module_name> [options]")
    print(f"Supported modules: {', '.join(supported_erps)}")
    print("Please specify a module to run the script.")
    exit(1)


def run_attendance():
  try:
      if not devices:
        logger.log('Please fill in the necessary details in bio_config.py before running the script', 'ERROR')
        handleExit('error', 1)

      fields = ["employee", "employee_name", "attendance_date", "company", "check_in", "check_out", "status", "attendance_device_id", "default_shift"]
      filters = {}

      employeesData = module.transport.get_users(filters=filters, fields=fields)
      ids = { str(d.get('employee')) for d in employeesData }
      if not employeesData or len(employeesData) == 0:
          logger.log('No employees found. Please check the configuration and try again.', 'ERROR')
          handleExit('error', 1)

      logger.log(f'Employees before filtering: {len(employeesData)}', 'INFO')
      employees = [employee for employee in employeesData if employee.get("employee")]
      logger.log(f'Employees after filtering: {len(employees)}', 'INFO')

      now = datetime.now()
      logger.log(f'Current time: {now}', 'INFO')

      def import_attendance():
          all = db.collect_latest_records()
          all = [record for record in all if record.get('attendance_device_id') in ids]
          logger.log(f'{len(all)} records found', 'INFO')

          if not all or len(all) == 0:
              logger.log('No attendance records found. Please run the puller script first.', 'ERROR')
          else:
              logger.log(f'Found {len(all)} attendance records', 'INFO')

              logger.log('Contacting ERP...', 'INFO')
              for record in all:
                  try:
                      record['attendance_device_id'] = str(record.get('attendance_device_id')) 
                      del record['_id']
                      record['timestamp'] = gISOl(record.get('timestamp'))
                      res = module.transport.decide(record)
                      logger.log(f'Response from ERP: {res}', 'INFO')

                  except Exception as error:
                      logger.log(f'Error processing record {record.get("attendance_device_id")}: {error}', 'ERROR')
                      pass

      now = datetime.now()
      import_attendance()

      finish = (datetime.now() - now).total_seconds()
      logger.log(f'Attendance marking complete! Finished in ' + (f'{finish // 3600} hours, {(finish % 3600) // 60} minutes and {finish % 60} seconds' if finish > 3600 else f'{finish // 60} minutes and {finish % 60} seconds'), 'SUCCESS')
      logger.log('Operation successful!', 'SUCCESS')
      handleExit('success')

  except (Exception) as error:
      logger.log(error, 'ERROR')
      handleExit('error', 1)


if __name__ == '__main__':
    logger.log('All processes started', 'INFO')
    run_attendance()


"""prevs = {}

if '--no-cache' not in sys.argv:
    for employee in employees:
        try:
            attendance_device_id = employee.get('attendance_device_id')
            if not attendance_device_id:
                continue
            attendance = redis_client.get(f'MGS-attendance-{attendance_device_id}')
            if not attendance:
                continue
            prevs[attendance_device_id] = datetime.fromisoformat(attendance)

        except Exception as error:
            log(f'Possible Redis error: {error}\nExiting to avoid data corruption for any employee. Please fix the Redis error and restart the script.', 'ERROR')
            handleExit('error', 1)
else:
    log('Skipping Redis cache check', WARNING)"""

# start_time = now.replace(minute=0, second=0, microsecond=0) - timedelta(hours=maxWorkHours)
# end_time = now.replace(minute=0, second=0, microsecond=0)
""" if got:
    log('Processing...', 'INFO')
    attendance_map = {}

    for event in got:
        user_id = event.user_id
        event_time = event.timestamp
        emp = next((e for e in employees if e["attendance_device_id"] == user_id), None)

        if not emp:
            continue

        if user_id in prevs and prevs[user_id] >= event_time:
            continue

        if user_id not in attendance_map:
            attendance_map[user_id] = {"IN": None, "OUT": None}

        attendance = attendance_map[user_id]

        if updateFor and emp["default_shift"] in updateFor and attendance["IN"] and attendance["IN"]["time"].date() != event_time.date():
            attendance["IN"] = None
            attendance["OUT"] = None

        if not attendance["IN"] or attendance["IN"]["time"] > event_time:
            if updateFor and emp["default_shift"] in updateFor and 0 < event_time.weekday() < 6 and event_time.hour > 12:
                continue
            attendance["IN"] = {"time": event_time, "event": event}
        else:
            if attendance["IN"] and (event_time - attendance["IN"]["time"]).total_seconds() > 3600:
                if not attendance["OUT"] or attendance["OUT"]["time"] < event_time:
                    attendance["OUT"] = {"time": event_time, "event": event}

    log(f'Found {len(attendance_map)} events for {len(attendance_map)} employees', 'INFO') """

""" if '--no-cache' in sys.argv:
    log('Checkouts will not be cached in Redis', WARNING) """


""" async def renew_session(device):
  while True:
    await asyncio.sleep(30)  # renews every 30 seconds

    # Only renew session if the device has been authenticated to avoid unnecessary logins
    if not device.get("authenticated"):
      continue

    log(f'Renewing session for {device.get("name")}...', 'INFO')
    try:
      res = requests.put(
        f'{device.get("apiURL")}/ISAPI/Security/sessionHeartbeat',
        headers=device["auth"]["headers"]
      )
      if not res.ok:
        raise Exception(f'Could not renew session. Error:\n{res.text}')
    except Exception as err:
      log(f'Failed to renew session: {err}', 'ERROR')
      log('Retrying...', WARNING)
      try:
        res = requests.post(
          f'{device.get("apiURL")}/ISAPI/Security/sessionHeartbeat',
          headers=device["auth"]["headers"]
        )
        if not res.ok:
          log('Failed to renew session', 'ERROR')
          log('Logging in again...', DEBUG)
          try:
            new_auth = await logon(device.get("username"), device.get("password"), device.get("apiURL"))
            device["auth"] = new_auth
          except Exception as login_err:
            log(f'Login failed: {login_err}', WARNING)
            log('Maximum retries reached. Exiting...', 'ERROR')
            await handleExit('error', 1)
        else:
          log('Session renewed successfully!', 'SUCCESS')
      except Exception as retry_err:
        log(f'Failed to renew session: {retry_err}\nMax retries reached. Exiting...', 'ERROR')
        await handleExit('error', 1)
    else:
      log('Session renewed successfully!', 'SUCCESS')

session_renewals = []
for device in devices:
  session_renewals.append(renew_session(device)) """


"""for employeeNo, attendance in attendance_map.items():
  IN, OUT = attendance["IN"], attendance["OUT"]
  if IN and OUT:
    INTime = IN["time"]
    OUTTime = OUT["time"]
    emp = next((employee for employee in employees if employee["attendance_device_id"] == employeeNo), None)
    ii = gISOl(INTime)
    oo = gISOl(OUTTime)

    # Check if the difference between IN and OUT is greater than 1 hour
    if (OUTTime - INTime).total_seconds() / 3600 < 1:
        log(f'Work hours for {emp["employee_name"]} is less than 1 hour. Skipping...', WARNING)
        continue

    if updateFor and emp["default_shift"] in updateFor and INTime.date() != OUTTime.date() and OUTTime.hour > 0:
        log(f'Employee {emp["employee_name"]} is whitelisted for the update policy, but the check-in and check-out dates are different. Skipping...', WARNING)
        redis_client.set(f'MGS-attendance-{employeeNo}', ii)
        continue

    inD = ii.split('T')[0]
    outD = oo.split('T')[0]
    inT = ii.split('T')[1]
    outT = oo.split('T')[1]
    attendance_date = outD if INTime.hour >= 23 else inD

    if '--dry-run' in sys.argv:
      print(f'{emp["employee_name"]}: {inT} -> {outT}')
      continue

    if '--no-cache' not in sys.argv:
        redis_client.set(f'MGS-attendance-{employeeNo}', oo)

    body = {
      "employee": emp["employee"],
      "attendance_date": attendance_date,
      "chekin": inT,
      "check_out": outT,
      "status": "Present",
    }

    for retry in range(3):
      try:
        attendance_response = requests.post(f"{frappe_api_url}/api/resource/Attendance", headers=headers, json=body)

        if not attendance_response.ok:
          res = attendance_response.json()
          if res.get("exc_type") != "DuplicateAttendanceError":
            log(f"Failed to create attendance for {emp.get('employee_name')} with Device ID: ({employeeNo})\nError: {res}", 'ERROR')

          if res.get("exc_type") == "DuplicateAttendanceError" and emp.get("default_shift") in updateFor:
            log(f"Attendance already exists. Updating attendance (in {emp.get("default_shift")}) for {emp.get('employee_name')}...", 'INFO')
            doc_name = res["exception"].split("/")[-1]
            re = requests.get(f"{frappe_api_url}/api/resource/Attendance/{doc_name}", headers=headers)
            record = re.json().get("data", {})

            if record.get("attendance_date") != attendance_date:
              log("Error: Attendance date mismatch. Skipping...", 'ERROR')
              break

            chekin = datetime.fromisoformat(f"{attendance_date}T{record['chekin']}")
            if OUTTime > chekin:
              body["work_hours"] = (OUTTime - chekin).total_seconds() / 3600

            body["chekin"] = chekin.strftime("%H:%M:%S")
            attendance_res = requests.put(f"{frappe_api_url}/api/resource/Attendance/{doc_name}", headers=headers, json=body)

            if not attendance_res.ok:
              log(f"Failed to update attendance for {emp.get('employee_name')} with Device ID: ({employeeNo})\nError: {attendance_res.text}", 'ERROR')
            else:
              log(f"Attendance updated for {emp.get('employee_name')} with Device ID: ({employeeNo})", 'SUCCESS')
          else:
            log(f"{emp.get('employee_name')}'s Attendance for {attendance_date} already exists for a Non whitelisted Shift. Skipping...", WARNING)
        else:
          log(f"Attendance submitted and cached for {emp.get('employee_name')} with Device ID: ({employeeNo})", 'SUCCESS')
        break
      except Exception as error:
          log(f"Possible network error. Retrying attendance submission for {emp.get('employee_name')}...", WARNING)
          sleep(3)"""

# Import support will be added later.
""" if isImport:
days_diff = (endDate - startDate).days
log(f'Importing {days_diff} days of attendance...', 'INFO')
for i in range(days_diff):
start = startDate + timedelta(days=i)

# The following applies to companies with 24-hour work hours. Please adjust accordingly.
# If your company works on 12-hour or below work hours, there is no need to adjust anything.
for hour in [10, 18, 2]:
a = start.replace(hour=hour, minute=0, second=0, microsecond=0)
if hour == 2:
    a += timedelta(days=1)

b = a - timedelta(hours=(17 if i == 0 and hour == 18 else 11 if i == 0 and hour != 2 else maxWorkHours))
import_attendance(b, a)

if '--clear' in sys.argv:
    print("\033c", end="")

else: """

