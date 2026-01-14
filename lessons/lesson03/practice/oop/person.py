class Person:
    def __init__(self, name, age, income, **kwargs):
        self._name = name
        self._age = age
        self._income = income

    @property
    def name(self):
        return self._name

    @property
    def age(self):
        return self._age

    @age.setter
    def age(self, value):
        if value < 0:
            raise ValueError(">>>>> Age must be non-negative")
        self._age = value

    @property
    def income(self):
        return self._income

    def __str__(self):
        return f"{self.name} ({self.age} tuổi) - Thu nhập: {self.income} usd/tháng"

    def __repr__(self):
        return f"Person(name={self.name!r}, age={self.age}, income={self.income})"