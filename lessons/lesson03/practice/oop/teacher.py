from lessons.lesson03.practice.oop.person import Person


class Teacher(Person):
    def __init__(self, name: str, age: str, income: float, subject: str, years: float, **kwargs):
        super().__init__(name, age, income, **kwargs)
        self._subject = subject
        self._years = years

    @property
    def subject(self):
        return self._subject

    @property
    def years(self):
        return self._years
    @years.setter
    def years(self, value: float):
        if value < 0:
            raise ValueError(">>>>> Years must be non-negative")
        self._years = value


    def __str__(self):
        return f"{self.name} - GV môn {self.subject}, {self.years} năm KN"

    def __repr__(self):
        return (f"Teacher(name={self.name!r}, age={self.age}, income={self.income}, "
                f"subject={self.subject!r}, years={self.years})")

