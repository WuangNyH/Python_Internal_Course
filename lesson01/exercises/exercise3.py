# Giải phương trình bậc nhất có dạng: `ax + b = 0`
a = float(input("Nhập hệ số a = "))
b = float(input("Nhập hệ số b = "))

if a == 0:
    if b == 0:
        print("PT vô số nghiệm")
    else:
        print("PT vô nghiệm")
else:
    x = - b / a
    print(f"PT có nghiệm x = {x:.2f}") # làm tròn 2 chữ số
