# Giải phương trình bậc hai có dạng: `ax2 + bx + c = 0`
a = float(input("Nhập hệ số a = "))
b = float(input("Nhập hệ số b = "))
c = float(input("Nhập hệ số c = "))

if a == 0:
    # Trở thành PT bậc nhất
    if b == 0:
        if c == 0:
            print("PT vô số nghiệm")
        else:
            print("PT vô nghiệm")
    else:
        x = - c / b
        print(f"PT có nghiệm x = {x:.2f}")
else:
    delta = b**2 - 4 * a * c
    print("delta = ", delta)

    if delta < 0:
        print("PT vô nghiệm")
    elif delta == 0:
        x = - b / (2 * a)
        print(f"PT có nghiệm kép x = {x:0.2f}")
    else:
        x1 = (-b + delta**0.5) / (2 * a)
        x2 = (-b - delta**0.5) / (2 * a)
        print("PT có 2 nghiệm phân biệt:")
        print(f"x1 = {x1:.2f}")
        print(f"x2 = {x2:.2f}")
