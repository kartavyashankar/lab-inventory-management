import hashlib
import os

from pandas import DataFrame

from model.User import User


def get_user_permission_for_lab(user: User, lab_id: int):
    if lab_id <= 0:
        return {"user": "none", "apparatus": "none"}
    if user.org_admin:
        return {"user": "write", "apparatus": "write"}
    if str(lab_id) not in user.access.keys():
        return {"user": "none", "apparatus": "none"}
    return user.access[str(lab_id)]


def hash_string(string: str):
    return hashlib.sha256(string.encode()).hexdigest()


def convert_to_dataframe(data: dict):
    return DataFrame.from_dict(data)


def write_to_csv(data: DataFrame, filename: str):
    data.to_csv(filename, index=False)


def clear_screen():
    if os.name == "nt":
        os.system("cls")
    else:
        os.system("clear")
