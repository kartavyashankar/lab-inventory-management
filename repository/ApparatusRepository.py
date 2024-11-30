from dependency_injector.wiring import Provide, inject

from client.ClientContainer import ClientContainer
from client.DBClient import DBClient
from exceptions.Exceptions import NotFoundException
from model.Apparatus import Apparatus


def parse_apparatus_data(apparatus_as_dict: dict):
    if apparatus_as_dict is None:
        raise NotFoundException
    apparatus = Apparatus()
    apparatus.tiny_id = apparatus_as_dict["tiny_id"]
    apparatus.year_of_purchase = apparatus_as_dict["year_of_purchase"]
    apparatus.working_condition = apparatus_as_dict["working_condition"]
    apparatus.lab_id = apparatus_as_dict["lab_id"]
    apparatus.name = apparatus_as_dict["name"]
    return apparatus


class ApparatusRepository:
    @inject
    def __init__(self, db_client: DBClient = Provide[ClientContainer.db_client]):
        self.client = db_client.apparatus_client()

    def list_apparatus_for_lab(self, lab_id: int):
        apparatus_list = []
        for apparatus_dict in self.client.find({"lab_id": lab_id}).to_list():
            apparatus_list.append(parse_apparatus_data(apparatus_dict))
        return apparatus_list

    def get_apparatus_by_id(self, lab_id: int, apparatus_id: int):
        return parse_apparatus_data(self.client.find_one({"lab_id": lab_id, "tiny_id": apparatus_id}))

    def add_apparatus(self, apparatus: Apparatus):
        apparatus_list = self.client.find({"lab_id": apparatus.lab_id}).to_list()
        apparatus.tiny_id = len(apparatus_list) + 1
        self.client.insert_one(apparatus.to_dict())
        return apparatus

    def update_apparatus(self, apparatus: Apparatus):
        query_filter = {"tiny_id": apparatus.tiny_id}
        new_apparatus = apparatus.to_dict()
        self.client.replace_one(query_filter, new_apparatus)
        return apparatus

    def remove_apparatus(self, lab_id: int, apparatus_id: int):
        self.client.delete_one({"lab_id": lab_id, "tiny_id": apparatus_id})

    def remove_all_apparatus_for_lab(self, lab_id: int):
        self.client.delete_many({"lab_id": lab_id})
