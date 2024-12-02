import json

from pandas import DataFrame

from client.DBClient import DBClient
from exceptions.Exceptions import UnauthorizedUserException, NotFoundException, UsernameUnavailableException, \
    ForbiddenOperationException
from model.Lab import Lab
from model.User import User
from repository.UserRepository import UserRepository
from service.LabService import LabService
from utils import get_user_permission_for_lab, hash_string, write_to_csv, convert_to_dataframe


class UserService:
    def __init__(self, db_client: DBClient):
        self.user_repository = UserRepository(db_client)
        self.lab_service = LabService(db_client)

    def login(self, username: str, password: str):
        try:
            user: User = self.user_repository.get_user_by_username(username)
            hashed_password = hash_string(password)
            if user.hashed_password != hashed_password:
                raise UnauthorizedUserException
            return user

        except NotFoundException:
            raise UnauthorizedUserException

    def add_user(self, user: User, password: str):
        try:
            self.user_repository.get_user_by_username(user.username)
            username_unavailable = True
        except NotFoundException:
            username_unavailable = False

        if username_unavailable:
            raise UsernameUnavailableException

        user.hashed_password = hash_string(password)
        return self.user_repository.add_user(user)

    def get_user_by_username(self, username: str):
        return self.user_repository.get_user_by_username(username)

    def remove_user(self, current_user: User, username: str):
        if not current_user.org_admin:
            raise ForbiddenOperationException
        user: User = self.user_repository.get_user_by_username(username)
        self.user_repository.remove_user(user.tiny_id)

    def update_user(self, current_user: User, user: User, password: str):
        if user.tiny_id != current_user.tiny_id:
            raise ForbiddenOperationException

        user.hashed_password = hash_string(password)
        return self.user_repository.update_user(user)

    def update_user_lab_access(self, current_user: User, lab_id: int, username: str, access_dict: dict):
        if get_user_permission_for_lab(current_user, lab_id)["user"] != "write":
            raise ForbiddenOperationException

        user: User = self.user_repository.get_user_by_username(username)
        user.access[str(lab_id)] = access_dict
        self.user_repository.update_user(user)

    def list_all_user_data(self, current_user: User):
        if not current_user.org_admin:
            raise ForbiddenOperationException
        user_list: list[User] = self.user_repository.list_users()

        return self.convert_to_df(
            current_user=current_user,
            user_list=user_list
        )

    def export_all_user_data(self, current_user: User):
        user_list_df: DataFrame = self.list_all_user_data(current_user)
        filename: str = "user-data.csv"
        write_to_csv(data=user_list_df, filename=filename)
        return filename

    def list_user_data_for_lab(self, current_user: User, lab_id: int):
        if get_user_permission_for_lab(current_user, lab_id)["user"] == "none":
            raise ForbiddenOperationException
        user_list: list[User] = self.user_repository.list_users()
        filtered_users: list[User] = []
        for user in user_list:
            user_access = get_user_permission_for_lab(user, lab_id)
            if user_access["user"] != "none" or user_access["apparatus"] != "none":
                filtered_users.append(user)

        return self.convert_to_df(
            current_user=current_user,
            user_list=filtered_users,
            lab_id=lab_id
        )

    def export_user_data_for_lab(self, current_user: User, lab_id: int):
        user_list_df: DataFrame = self.list_user_data_for_lab(current_user, lab_id)
        lab: Lab = self.lab_service.get_lab_by_id(current_user, lab_id)
        filename: str = lab.name + "-user-data.csv"
        write_to_csv(data=user_list_df, filename=filename)
        return filename

    def convert_to_df(self, current_user: User, user_list: list[User], lab_id: int = 0):
        elevated_data = False
        if get_user_permission_for_lab(current_user, lab_id)["user"] == "write":
            elevated_data = True

        if current_user.org_admin:
            elevated_data = True

        user_list_dict: dict = {"Full Name": [], "Access": [], "Mobile Number": []}
        if elevated_data:
            user_list_dict["User Id"] = []
            user_list_dict["Username"] = []

        for user in user_list:
            user_list_dict["Full Name"].append(user.full_name)
            if current_user.org_admin:
                user_list_dict["Access"].append(self.generate_access_string(current_user, user))
            else:
                user_list_dict["Access"].append(user.access[lab_id])

            user_list_dict["Mobile Number"].append(user.mobile_number)
            if elevated_data:
                user_list_dict["User Id"].append(user.tiny_id)
                user_list_dict["Username"].append(user.username)

        return convert_to_dataframe(user_list_dict)

    def generate_access_string(self, current_user, user: User):
        parsed_access: dict = {}
        if user.org_admin:
            labs = self.lab_service.get_all_labs(current_user)
            for lab in labs:
                parsed_access[lab.name] = get_user_permission_for_lab(user, lab.tiny_id)
        else:
            for lab_id in user.access.keys():
                try:
                    lab: Lab = self.lab_service.get_lab_by_id(current_user, int(lab_id))
                    parsed_access[lab.name] = user.access[lab_id]
                except NotFoundException:
                    continue
        return json.dumps(parsed_access)
