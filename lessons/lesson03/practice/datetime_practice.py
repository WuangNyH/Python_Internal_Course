# ===== BTTH4: In ngày giờ hiện tại theo nhiều định dạng =====

from datetime import datetime

now = datetime.now()

# Năm-Tháng-Ngày: DD-MM-YYYY
date_str = now.strftime("%d-%m-%Y")
print("Ngày-Tháng-Năm:", date_str)

# Giờ:Phút:Giây: HH:MM:SS
time_str = now.strftime("%H:%M:%S")
print("Giờ:Phút:Giây:", time_str)

# Hôm nay là thứ mấy?
# weekday(): Monday = 0, Sunday = 6
weekday_num = now.weekday()

weekday_map = {
    0: "Thứ Hai",
    1: "Thứ Ba",
    2: "Thứ Tư",
    3: "Thứ Năm",
    4: "Thứ Sáu",
    5: "Thứ Bảy",
    6: "Chủ Nhật",
}

print("Hôm nay là:", weekday_map[weekday_num])


# ===== BTTH5: Tính tuổi từ ngày sinh =====

# from datetime import datetime
#
# input_str = input("Nhập ngày sinh (dd/mm/yyyy): ")
#
# try:
#     dob = datetime.strptime(input_str, "%d/%m/%Y")
#     today = datetime.now()
#     age = (today - dob).days // 365
#     print("Tuổi:", age)
# except ValueError:
#     print("Ngày sinh không hợp lệ! Vui lòng nhập đúng dạng dd/mm/yyyy")


# ===== BTTH6: Đo thời gian thực thi thuật toán =====

from time import time, perf_counter

n = 1_000_000

# 1) Tính tổng bằng vòng lặp
start = time()
total_loop = 0
for i in range(1, n + 1):
    total_loop += i
end = time()
loop_time = end - start

print("Tổng (vòng lặp):", total_loop)
print("Thời gian (vòng lặp):", loop_time, "giây")

# 2) Tính tổng bằng công thức
start = perf_counter()
total_formula = n * (n + 1) // 2 # dùng // để ra số nguyên
end = perf_counter()
formula_time = end - start

print("Tổng (công thức):", total_formula)
print("Thời gian (công thức):", formula_time, "giây")

# So sánh
print("Công thức nhanh hơn bao nhiêu lần (xấp xỉ):",
      loop_time / formula_time if formula_time > 0 else "∞") # tránh lỗi "div by zero"
