# ===== Lấy thời gian hiện tại =====

from datetime import datetime

now = datetime.now()
print(now)

print(now.year)
print(now.month)
print(now.day)
print(now.hour)
print(now.minute)
print(now.second)


# ===== Tạo đối tượng DateTime cụ thể =====
# specific = datetime(2025, 2, 14, 20, 30, 0)
# print(specific)


# ===== Định dạng ngày giờ: strftime =====
# now = datetime.now()
# formatted = now.strftime("%Y-%m-%d %H:%M:%S")
# print(formatted)
#
# print(now.strftime("Hôm nay là %A, ngày %d/%m/%Y"))


# ===== Chuyển chuỗi thành datetime: strptime =====
# s = "2025-02-14 20:30:00"
# dt = datetime.strptime(s, "%Y-%m-%d %H:%M:%S")
# print(dt)


# ===== Cộng / trừ ngày timedelta =====
from datetime import timedelta

# now = datetime.now()
# tomorrow = now + timedelta(days=1)
# yesterday = now - timedelta(days=1)
#
# print(tomorrow)
# print(yesterday)
#
# in_three_hours = now + timedelta(hours=3)
# two_weeks_ago = now - timedelta(weeks=2)
#
# print(in_three_hours)
# print(two_weeks_ago)


# ===== So sánh thời gian =====
# x = datetime(2025, 1, 1)
# y = datetime(2024, 1, 1)
#
# print(x > y) # True
# print(x == y) # False


# ===== Đo thời gian thực thi đoạn code =====
# import time
#
# start = time.time()
#
# # --- đoạn code cần đo thời gian ---
# result = 0
# for i in range(1_000_000):
#     result += i
# # ----------------------------------
#
# end = time.time()
# elapsed = end - start
# print("Thời gian thực thi:", elapsed, "giây")


# Dùng perf_counter()
# from time import perf_counter
#
# start = perf_counter()
# for i in range(1_000_000):
#     pass
# end = perf_counter()
#
# print("Elapsed:", end - start)
