print("Hello, Techzen Academy!")

age = 20
height = 1.7
name = "Taro"
is_student = True

# In ra kiểu dữ liệu
print(type(age), type(height), type(name), type(is_student))

# Nhập dữ liệu từ bàn phím
name = input("Nhập tên: ")
age = int(input("Nhập tuổi: "))  # cần ép sang int

# Xuất dữ liệu đơn giản
print("Xin chào", name, "- Bạn", age, "tuổi")

# Xuất dữ liệu với f-string

# f"...{variable}..."
print(f"Xin chào {name}\nBạn {age} tuổi")

# f"...{expression}..."
a, b = 5, 7
print(f"Tổng của {a} và {b} là {a + b}")
print(f"Tên in hoa: {name.upper()}")
