import json


class User:
    def __init__(self):
        self.username: str = ''
        self.tiny_id: int = 0
        self.hashed_password: str = ''
        self.mobile_number: str = ''
        self.unique_school_code: str = ''
        self.full_name: str = ''
        self.org_admin: bool = False
        self.access: dict = {}
        '''
        An example for access
    
        self.access = {
            "0": {  # Here 0 is Lab Id in str
                "user": "none",  # Allowed values: none, read, write -> depicts user's access for other lab users data
                "apparatus": "none"  # Allowed values: none, read, write -> depicts user's access for lab apparatus data
            }
        }
        '''

    def to_dict(self):
        return {
            "full_name": self.full_name,
            "tiny_id": self.tiny_id,
            "hashed_password": self.hashed_password,
            "mobile_number": self.mobile_number,
            "unique_school_code": self.unique_school_code,
            "access": json.dumps(self.access),
            "username": self.username,
            "org_admin": self.org_admin
        }

    def to_displayable_dict(self):
        return {
            "Username": self.username,
            "Full Name": self.full_name,
            "Unique School Code": self.unique_school_code,
            "Mobile number": self.mobile_number
        }
