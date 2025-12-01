"""
Xếp loại học viên:
    Điểm < 5: Yếu
    Điểm >= 5: Khá
"""
score = int(input("Nhập điểm: "))

# Câu điều kiện thiếu
if score < 5:
    print("Yếu")

if score >= 5:
    print("Khá")

# Câu điều kiện đủ
if score < 5:
    print("Yếu")
else:
    print("Khá")

"""
Xếp loại học viên:
    Điểm < 5: Yếu
    Điểm >= 5 và điểm < 7: Trung bình
    Điểm >= 7 và điểm < 8.5: Khá
    Điểm >= 8.5: Giỏi
"""
score = float(input("Nhập điểm: "))

if score < 5:
    print("Yếu")
elif score < 7:
    print("Trung bình")
elif score < 8.5:
    print("Khá")
else:
    print("Giỏi")

# Ví dụ SAI về thứ tự kiểm tra:
score = 4.0

if score < 8.5:
    print("Giỏi")
elif score < 7:
    print("Khá")
elif score < 5:
    print("Trung bình")
else:
    print("Yếu")

# Nested if
age = 20

if age >= 18:
    print("Đã đủ 18+")
    if age >= 60:
        print("Đã đủ tuổi hưu")

# Ternary Operator
status = "18+" if age >= 18 else "Chưa đủ tuổi"
print("Tình trạng:", status)

a, b = 10, 5
max_value = a if a > b else b
print("max_value=", max_value)
