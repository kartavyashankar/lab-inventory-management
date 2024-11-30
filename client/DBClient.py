from pymongo import MongoClient, ReadPreference


class DBClient:
    def __init__(self):
        url = "mongodb+srv://pyapp:rYdD5sXNpxMfKgNq@jvmlabs.dv3r9.mongodb.net/?retryWrites=true&w=majority&appName=jvmlabs"
        mongo_client = MongoClient(url)
        self.db_name = "jvm-labs"
        self.db_client = mongo_client[self.db_name]

    def labs_client(self):
        return self.db_client["labs"]

    def apparatus_client(self):
        return self.db_client["apparatus"]

    def user_client(self):
        return self.db_client["users"]
