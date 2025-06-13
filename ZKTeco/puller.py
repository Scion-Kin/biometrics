#!/usr/bin/env python3

from exec import exec
from bio_config import devices
from db import db
from logger import logger

if __name__ == "__main__":
    for device in devices:
        logger.log(f"Starting attendance puller for device: {device.get('name')}", 'INFO')
        try:
            client = db.get_db('records')
            if client is None:
                logger.log(f"Database connection failed. Skiping device {device.get('name')}.", 'ERROR')
                continue

            exec(device, 'disable_device')
            records = exec(device, 'get_attendance')
            if not records or len(records) < 1:
                logger.log(f"No attendance records found for device: {device['name']}", 'WARNING')
                continue

            elif isinstance(records, list):
                records = [
                    {"attendance_device_id": record.user_id, "timestamp": record.timestamp, "status": record.status, "punch": record.punch, "device": device.get('ip')}
                    for record in records
                ]
                re = client.insert_many(records)
                if re.acknowledged:
                    logger.log(f"Inserted {len(re.inserted_ids)} records into the database from: ({device['name']})", 'SUCCESS')
                    exec(device, 'clear_attendance')

                else:
                    logger.log(f"Failed to insert records into the database for device: {device['name']}", 'ERROR')
                    logger.log(f"Possible reason: {re}", 'ERROR')
                    logger.log(f"Please solve the issue and try again.", 'ERROR')

        except ConnectionError as ce:
            logger.log(f"Connection error while processing device {device['name']}: {ce}", 'ERROR')

        except Exception as e:
            logger.log(f"Error while processing device {device['name']}: {e}", 'ERROR')

    exec(device, 'enable_device')
    db.close_connection()
    logger.log("All devices processed. Main script will run next.", "SUCCESS")
    logger.close()
