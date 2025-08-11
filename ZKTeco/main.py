#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''
    Copyright (c) 2024-2025 Buffer Punk Ltd.
    This module will be open-sourced under the GNU General Public License v3.0.
    Before that, under no circumstances should this module be used by non-licensed users.
    To obtain a license, please see license information at the top level of this repository.

    This module is used to integrate ZKTeco biometric devices with ERPNext or other ERPs.
    It provides functions to fetch attendance data from the device and
    update the attendance records in ERPNext, Laravel, or other supported ERPs.
'''

import sys, importlib
from logger import logger
from datetime import datetime, timedelta
from bio_config import devices
from db import db

def handleExit(type, code=0):
    if (code != 0): logger.error('MGS exit on error. Exiting...')
    else: logger.info('MGS graceful exit. Shutting down. Please wait...')

    db.close_connection()
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
        logger.error(f"Error loading module: {e}")
        handleExit('error', 1)

else:
    print(f"Usage: {sys.argv[0]} -m <module_name> [options]")
    print(f"Supported modules: {', '.join(supported_erps)}")
    print("Please specify a module to run the script.")
    exit(1)


def run_attendance():
  try:
      if not devices:
        logger.error('Please fill in the necessary details in bio_config.py before running the script')
        handleExit('error', 1)

      fields = ["employee", "employee_name", "attendance_date", "company", "check_in", "check_out", "status", "attendance_device_id", "default_shift"]
      filters = {}
      is_import = '--import' in sys.argv

      employeesData = module.transport.get_users(filters=filters, fields=fields)
      if not employeesData or len(employeesData) == 0:
          logger.error('No employees found. Please check the configuration and try again.')
          handleExit('error', 1)

      ids = [ str(d.get('employee')) for d in employeesData ]
      logger.info(f'Employees before filtering: {len(employeesData)}')
      employees = [employee for employee in employeesData if employee.get("employee")]
      logger.info(f'Employees after filtering: {len(employees)}')

      now = datetime.now()
      logger.info(f'Current time: {now}')

      def import_attendance(filters=None):
          records = db.collect_filtered_records(filters=filters) if filters else db.collect_latest_records()
          if not len(records):
              return logger.info('No attendance records found.')
          else:
                logger.info(f'Found {len(records)} attendance records')
                logger.info('Contacting ERP...')

                if "--use-bulk" in sys.argv or "-b" in sys.argv:
                    return module.transport.bulk_submit(records, ids=ids)

                for record in records:
                    try:
                        record['attendance_device_id'] = str(record.get('attendance_device_id'))
                        if record.get('_id'): del record['_id']
                        record['timestamp'] = gISOl(record.get('timestamp'))
                        res = module.transport.decide(record)
                        logger.info(f'Response from ERP: {res}')

                    except Exception as error:
                        logger.error(f'Error processing record {record.get("attendance_device_id")}: {error}')
                        pass

      now = datetime.now()
      if not is_import:
        import_attendance({'attendance_device_id': { '$in': ids }})

      else:
        logger.info('Importing attendance records...')
        if len(sys.argv) > sys.argv.index('--import') + 2:
            from_index = sys.argv.index('--import') + 1
            to_index = sys.argv.index('--import') + 2

            from_date = datetime.strptime(sys.argv[from_index], '%Y-%m-%d')
            to_date = datetime.strptime(sys.argv[to_index], '%Y-%m-%d')
            if from_date > to_date:
                logger.error('The "from" date must be earlier than the "to" date')
                handleExit('error', 1)

            from_date = from_date.replace(hour=0, minute=30, second=0, microsecond=0)
            to_date = to_date.replace(hour=23, minute=59, second=59, microsecond=999999)

            while from_date <= to_date:
                to = from_date + timedelta(hours=1)
                logger.info(f'Importing records from {from_date} to {to}')
                filters = {'timestamp': {'$gte': from_date, '$lt': to}, 'attendance_device_id': {'$in': ids}}
                import_attendance(filters=filters)
                from_date = to

        else:
            logger.error('Please provide the date range for import using --import <from_date> <to_date>')
            handleExit('error', 1)

      finish = (datetime.now() - now).total_seconds()
      logger.success(f'Attendance marking complete! Finished in ' + (f'{finish // 3600} hours, {(finish % 3600) // 60} minutes and {finish % 60} seconds' if finish > 3600 else f'{finish // 60} minutes and {finish % 60} seconds'))
      logger.success('Operation successful!')
      handleExit('success')

  except (Exception) as error:
      logger.error(error)
      handleExit('error', 1)


if __name__ == '__main__':
    logger.info('All processes started')
    run_attendance()
