from typing import List

from lessons.lesson03.exercises.exe2.student import Student


def load_students_from_file(filename: str) -> List[Student]:
    students: List[Student] = []

    try:
        with open(filename, "r", encoding="utf-8") as f:
            for line_no, line in enumerate(f, start=1):
                raw = line.strip()
                if not raw:
                    continue

                parts = [p.strip() for p in raw.split(",")]

                if len(parts) != 3:
                    if line_no == 1:
                        continue
                    print(f"Dòng {line_no}: sai định dạng, bỏ qua. Nội dung: {raw}")
                    continue

                name, age_str, score_str = parts

                if line_no == 1 and age_str.lower() == "tuổi":
                    continue

                try:
                    age = int(age_str)
                    score = float(score_str)
                except ValueError:
                    print(
                        f"Dòng {line_no}: không parse được age/score, bỏ qua"
                        f"(age='{age_str}', score='{score_str}')"
                    )
                    continue

                students.append(Student(name, age, score))

    except FileNotFoundError:
        print(f"File '{filename}' không tồn tại.")
        return []
    except OSError as e:
        print(f"Lỗi khi đọc file: {e}")
        return []

    return students


def calc_avg_score(students: List[Student]) -> float:
    if not students:
        return 0.0
    total = 0.0
    for s in students:
        total += s.score
    return total / len(students)


def find_top_student(students: List[Student]) -> Student | None:
    if not students:
        return None

    top = students[0]
    for s in students[1:]:
        if s.score > top.score:
            top = s
    return top


def filter_failed(students: List[Student]) -> List[Student]:
    return [s for s in students if not s.is_passed()]


def main():
    filename = input("Nhập tên file điểm sinh viên: ").strip()

    students = load_students_from_file(filename)

    if not students:
        print("Không có dữ liệu sinh viên hợp lệ (hoặc không đọc được file).")
        return

    print(f"\nĐã load {len(students)} sinh viên từ file '{filename}'\n")

    # Điểm trung bình lớp
    avg = calc_avg_score(students)
    print(f"Điểm trung bình lớp: {avg:.2f}")

    # Sinh viên điểm cao nhất
    top = find_top_student(students)
    if top is not None:
        print("Sinh viên điểm cao nhất:")
        print("  ", top)
    else:
        print("Không tìm được sinh viên điểm cao nhất (list rỗng)")

    # Danh sách sinh viên rớt
    failed = filter_failed(students)
    if not failed:
        print("\nKhông có sinh viên rớt.")
    else:
        print("\nDanh sách sinh viên rớt:")
        for s in failed:
            print("  ", s)


if __name__ == "__main__":
    main()