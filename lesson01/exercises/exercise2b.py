# ===== Cách 2: Đổi chỗ hai biến không dùng biến tạm =====
a = int(input("Nhập số nguyên a: "))
b = int(input("Nhập số nguyên b: "))

print(f"Trước khi hoán chỗ: a = {a}, b = {b}")

a = a + b # dùng biến a chứa tổng
b = a - b # b = (a + b) - b = a ban đầu
a = a - b # a = (a + b) - (a ban đầu) = b ban đầu

print(f"Sau khi hoán chỗ: a = {a}, b = {b}")
