import datetime

from pymongo import MongoClient
from pymongo.errors import PyMongoError

from bot.config import DATABASE_URL, SUDO_USERS
from bot.logging import LOGGER


class DatabaseHelper:
    def __init__(self):
        self.__err = False
        self.__client = None
        self.__db = None
        self.__col = None
        self.__col2 = None
        self.__col3 = None
        self.__connect()

    def __connect(self):
        try:
            self.__client = MongoClient(DATABASE_URL)
            self.__db = self.__client["MFBot"]
            self.__col = self.__db["users"]
            self.__col2 = self.__db["sudo_users"]
            self.__col3 = self.__db["urls"]
            self.__err = False
        except PyMongoError as err:
            LOGGER(__name__).error(f"Error in DB connection: {err}")
            self.__err = True

    async def auth_user(self, user_id: int):
        if self.__err:
            return
        self.__col2.insert_one({"sudo_user_id": user_id})
        self.__client.close()
        LOGGER(__name__).info(f"Added {user_id} to Sudo Users List!")
        return f"<b><i>Successfully added {user_id} to Sudo Users List!</i></b>"

    async def unauth_user(self, user_id: int):
        if self.__err:
            return
        self.__col2.delete_many({"sudo_user_id": user_id})
        self.__client.close()
        LOGGER(__name__).info(f"Removed {user_id} from Sudo Users List!")
        return f"<b><i>Successfully removed {user_id} from Sudo Users List!</i></b>"

    def new_user(self, user_id):
        return dict(
            id=user_id,
            join_date=datetime.date.today().isoformat(),
            last_used_on=datetime.date.today().isoformat(),
        )

    async def get_user(self, user_id: int):
        if self.__err:
            return
        user = self.__col.find_one({"id": user_id})
        if user is not None:
            return user
        await self.add_user(user_id)
        self.__client.close()
        return user

    async def add_user(self, user_id: int):
        if self.__err:
            return
        user = self.new_user(user_id)
        self.__col.update_one(
            {"id": user["id"]},
            {
                "$set": {
                    "join_date": user["join_date"],
                    "last_used_on": user["last_used_on"],
                }
            },
            upsert=True,
        )
        self.__client.close()

    async def is_user_exist(self, user_id: int):
        if self.__err:
            return
        user = await self.get_user(user_id)
        return True if user else False

    async def total_users_count(self):
        if self.__err:
            return
        count = self.__col.count_documents({})
        self.__client.close()
        return count

    async def get_all_users(self):
        if self.__err:
            return
        all_users = self.__col.find({"id"})
        self.__client.close()
        return all_users

    async def delete_user(self, user_id: int):
        if self.__err:
            return
        if self.__col.find_one({"id": int(user_id)}):
            self.__col.delete_many({"id": user_id})
        self.__client.close()

    async def update_last_used_on(self, user_id: int):
        if self.__err:
            return
        self.__col.update_one(
            {"id": user_id},
            {"$set": {"last_used_on": datetime.date.today().isoformat()}},
            upsert=True,
        )
        self.__client.close()

    async def get_last_used_on(self, user_id: int):
        if self.__err:
            return
        user = await self.get_user(user_id)
        return user.get("last_used_on", datetime.date.today().isoformat())

    async def get_bot_started_on(self, user_id: int):
        if self.__err:
            return
        user = await self.get_user(user_id)
        return user.get("join_date", datetime.date.today().isoformat())

    def load_sudo_users(self):
        if self.__err:
            return
        sudo_users = self.__col2.find().sort("sudo_user_id")
        for sudo_user in sudo_users:
            SUDO_USERS.add(sudo_user["sudo_user_id"])
        LOGGER(__name__).info(f"Successfully Loaded Sudo Users from DB!")
        self.__client.close()

    def new_dblink(self, url, result):
        return dict(
            usr_url=url,
            result_url=result,
            url_added_on=datetime.date.today().isoformat(),
            last_fetched_on=datetime.date.today().isoformat(),
        )

    async def check_dblink(self, url):
        if self.__err:
            return
        usr_url = self.__col3.find_one({"usr_url": url})
        if usr_url is not None:
            return usr_url
        self.__client.close()

    async def add_new_dblink(self, url, result):
        if self.__err:
            return
        dblink = self.new_dblink(url, result)
        self.__col3.update_one(
            {"usr_url": dblink["usr_url"]},
            {
                "$set": {
                    "result_url": dblink["result_url"],
                    "url_added_on": dblink["url_added_on"],
                    "last_fetched_on": dblink["last_fetched_on"],
                }
            },
            upsert=True,
        )
        self.__client.close()

    async def is_dblink_exist(self, url):
        if self.__err:
            return
        user = await self.check_dblink(url)
        return True if user else False

    async def fetch_dblink_result(self, url):
        if self.__err:
            return
        dblink = await self.check_dblink(url)
        return dblink.get("result_url")

    async def fetch_dblink_added(self, url):
        if self.__err:
            return
        dblink = await self.check_dblink(url)
        return dblink.get("url_added_on")

    async def update_last_fetched_on(self, url):
        if self.__err:
            return
        self.__col3.update_one(
            {"usr_url": url},
            {"$set": {"last_fetched_on": datetime.date.today().isoformat()}},
            upsert=True,
        )
        self.__client.close()

    async def get_url_added_on(self, url):
        if self.__err:
            return
        dblink = await self.check_dblink(url)
        return dblink.get("url_added_on")

    async def get_last_fetched_on(self, url):
        if self.__err:
            return
        dblink = await self.check_dblink(url)
        return dblink.get("last_fetched_on")

    async def total_dblinks_count(self):
        if self.__err:
            return
        count = self.__col3.count_documents({})
        self.__client.close()
        return count

    def check_db_connection(self):
        if self.__err:
            return None
        if not self.__err:
            LOGGER(__name__).info("Successfully Connected to DB!")
        self.__client.close()
        return ""


if DATABASE_URL is not None:
    DatabaseHelper().check_db_connection()
    DatabaseHelper().load_sudo_users()
