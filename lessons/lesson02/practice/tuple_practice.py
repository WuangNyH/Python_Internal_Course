# ===== BTTH4 =====
student_info = ("Nguyen Van A", 20, "Python Core")

full_name, score, course = student_info
print(f"Name: {full_name}")
print(f"Score: {score}")
print(f"Course: {course}")


# ===== BTTH5 =====

def calculate_stats(scores: list[float]) -> tuple[float, float, float]:
    return sum(scores) / len(scores), min(scores), max(scores)

scores = [7.5, 8.0, 6.5, 9.0, 8.5]
avg, min_score, max_score = calculate_stats(scores)
print(f"Average score: {avg}")
print(f"Minimum score: {min_score}")
print(f"Maximum score: {max_score}")


# ===== BTTH6 =====
# a. Dùng vòng lặp + unpacking tuple để in ra từng học viên theo format `Name: ..., Age: ..., Score: ...`
students = [
    ("Nguyen Van A", 20, 8.5),
    ("Tran Thi B", 19, 7.0),
    ("Le Van C", 21, 9.0),
]

for full_name, age, score in students:
    print(f"Full name: {full_name}, Age: {age}, Score: {score}")

# b. Tạo một list mới `scores` chỉ chứa điểm số của học viên, bằng:
# Cách 1
scores = []

for _, _, score in students:
    scores.append(score)

print(f"Scores: {scores}")

# Cách 2
scores = [score for _, _, score in students]
print(f"Scores: {scores}")

# c. Tìm học viên có điểm cao nhất, in ra `Top student: <name>, Score: <score>`
# Cách 1: Dùng for tìm max
top_student = students[0] # gán tạm cho tuple student đầu tiên

for student in students:
    if student[2] > top_student[2]:
        top_student = student

print(f"Top student: {top_student}")

# Cách 2: Dùng hàm max() với tham số key
# students không phải là 1 list điểm gồm [8.5, 7.0, 9.0]
# students là list[tuple[name, age, score]]
# => python ko thể biết lấy max trên phần tử nào của tuple
# dùng tham số key: so sánh max trên giá trị nào của tuple, list, ...
# => truyền hàm get_score bằng lambda cho key (lấy giá trị tuple[2] để so sánh max)
def get_score(student: tuple[str, int, float]) -> float:
    return student[2]

top_student = max(students, key=lambda student: get_score(student))

# Hoặc truyền hàm trực tiếp
# top_student = max(students, key=get_score)

# Hoặc sử dụng hàm lambda ẩn danh (ko cần định nghĩa hàm get_score())
# top_student = max(students, key=lambda student: student[2])

# max() trả về phần tử gốc (ở đây là tuple)
print(f"Top student: {top_student}")
