# ===== BTTH9 =====
from lessons.lesson03.practice.oop.person import Person


class Community:
    def __init__(self, *people: Person):
        self.people: list[Person] = list(people)

    def add_person(self, person: Person) -> None:
        self.people.append(person)

    def find(self, **conditions) -> list[Person]:
        result: list[Person] = []

        for person in self.people:
            match = True
            for key, value in conditions.items():
                attr_value = getattr(person, key, object())
                if attr_value != value:
                    match = False
                    break
            if match:
                result.append(person)

        return result

    def __str__(self) -> str:
        if not self.people:
            return "Cộng đồng hiện chưa có ai"

        lines = [f"Cộng đồng có {len(self.people)} người:"]
        for p in self.people:
            lines.append(f"- {p}")
        return "\n".join(lines)
