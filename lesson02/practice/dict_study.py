# ===== Khái niệm =====
student = {
    "name": "Nguyen Van A",
    "age": 20,
    "course": "Python Core",
}

print(student["name"]) # Nguyen Van A
print(student["age"]) # 20

# Mapping từ mã sang nội dung
status = {
    "A": "Đang học",
    "P": "Tạm nghỉ",
    "G": "Đã tốt nghiệp",
}

print(status["G"])  # Đã tốt nghiệp


# ===== Khởi tạo dictionary =====
# Dùng cặp `key: value` trong ngoặc nhọn
empty_dict = {}

student = {
    "name": "Nguyen Van A",
    "age": 20
}

# Dùng hàm `dict()`
user = dict(name="An", age=25)
print(user)  # {'name': 'An', 'age': 25}

# Từ `list`/`tuple` các cặp 2 phần tử
pairs = [("a", 1), ("b", 2), ("c", 3)]
my_dict = dict(pairs)
print(my_dict)  # {'a': 1, 'b': 2, 'c': 3}


# ===== Truy cập bằng `[]` =====
student = {"name": "An", "age": 20}
print(student["name"])  # An

# Lỗi khi `key` không tồn tại
# print(student["address"])  # KeyError: 'address'


# ===== Truy cập an toàn bằng `get()` =====
print(student.get("name")) # An
print(student.get("address")) # None

# Fallback trả giá trị mặc định
print(user.get("email", "N/A")) # nếu thiếu, mặc định là N/A
print(user.get("active", False))


# ===== Thêm mới / cập nhật =====
student = {"name": "An", "age": 20}
student["age"] = 21 # cập nhật
student["address"] = "Hanoi" # thêm mới

print(student) # {'name': 'An', 'age': 21, 'address': 'Hanoi'}


# ===== Xóa phần tử =====
# Dùng `del`
student = {"name": "An", "age": 20, "city": "Danang"}

del student["city"]
print(student)  # {'name': 'An', 'age': 20}

# Dùng `pop()`
student = {"name": "An", "age": 20, "city": "Danang"}

age = student.pop("age")
print(age) # 20
print(student)  # {'name': 'An', 'city': 'Danang'}

score = student.pop("score", "Unknown")
print(score)  # Unknown

# Xóa toàn bộ
student.clear()
print(student)  # {}


# ===== Duyệt theo key (mặc định) =====
student = {
    "name": "Nguyen Van A",
    "age": 20,
    "city": "Danang",
}

for key in student:
    print(key, "=>", student[key])


# ===== Duyệt `.keys()`, `.values()`, `.items()` =====
# Lấy danh sách key
print(student.keys()) # dict_keys(['name', 'age', 'city'])

# Lấy danh sách value
print(student.values()) # dict_values(['Nguyen Van A', 20, 'Danang'])

# Lấy cặp (key, value)
print(student.items())
# dict_items([('name', 'Nguyen Van A'), ('age', 20), ('city', 'Danang')])

# Duyệt với `items()`
for key, value in student.items():
    print(key, ":", value)


# ===== Toán tử `in` với dict =====
student = {"name": "An", "age": 20}

print("name" in student) # True
print("address" in student) # False


# ===== Gộp / cập nhật nhiều phần tử với `update()` =====
student = {"name": "An", "age": 20}

extra = {"age": 21, "city": "Danang"}
student.update(extra)

# update bằng keyword argument
student.update(hobby="football")
print(student) # {'name': 'An', 'age': 21, 'city': 'Danang', 'hobby': 'football'}


# ===== Nested dict =====
students = {
    "SV01": {
        "name": "Nguyen Van A",
        "age": 20,
        "scores": [8.0, 7.5, 9.0],
    },
    "SV02": {
        "name": "Tran Thi B",
        "age": 21,
        "scores": [7.0, 8.5, 8.0],
    },
}

print(students.get("SV01").get("name")) # Nguyen Van A
print(students.get("SV02").get("scores")[1]) # 8.5
