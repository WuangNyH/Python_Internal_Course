class Student:
    def __init__(self, name: str, age: int, score: float):
        self.name = name
        self.age = age
        self.score = score

    def is_passed(self) -> bool:
        return self.score >= 5.0

    def __str__(self) -> str:
        return f"{self.name} ({self.age} tuổi) – Điểm: {self.score}"

    def __repr__(self) -> str:
        return f"Student(name={self.name!r}, age={self.age}, score={self.score})"