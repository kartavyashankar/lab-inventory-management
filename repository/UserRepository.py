import json

from dependency_injector.wiring import Provide, inject

from client.ClientContainer import ClientContainer
from client.DBClient import DBClient
from exceptions.Exceptions import NotFoundException
from model.User import User


def parse_user_data(user_as_dict: dict):
    if user_as_dict is None:
        raise NotFoundException
    user = User()
    user.tiny_id = user_as_dict["tiny_id"]
    user.full_name = user_as_dict["full_name"]
    user.username = user_as_dict["username"]
    user.mobile_number = user_as_dict["mobile_number"]
    user.access = json.loads(user_as_dict["access"])
    user.hashed_password = user_as_dict["hashed_password"]
    user.unique_school_code = user_as_dict["unique_school_code"]
    user.org_admin = user_as_dict["org_admin"]
    return user


class UserRepository:
    @inject
    def __init__(self, db_client: DBClient = Provide[ClientContainer.db_client]):
        self.client = db_client.user_client()

    def list_users(self):
        user_list = []
        for user_dict in self.client.find({}).to_list():
            user_list.append(parse_user_data(user_dict))
        return user_list

    def get_user_by_id(self, user_id: int):
        return parse_user_data(self.client.find_one({"tiny_id": user_id}))

    def get_user_by_username(self, username: str):
        return parse_user_data(self.client.find_one({"username": username}))

    def add_user(self, user: User):
        user_list = self.client.find({}).to_list()
        user.tiny_id = len(user_list) + 1
        self.client.insert_one(user.to_dict())
        return user

    def update_user(self, user: User):
        query_filter = {"tiny_id": user.tiny_id}
        new_user = user.to_dict()
        self.client.replace_one(query_filter, new_user)
        return user

    def remove_user(self, user_id: int):
        self.client.delete_one({"tiny_id": user_id})
