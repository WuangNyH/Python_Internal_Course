# ===== Khái niệm =====
numbers = [1, 2, 3, 4, 5]
mixed = [1, "hello", True, 3.14]
empty = []

print(numbers)
print(mixed)


# ===== Truy cập phần tử =====
fruits = ["apple", "banana", "orange"]
print(fruits[0]) # apple
print(fruits[2]) # orange

print(fruits[-1]) # orange
print(fruits[-2]) # banana


# ===== Cắt list =====
numbers = [10, 20, 30, 40, 50]

print(numbers[1:4]) # [20, 30, 40]
print(numbers[:3]) # [10, 20, 30]
print(numbers[2:]) # [30, 40, 50]
print(numbers[:]) # copy list

print(numbers[::2]) # [10, 30, 50] => bỏ qua 1 phần tử
print(numbers[::-1]) # đảo list


# ===== Thay đổi phần tử =====
nums = [1, 2, 3]
nums[1] = 100
print(nums) # [1, 100, 3]


# ===== Thêm phần tử cuối list =====
names = ["An", "Binh"]
names.append("Cuong")
print(names)


# ===== Chèn vào vị trí bất kỳ =====
names.insert(1, "Taro")
print(names)


# ===== Nối 2 list =====
a = [1, 2, 3]
b = [4, 5]
a.extend(b)
print(a) # [1, 2, 3, 4, 5]


# ===== Tìm kiếm trong list =====
colors = ["red", "green", "blue"]
print("green" in colors) # True
print("yellow" in colors) # False


# ===== Các hàm built-in =====
nums = [4, 7, 1, 9]

print(len(nums)) # số phần tử
print(sorted(nums)) # trả về list mới đã sort

nums.sort() # Sắp xếp tại chỗ
print("sort tại chỗ:", nums)

# ===== Duyệt list =====
# Duyệt phần tử
for x in nums:
    print(x)

# Duyệt theo index
for i in range(len(nums)):
    print(i, nums[i])

# Duyệt index + value bằng enumerate()
for i, value in enumerate(nums, start=1):
    print(i, value)

# Duyệt song song nhiều list bằng zip()
students = ["A", "B", "C", "D"]
math = [9.0, 7.5, 8.0]
english = [8.5, 6.0, 9.0]

for s, m, e in zip(students, math, english):
    print(s, m, e)


# ===== List comprehension =====
nums = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]

# Tăng mỗi số lên 1
new_list = [n + 1 for n in nums]
print(new_list)

# Lọc phần tử theo điều kiện
evens = [x for x in nums if x % 2 == 0]
print(evens) # [0, 2, 4, 6, 8]

# Lọc phần tử theo điều kiện
pairs = [(x, y) for x in [1, 2] for y in [3, 4]]
print(pairs) # [(1, 3), (1, 4), (2, 3), (2, 4)]


# ===== 2D list =====
matrix = [
    [1, 2, 3],
    [4, 5, 6]
]

print(matrix[1][2]) # 6

for row in matrix:
    for value in row:
        print(value, end=" ")
    print()


# ===== Copy list =====
a = [1, 2, 3]
b = a
b[0] = 100
print(a) # bị thay đổi theo!

# Copy đúng cách
b = a.copy()
# hoặc
b = a[:]


# ===== Thay đổi list khi đang duyệt =====
a = [1, 2, 3, 4]
for x in a:
    print("Removing:", x)
    a.remove(x) # gây lỗi logic

print(a)