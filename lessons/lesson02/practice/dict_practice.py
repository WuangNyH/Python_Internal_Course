from typing import Any

# ===== BTTH7 =====
student: dict[str, Any] = {
    "name": "Nguyen Van A",
    "age": 20,
    "scores": [7.5, 8.0, 6.5, 9.0],
}

# a. In ra tên và tuổi của sinh viên theo format
print(f"Name: {student.get('name')}")
print(f"Age: {student.get('age')}")

# b. Tính điểm trung bình từ `scores` và thêm vào dict với key `"avg_score"`
scores = student.get("scores")
avg_score = sum(scores) / len(scores)

student["avg_score"] = avg_score

# update bằng keyword argument
# student.update(avg_score=avg_score)
print(student)


# ===== BTTH8 =====
s = "hello world"

counter: dict[str, int] = {}

# Cách 1
for char in s:
    if char not in counter:
        counter[char] = 1
    else:
        counter[char] += 1

# Cách 2: dùng get() với mặc định là 0
for char in s:
    counter[char] = counter.get(char, 0) + 1

print(counter)


# ===== BTTH9 =====
students: dict[str, dict[str, Any]] = {
    "SV01": {"name": "Nguyen Van A", "age": 20},
    "SV02": {"name": "Tran Thi B", "age": 21},
}

# a. Thêm sinh viên mới `SV03` với tên và tuổi bất kỳ
student3 = {"name": "Phan Van C", "age": 18}
students["SV03"] = student3
print(students)

# b. Cập nhật tuổi của `SV01` tăng thêm 1
students["SV01"]["age"] += 1
print(students)

# c. Duyệt `students` và in ra theo format
for student_id, info in students.items():
    print(f"{student_id}: {info.get("name")} ({info.get("age")})")

