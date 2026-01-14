# ===== Lỗi SyntaxError =====
# if x > 0
#     print("x > 0")


# ===== Lỗi runtime =====
x = 10
# print(x / 0) # ZeroDivisionError: division by zero

nums = [1, 2, 3]
# print(nums[10])  # IndexError: list index out of range


# ===== Lỗi logic =====
# Tính trung bình nhưng quên chia cho số lượng phần tử
nums = [1, 2, 3]
avg = sum(nums) # sai logic
print(avg) # 6, đáng lẽ phải là 2.0


# ===== Cách đọc traceback =====
nums = [1, 2, 3]
print(nums[5])


