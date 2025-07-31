#!/usr/bin/env python3

from exec import exec
from bio_config import devices
from db import db
from logger import logger

if __name__ == "__main__":
    for device in devices:
        logger.info(f"Starting attendance puller for device: {device.get('name')}")
        try:
            client = db.get_db('records')
            if client is None:
                logger.error(f"Database connection failed. Skiping device {device.get('name')}.")
                continue

            exec(device, 'disable_device')
            records = exec(device, 'get_attendance')
            if not records or len(records) < 1:
                logger.warning(f"No attendance records found for device: {device['name']}")
                continue

            elif isinstance(records, list):
                records = [
                    {"attendance_device_id": record.user_id, "timestamp": record.timestamp, "status": record.status, "punch": record.punch, "device": device.get('ip')}
                    for record in records
                ]
                re = client.insert_many(records)
                if re.acknowledged:
                    logger.success(f"Inserted {len(re.inserted_ids)} records into the database from: ({device['name']})")
                    exec(device, 'clear_attendance')

                else:
                    logger.error(f"Failed to insert records into the database for device: {device['name']}")
                    logger.error(f"Possible reason: {re}")
                    logger.error(f"Please solve the issue and try again.")

        except ConnectionError as ce:
            logger.error(f"Connection error while processing device {device['name']}: {ce}")

        except Exception as e:
            logger.error(f"Error while processing device {device['name']}: {e}")

    exec(device, 'enable_device')
    db.close_connection()
    logger.success("All devices processed. Main script will run next.", "SUCCESS")
