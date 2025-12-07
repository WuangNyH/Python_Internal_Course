# ===== Khái niệm =====
point = (10, 20)
print(point[0])


# ===== Tuple nhiều phần tử =====
nums = (1, 2, 3)
colors = ("red", "green", "blue")
mixed = (1, "hello", True, 3.14)


# ===== Tuple nhiều phần tử =====
nums = 1, 2, 3  # vẫn là tuple
print(type(nums))  # <class 'tuple'>


# ===== Tuple nhiều phần tử =====
x = (5) # KHÔNG phải tuple, chỉ là số 5
x_tuple = (5,) # Đây mới là tuple 1 phần tử

print(type(x)) # <class 'int'>
print(type(x_tuple)) # <class 'tuple'>


# ===== Truy cập phần tử trong tuple =====
fruits = ("apple", "banana", "orange")

print(fruits[0]) # apple
print(fruits[2]) # orange
print(fruits[-1]) # orange (index âm từ phải sang trái)

# print(fruits[10])  # IndexError: tuple index out of range


# ===== Slicing với tuple =====
nums = (10, 20, 30, 40, 50)

print(nums[1:4]) # (20, 30, 40)
print(nums[:3]) # (10, 20, 30)
print(nums[2:]) # (30, 40, 50)
print(nums[::2]) # bước nhảy 2 => (10, 30, 50)
print(nums[::-1]) # nghịch đảo => (50, 40, 30, 20, 10)


# ===== Tuple là immutable =====
nums = (1, 2, 3)
# nums[1] = 100  # TypeError: 'tuple' object does not support item assignment

# Có thể tạo tuple mới từ tuple cũ
nums = (1, 2, 3)
nums2 = nums + (4, 5)
print(nums2)  # (1, 2, 3, 4, 5)


# ===== Unpacking =====
point = (10, 20)
x, y = point

print(x)  # 10
print(y)  # 20

# Số biến ko khớp với tuple
p = (1, 2, 3)
a, b, c = p # OK
# a, b = p # ValueError: too many values to unpack


# ===== Unpacking với _ =====
student = ("Taro", 20, "Tokyo")
name, age, _ = student  # bỏ qua city

print(name, age)  # Taro 20


# ===== Unpacking với * =====
nums = (1, 2, 3, 4, 5)
first, *middle, last = nums

print(first) # 1
print(middle) # [2, 3, 4]
print(last) # 5


# ===== Dùng tuple để trả về nhiều giá trị từ hàm =====
def get_min_max(numbers: list[float]) -> tuple[float, float]:
    minimum = min(numbers)
    maximum = max(numbers)
    return minimum, maximum  # Python tự gói thành tuple

scores = [7.5, 8.0, 6.5, 9.0, 8.5]
min_score, max_score = get_min_max(scores)

print("Min:", min_score)
print("Max:", max_score)


# ===== Dùng tuple làm key cho dict =====
students = {}

key1 = ("Nguyen", "An")
key2 = ("Tran", "Binh")

students[key1] = 8.5
students[key2] = 9.0

print(students[("Nguyen", "An")])  # 8.5

# Nếu dùng list làm key sẽ bị lỗi
key = ["Nguyen", "An"]
# my_dict = {key: 8.5} # TypeError: cannot use 'list' as a dict key (unhashable type: 'list')


# ===== Một số hàm & thao tác thường dùng với tuple =====
nums = (4, 7, 1, 9)

print(len(nums)) # 4
print(min(nums)) # 1
print(max(nums)) # 9
print(sum(nums)) # 21
print(sorted(nums)) # [1, 4, 7, 9]  (trả về LIST mới => ko thay đổi nums)

# duyệt tuple
for x in nums:
    print(x)

# duyệt index + value
for i, value in enumerate(nums):
    print(i, value)

# duyệt tuple song song với zip()
a = (1, 2, 3)
b = ("A", "B", "C")

for x, y in zip(a, b):
    print(x, y)
