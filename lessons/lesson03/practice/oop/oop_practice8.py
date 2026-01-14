# ===== BTTH8 =====
class Employee:
    def __init__(self, name: str, salary: float, bonus_rate: float = 0.1):
        self._name = name
        self._salary = 0.0 # tạm gán, set qua property
        self._bonus_rate = 0.1
        self.salary = salary # dùng setter để validate
        self.bonus_rate = bonus_rate

    @property
    def name(self) -> str:
        return self._name

    @property
    def salary(self) -> float:
        return self._salary

    @salary.setter
    def salary(self, value: float) -> None:
        if value < 0:
            raise ValueError("Salary must be non-negative")
        self._salary = value

    @property
    def bonus_rate(self) -> float:
        return self._bonus_rate

    @bonus_rate.setter
    def bonus_rate(self, value: float) -> None:
        if not (0 <= value <= 1):
            raise ValueError("Bonus rate must be between 0 and 1")
        self._bonus_rate = value

    def total_income(self) -> float:
        """Tổng thu nhập = lương + tiền thưởng."""
        return self.salary + self.salary * self.bonus_rate

    def __repr__(self) -> str:
        return f"Employee(name={self.name!r}, salary={self.salary}, bonus_rate={self.bonus_rate})"

