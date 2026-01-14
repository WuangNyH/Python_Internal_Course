from typing import List
from datetime import datetime

from models import Task


def load_tasks(filename: str) -> List[Task]:
    tasks: List[Task] = []

    try:
        with open(filename, "r", encoding="utf-8") as f:
            for line_no, line in enumerate(f, start=1):
                raw = line.strip()
                if not raw:
                    continue

                parts = [p.strip() for p in raw.split(";")]
                if len(parts) != 3:
                    print(f"Dòng {line_no} sai format, bỏ qua: {raw}")
                    continue

                desc, due_str, status = parts
                status = status.lower()

                if status not in ("todo", "done"):
                    print(f"Status không hợp lệ ở dòng {line_no}, mặc định = todo")
                    status = "todo"

                try:
                    due_date = datetime.strptime(due_str, "%Y-%m-%d")
                except ValueError:
                    print(f">>>>> Ngày không hợp lệ ở dòng {line_no}: {due_str}")
                    continue

                tasks.append(Task(desc, due_date, status))

    except FileNotFoundError:
        print(f"File '{filename}' chưa tồn tại. Khởi tạo danh sách trống")
        return []
    except OSError as e:
        print(f"Lỗi khi đọc file '{filename}': {e}")
        return []

    return tasks


def save_tasks(filename: str, tasks: List[Task]) -> None:
    try:
        with open(filename, "w", encoding="utf-8") as f:
            for task in tasks:
                f.write(task.to_line() + "\n")
    except OSError as e:
        print(f"Lỗi khi ghi file '{filename}': {e}")


def get_overdue_tasks(tasks: List[Task], now: datetime | None = None) -> List[Task]:
    if now is None:
        now = datetime.now()
    return [t for t in tasks if t.is_overdue(now)]
