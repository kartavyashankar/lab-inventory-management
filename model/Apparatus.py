class Apparatus:
    def __init__(self):
        self.name: str = ''
        self.year_of_purchase: int = 0
        self.working_condition: str = ''
        self.tiny_id: int = 0
        self.lab_id: int = 0

    def to_dict(self):
        return {
            "name": self.name,
            "year_of_purchase": self.year_of_purchase,
            "working_condition": self.working_condition,
            "tiny_id": self.tiny_id,
            "lab_id": self.lab_id
        }
