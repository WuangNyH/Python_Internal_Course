# Bài 1: Quản lý học viên & khóa học

# Dữ liệu ban đầu
students = [
    ("SV01", "Nguyen Van A", 20),
    ("SV02", "Tran Thi B", 21),
    ("SV03", "Le Van C", 19),
]

scores = {
    "SV01": {"math": 8.0, "python": 7.5},
    "SV02": {"math": 6.5, "python": 8.5},
    "SV03": {"math": 9.0, "python": 9.5},
}

courses = {"math", "python"}

# a. In danh sách học viên (list + tuple + unpacking)
for student_id, name, age in students:
    print(f"{student_id} - {name} ({age})")


# b. Tạo list python_scores gồm tuple (id, name, python_score)
python_scores = []

for student_id, name, age in students:
    python_score = scores[student_id]["python"]
    python_scores.append((student_id, name, python_score))

print(python_scores)


# c. Tìm học viên có điểm Python cao nhất (max + key)
top_student = max(python_scores, key=lambda s: s[2])

student_id, name, python_score = top_student
print(f"Top Python: {name} - {python_score}")


# d. Thêm môn "database" vào set và cập nhật điểm cho từng sinh viên
courses.add("database")

for student_id in scores:
    scores[student_id]["database"] = 0

print(courses)
print(scores)
