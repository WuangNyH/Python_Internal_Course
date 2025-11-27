# Bài 8: Kiểm tra số chính phương

import math

x = int(input("Nhập số nguyên dương x: "))

# Kiểm tra điều kiện đầu vào
if x < 0:
    print("Giá trị không hợp lệ! x phải là số nguyên dương.")
else:
    square_root = math.sqrt(x)

    # Kiểm tra phần thập phân bằng 0 → là số nguyên
    if square_root % 1 == 0:
        print(f"{x} là số chính phương")
    else:
        print(f"{x} không phải là số chính phương")
