# ===== BTTH4: Tính tổng từ 1 đến n =====
# Yêu cầu người dùng phải nhập n>0
n = 0
while n <= 0:
    n = int(input("Nhập n nguyên dương: "))
    if n <= 0:
        print("n phải lớn hơn 0, hãy nhập lại")

s = 0
for i in range(1, n + 1):
    s += i

print(f"Tổng từ 1 đến {n} là {s}")


# ===== BTTH5: Đếm số ký tự 'a' trong chuỗi =====
string = input("Nhập chuỗi: ")

count = 0
for char in string:
    if char == "a":
        count += 1

print(f"Số ký tự 'a' trong chuỗi: {count}")


# ===== BTTH6: In hình =====
"""
6a. Hình chữ nhật rỗng
* * * * * *
*         *
*         *
*         *
* * * * * *
"""
row, col = 5, 6
for i in range(row):
    for j in range(col):
        if i == 0 or i == row - 1 or j == 0 or j == col - 1:
            print("*", end=" ")
        else:
            print(" ", end=" ")
    print()


"""
6b. Hình tam giác vuông cân
*
* *
* * *
* * * *
* * * * *
"""
for i in range(row):
    for j in range(col):
        if j <= i:
            print("*", end=" ")
        else:
            print(" ", end=" ")
    print()

