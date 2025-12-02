# ===== BTTH1: Kiểm tra tuổi =====
age = int(input("Nhập tuổi: "))

if age < 0:
    print("Tuổi không thể âm được người đẹp ơi")
elif age < 11:
    print("Trẻ con")
elif age < 18:
    print("Thiếu niên")
elif age < 30:
    print("Thanh niên")
else:
    print("Già rồi người đẹp ơi")


# ===== BTTH2: Kiểm tra chẵn lẻ =====
n = int(input("Nhập số nguyên dương: "))

if n < 0:
    print("Vui lòng nhập số nguyên dương người đẹp ơi")

result = "Even" if n % 2 == 0 else "Odd"
print(result)


# ===== BTTH3: Kiểm tra năm nhuận =====
year = int(input("Nhập năm: "))

if year < 0:
    print("Năm không thể âm được người đẹp ơi")
elif (year % 400 == 0) or (year % 4 == 0 and year % 100 != 0):
    print(year, "là năm nhuận")
else:
    print(year, "không phải năm nhuận")
