# ===== Khởi tạo object =====
from student import Student


s1 = Student("An", 20, 8.5)
print(s1.name) # An
print(s1.age) # 20
print(s1.score) # 8.5

s2 = Student("Binh", 21, 7.8)


# ===== Method =====
# s3 = Student("An", 20, 7.5)
#
# s3.introduce() # Hi, mình là An, 20 tuổi
# print(s3.is_passed()) # True


# ===== list[Student] =====
# student_list = [
#     Student("An", 20, 8.5),
#     Student("Binh", 21, 6.0),
#     Student("Chi", 19, 4.5),
# ]

# In danh sách sinh viên
# for s in students:
#     s.introduce()

# Tính điểm trung bình của lớp
# def calc_avg_score(students: list[Student]) -> float:
#     if not students:
#         return 0
#     total = 0
#     for s in students:
#         total += s.score
#     return total / len(students)
#
# avg = calc_avg_score(student_list)
# print("Điểm trung bình lớp:", avg)

# Tìm sinh viên điểm cao nhất
# def find_top_student(students: list[Student]) -> Student | None:
#     if not students:
#         return None
#     top = students[0]
#     for s in students[1:]:
#         if s.score > top.score:
#             top = s
#     return top
#
# empty_list = []
# best = find_top_student(student_list)
#
# if not best:
#     print("Ko có data")
# else:
#     print("Top student:", best.name, best.score)


# ===== Encapsulation =====
# acc = BankAccount("An", 1000)
# acc.deposit(500)
# acc.withdraw(300)
# print(acc.get_balance()) # 1200


# ===== @property =====
# p = Person("An", 20)
#
# print(p.age) # gọi getter, age ko phải là biến thật (_age là biến thật)
# p.age = 25 # gọi setter
#
# try:
#     p.age = -1 # raise ValueError
# except ValueError as e:
#     print(e)

# thuộc tính chỉ đọc
# p.income = 1000 # Lỗi TypeError: Person.__init__() missing 1 required positional argument: 'income'


# ===== __str__ =====
# students = [Student("An", 20, 8.5), Student("Binh", 21, 6.0)]
# print(students)
#
# p = Person("An", 20, 1000)
# print(p)


# ===== __repr__ =====
# p2 = Person("Nam", 20, 1000)
# print(repr(p2))


# ===== *args =====
# logger = Logger()
# logger.log()
# logger.log("Xin chao", "Python", 3)


# ===== *kwargs =====
# def show_info(**kwargs):
#     print(kwargs)
#
# show_info(name="An", age=20, score=8.5)


# ===== Kết hợp `*args` và `*kwargs` =====
# def introduce(
#         name: str,
#         age: int,
#         *skills,
#         title: str = "N/A",
#         level: str = "basic",
#         **extra_info) -> None:
#     print("Name:", name)
#     print("Age:", age)
#     print("Skills:", skills)
#     print("Title:", title)
#     print("Level:", level)
#     print("Extra:", extra_info)
#
#
# introduce(
#     "An",
#     20,
#     "Python",
#     "Java",
#     title="Developer",
#     level="Fresher",
#     hobby="gaming",
#     city="Danang"
# )


# ===== Constructor linh hoạt =====
# staff = Staff("An", 20, hobby="gaming", city="DN")
# print(staff.extra)


# ===== getattr() =====
# staff = Staff("An", 20, hobby="gaming", city="DN")
# print(getattr(staff, "name"))
# print(getattr(staff, "extra"))

# Khi không cung cấp default, Python sẽ báo lỗi:
# print(getattr(staff, "salary"))

# Xử lý khi thuộc tính không tồn tại
# print(getattr(staff, "salary", "Không có lương"))
