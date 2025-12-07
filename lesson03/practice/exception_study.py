# ===== Cú pháp try / except =====

try:
    # đoạn code có nguy cơ lỗi
    x = 10 / 0
except ZeroDivisionError:
    print("Không thể chia cho 0!")

# Nhiều loại lỗi
try:
    raw = input("Nhập một số nguyên: ")
    x = int(raw)
    y = 10 / x
    print(f"Kết quả 10 / {x} =", y)
except ValueError:
    print("Lỗi: Bạn phải nhập một số nguyên hợp lệ!")
except ZeroDivisionError:
    print("Lỗi: Không thể chia cho 0!")
except Exception as e:
    print("Lỗi không xác định:", e)


# ===== Bắt nhiều lỗi trong cùng một except =====
try:
    x = int("abc")
except (ValueError, TypeError):
    print("Lỗi nhập liệu!")


# ===== Bắt mọi lỗi =====
def risky_code(a):
    print(1/a)

try:
    risky_code(0)
except Exception as e:
    print("Có lỗi xảy ra:", e)


# ===== Tự tạo exception bằng raise =====

