from pandas import DataFrame

from client.DBClient import DBClient
from exceptions.Exceptions import ForbiddenOperationException
from model.Apparatus import Apparatus
from model.Lab import Lab
from model.User import User
from repository.ApparatusRepository import ApparatusRepository
from service.LabService import LabService
from utils import get_user_permission_for_lab, convert_to_dataframe, write_to_csv


class ApparatusService:
    def __init__(self, db_client: DBClient):
        self.apparatus_repository = ApparatusRepository(db_client)
        self.lab_service = LabService(db_client)

    def list_all_apparatus(self, current_user: User, lab_id: int):
        if get_user_permission_for_lab(current_user, lab_id)["apparatus"] == "none":
            raise ForbiddenOperationException
        apparatus_list: list[Apparatus] = self.apparatus_repository.list_apparatus_for_lab(lab_id)

        apparatus_list_dict: dict = {"Name": [], "Year of purchase": [], "Working condition": [], "Apparatus Id": []}

        for apparatus in apparatus_list:
            apparatus_list_dict["Name"].append(apparatus.name)
            apparatus_list_dict["Year of purchase"].append(apparatus.year_of_purchase)
            apparatus_list_dict["Working condition"].append(apparatus.working_condition)
            apparatus_list_dict["Apparatus Id"].append(apparatus.tiny_id)

        return convert_to_dataframe(apparatus_list_dict)

    def export_all_apparatus_data(self, current_user: User, lab_id: int):
        apparatus_list_df: DataFrame = self.list_all_apparatus(current_user, lab_id)
        lab: Lab = self.lab_service.get_lab_by_id(current_user, lab_id)
        filename: str = lab.name + "-apparatus-data.csv"
        write_to_csv(data=apparatus_list_df, filename=filename)
        return filename

    def update_apparatus(self, current_user: User, apparatus: Apparatus):
        user_access = get_user_permission_for_lab(current_user, apparatus.lab_id)
        if user_access["apparatus"] != "write":
            raise ForbiddenOperationException

        return self.apparatus_repository.update_apparatus(apparatus)

    def add_apparatus(self, current_user: User, apparatus: Apparatus):
        user_access = get_user_permission_for_lab(current_user, apparatus.lab_id)
        if user_access["apparatus"] != "write":
            raise ForbiddenOperationException

        return self.apparatus_repository.update_apparatus(apparatus)

    def remove_apparatus(self, current_user: User, lab_id: int, apparatus_id: int):
        user_access = get_user_permission_for_lab(current_user, lab_id)
        if user_access["apparatus"] != "write":
            raise ForbiddenOperationException

        self.apparatus_repository.remove_apparatus(lab_id, apparatus_id)

    def get_apparatus(self, current_user: User, lab_id: int, apparatus_id: int):
        user_access = get_user_permission_for_lab(current_user, lab_id)
        if user_access["apparatus"] == "none":
            raise ForbiddenOperationException

        self.apparatus_repository.get_apparatus_by_id(lab_id, apparatus_id)