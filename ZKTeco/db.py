import pymongo
from logger import logger

class DB:
    """
    A class to handle MongoDB database connections and operations.
    """
    def __init__(self):
        """
        Initialize the DB class.
        """
        self.client = None

    def connect(self):
        """
        Connect to the MongoDB database.
        Returns a MongoClient instance.
        """
        if self.client:
            return self.client

        try:
            client = pymongo.MongoClient("mongodb://localhost:27017/")
            return client
        except pymongo.errors.ConnectionError as e:
            logger.log(f"Could not connect to MongoDB: {e}", 'ERROR')
            return None

    def get_db(self, collection_name):
        """
        Get a specific collection from the MongoDB database.

        :param collection_name: The name of the collection to retrieve.
        :return: The specified collection from the database.
        """

        if self.client:
            db = self.client.attendance
            return db[collection_name]
        else:
            self.client = self.connect()
            return self.client.attendance[collection_name] if self.client else None

    def close_connection(self):
        """
        Close the connection to the MongoDB database.
        
        :return: None
        """
        if self.client is not None:
            try:
                self.client.close()
                logger.log("Database connection closed successfully.", 'SUCCESS')
            except pymongo.errors.PyMongoError as e:
                logger.log(f"Error closing database connection: {e}", 'ERROR')
        else:
            logger.log("No active database connection to close.", 'WARNING')

    def collect_latest_records(self):
        """
        Collect the latest attendance records from the database.
        
        :return: A list of the latest attendance records.
        """
        if self.client is None:
            logger.log("Database connection failed. Cannot collect records.", 'ERROR')
            return []

        db = self.get_db('records')
        try:
            pipeline = [
                { "$sort": { "attendance_device_id": 1, "timestamp": -1 } },
                {
                    "$group": {
                        "_id": "$attendance_device_id",
                        "latestRecord": { "$first": "$$ROOT" }
                    }
                },
                { "$replaceRoot": { "newRoot": "$latestRecord" } }
            ]
            latest_records = list(db.aggregate(pipeline))
            return latest_records

        except pymongo.errors.PyMongoError as e:
            logger.log(f"Error fetching records: {e}", 'ERROR')
            return []

db = DB()
