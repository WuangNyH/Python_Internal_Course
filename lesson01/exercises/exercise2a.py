# ===== Cách 1: Đổi chỗ hai biến bằng biến tạm =====
a = int(input("Nhập số nguyên a: "))
b = int(input("Nhập số nguyên b: "))

print(f"Trước khi hoán chỗ: a = {a}, b = {b}")

temp = a
a = b
b = temp

print(f"Sau khi hoán chỗ: a = {a}, b = {b}")


# ===== Cách 2: Đổi chỗ hai biến không dùng biến tạm =====
