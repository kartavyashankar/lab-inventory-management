class Lab:
    def __init__(self):
        self.name: str = ''
        self.tiny_id: int = 0

    def to_dict(self):
        return {
            "name": self.name,
            "tiny_id": self.tiny_id
        }
