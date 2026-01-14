from datetime import datetime
from typing import List

from models import Task
from task_service import load_tasks, save_tasks, get_overdue_tasks

FILENAME = "tasks.txt"


def print_all_tasks(tasks: List[Task]) -> None:
    if not tasks:
        print("Chưa có task nào")
        return

    print("\nDanh sách task:")
    for idx, task in enumerate(tasks, start=1):
        print(f"{idx}. {task}")


def print_overdue_tasks(tasks: List[Task]) -> None:
    overdue = get_overdue_tasks(tasks)

    if not overdue:
        print("Không có task quá hạn")
        return

    print("\nCác task quá hạn:")
    for t in overdue:
        print(" -", t)


def add_task(tasks: List[Task]) -> None:
    desc = input("Nhập mô tả task: ").strip()
    if not desc:
        print("Mô tả không được để trống")
        return

    due_str = input("Nhập hạn (YYYY-MM-DD): ").strip()

    try:
        due_date = datetime.strptime(due_str, "%Y-%m-%d")
    except ValueError:
        print("Ngày không hợp lệ, không thêm task")
        return

    tasks.append(Task(desc, due_date, "todo"))
    print("Đã thêm task mới")


def mark_task_done(tasks: List[Task]) -> None:
    if not tasks:
        print("Không có task nào để đánh dấu")
        return

    print_all_tasks(tasks)

    choice = input("Nhập số task muốn đánh dấu DONE: ").strip()
    try:
        idx = int(choice)
    except ValueError:
        print("Bạn phải nhập số")
        return

    if idx < 1 or idx > len(tasks):
        print("Số không hợp lệ")
        return

    tasks[idx - 1].status = "done"
    print("✅ Đã đánh dấu DONE:", tasks[idx - 1].description)


def show_menu():
    print("\n===== QUẢN LÝ TO-DO LIST =====")
    print("1. Xem tất cả task")
    print("2. Xem task quá hạn")
    print("3. Thêm task mới")
    print("4. Đánh dấu task DONE")
    print("5. Thoát")
    print("===============================")


def main():
    tasks = load_tasks(FILENAME)

    while True:
        show_menu()
        choice = input("Chọn chức năng (1–5): ").strip()

        if choice == "1":
            print_all_tasks(tasks)
        elif choice == "2":
            print_overdue_tasks(tasks)
        elif choice == "3":
            add_task(tasks)
            save_tasks(FILENAME, tasks)
        elif choice == "4":
            mark_task_done(tasks)
            save_tasks(FILENAME, tasks)
        elif choice == "5":
            print("Tạm biệt!")
            break
        else:
            print("Lựa chọn không hợp lệ, vui lòng chọn 1–5")


if __name__ == "__main__":
    main()
