from client.DBClient import DBClient
from exceptions.Exceptions import ForbiddenOperationException
from model.Lab import Lab
from model.User import User
from repository.ApparatusRepository import ApparatusRepository
from repository.LabRepository import LabRepository
from utils import get_user_permission_for_lab, write_to_csv, convert_to_dataframe


class LabService:
    def __init__(self, db_client: DBClient):
        self.lab_repository = LabRepository(db_client)
        self.apparatus_repository = ApparatusRepository(db_client)

    def get_all_labs(self, current_user: User):
        if not current_user.org_admin:
            raise ForbiddenOperationException
        return self.lab_repository.list_labs()

    def get_lab_by_id(self, current_user: User, lab_id: int):
        user_access = get_user_permission_for_lab(current_user, lab_id)
        if user_access["user"] == "none" and user_access["apparatus"] == "none":
            raise ForbiddenOperationException
        return self.lab_repository.get_lab_by_id(lab_id)

    def add_lab(self, current_user: User, lab: Lab):
        if not current_user.org_admin:
            raise ForbiddenOperationException
        return self.lab_repository.add_lab(lab)

    def remove_lab(self, current_user: User, lab_id: int):
        if not current_user.org_admin:
            raise ForbiddenOperationException
        self.lab_repository.remove_lab(lab_id)
        self.apparatus_repository.remove_all_apparatus_for_lab(lab_id)

    def update_lab(self, current_user: User, lab: Lab):
        if get_user_permission_for_lab(current_user, lab.tiny_id)["user"] != "write":
            raise ForbiddenOperationException
        return self.lab_repository.update_lab(lab)

    def list_all_lab_data(self, current_user: User):
        if not current_user.org_admin:
            raise ForbiddenOperationException

        lab_list: list[Lab] = self.lab_repository.list_labs()
        lab_list_dict = {"Lab Id": [], "Lab Name": []}

        for lab in lab_list:
            lab_list_dict["Lab Id"].append(lab.tiny_id)
            lab_list_dict["Lab Name"].append(lab.name)

        return convert_to_dataframe(lab_list_dict)

    def export_all_lab_data(self, current_user: User):
        lab_list_df = self.list_all_lab_data(current_user)
        filename="lab-data.csv"
        write_to_csv(data=lab_list_df, filename=filename)
        return filename
