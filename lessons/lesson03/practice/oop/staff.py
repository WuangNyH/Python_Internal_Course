class Staff:
    def __init__(self, name: str, age: int, **kwargs):
        self.name = name
        self.age = age
        self.extra = kwargs

