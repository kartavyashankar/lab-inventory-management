from client.DBClient import DBClient
from exceptions.Exceptions import NotFoundException
from model.Lab import Lab


def parse_lab_data(lab_as_dict: dict):
    if lab_as_dict is None:
        raise NotFoundException
    lab = Lab()
    lab.tiny_id = lab_as_dict["tiny_id"]
    lab.name = lab_as_dict["name"]
    return lab


class LabRepository:
    def __init__(self, db_client: DBClient):
        self.client = db_client.labs_client()

    def list_labs(self):
        lab_list = []
        for lab_dict in self.client.find({}).to_list():
            lab_list.append(parse_lab_data(lab_dict))
        return lab_list

    def get_lab_by_id(self, lab_id: int):
        return parse_lab_data(self.client.find_one({"tiny_id": lab_id}))

    def add_lab(self, lab: Lab):
        lab_list = self.client.find({}).to_list()
        lab.tiny_id = len(lab_list) + 1
        self.client.insert_one(lab.to_dict())
        return lab

    def update_lab(self, lab: Lab):
        query_filter = {"tiny_id": lab.tiny_id}
        new_lab = lab.to_dict()
        self.client.replace_one(query_filter, new_lab)
        return lab

    def remove_lab(self, lab_id: int):
        self.client.delete_one({"tiny_id": lab_id})
