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
            logger.error(f"Could not connect to MongoDB: {e}")
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
                logger.success("Database connection closed successfully.")
            except pymongo.errors.PyMongoError as e:
                logger.error(f"Error closing database connection: {e}")
        else:
            logger.warning("No active database connection to close.")

    def collect_latest_records(self):
        """
        Collect the latest attendance records from the database.
        
        :return: A list of the latest attendance records.
        """
        if self.client is None:
            logger.error("Database connection failed. Cannot collect records.")
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
            logger.error(f"Error fetching records: {e}")
            return []
        
    def collect_filtered_records(self, filters=None):
        """
        Collect attendance records from the database based on provided filters.
        
        :param filters: A dictionary of filters to apply to the query.
        :return: A list of attendance records matching the filters.
        """
        if self.client is None:
            logger.error("Database connection failed. Cannot collect records.")
            return []

        db = self.get_db('records')
        if not filters:
            raise ValueError("Filters must be provided to collect filtered records.")

        try:
            g = list(db.find(filters, {"_id": 0}))
            return g

        except pymongo.errors.PyMongoError as e:
            logger.error(f"Error fetching filtered records: {e}")
            return []

db = DB()
