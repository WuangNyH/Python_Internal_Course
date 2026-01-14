from datetime import datetime


class Task:
    def __init__(self, description: str, due_date: datetime, status: str = "todo"):
        self.description = description
        self.due_date = due_date
        self.status = status

    def is_overdue(self, now: datetime) -> bool:
        return self.status != "done" and self.due_date.date() < now.date()

    def __str__(self) -> str:
        status_label = "DONE" if self.status == "done" else "TODO"
        due_str = self.due_date.strftime("%Y-%m-%d")
        return f"[{status_label}] {self.description} (Hạn: {due_str})"

    def __repr__(self) -> str:
        return (
            f"Task(description={self.description!r}, "
            f"due_date={self.due_date.strftime('%Y-%m-%d')!r}, "
            f"status={self.status!r})"
        )

    def to_line(self) -> str:
        due_str = self.due_date.strftime("%Y-%m-%d")
        return f"{self.description};{due_str};{self.status}"
