# ===== BTTH10 =====
nums = [1, 2, 2, 3, 4, 4, -1, 5]

# a. Dùng `set` để loại bỏ các số trùng lặp
unique_nums = set(nums)

#  b. Tạo lại một list mới `unique_nums` đã được sắp xếp giảm dần
print(sorted(unique_nums, reverse=True))
print(unique_nums)


# ===== BTTH11 =====
allowed_roles = {"admin", "editor", "viewer"}
user_role = input("Nhap role nguoi dung: ")

normalized_user_role = user_role.strip().lower()

if normalized_user_role in allowed_roles:
    print("Role hop le")
else:
    print("Role khong hop le")


# ===== BTTH12 =====
class_A = {"SV01", "SV02", "SV03", "SV04"}
class_B = {"SV03", "SV04", "SV05"}

# a) Học viên học cả 2 lớp (giao)
both_classes = class_A & class_B
# hoặc:
# class_A.intersection(class_B)

# b) Học viên chỉ học lớp A (hiệu)
only_A = class_A - class_B
# hoặc:
# class_A.difference(class_B)

# c) Tất cả học viên của 2 lớp (hợp)
all_students = class_A | class_B
# hoặc:
# class_A.union(class_B)

# d) Học viên chỉ học 1 trong 2 lớp (hiệu đối xứng)
only_one = class_A ^ class_B
# hoặc:
# class_A.symmetric_difference(class_B)

print("a) Ca 2 lop:", both_classes)
print("b) Chi lop A:", only_A)
print("c) Tat ca:", all_students)
print("d) Chi 1 trong 2 lop:", only_one)
