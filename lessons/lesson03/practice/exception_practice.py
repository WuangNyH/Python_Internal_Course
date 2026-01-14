# ===== BTTH1: Bắt lỗi nhập số =====

n = 0
while n <= 0:
    user_input = input("Nhập số nguyên dương: ")
    try:
        n = int(user_input)
        if n <= 0:
            print("Vui lòng nhập số nguyên dương > 0")
        else:
            print("Bạn đã nhập:", n)
            break
    except ValueError:
        print("Nhập sai rồi kìa, nhập lại dùm cái")


# ===== BTTH2: Tạo menu và xử lý lỗi lựa chọn =====

# def tinh_bmi():
#     try:
#         weight = float(input("Nhập cân nặng (kg): "))
#         height = float(input("Nhập chiều cao (m): "))
#         if height <= 0:
#             print("Chiều cao phải > 0")
#             return
#         if weight <= 0:
#             print("Cân nặng phải > 0")
#             return
#         bmi = weight / (height ** 2)
#         print(f"Chỉ số BMI của bạn là: {bmi:.2f}")
#     except ValueError:
#         print("Vui lòng nhập số hợp lệ cho cân nặng và chiều cao")
#
# while True:
#     print("\n=== MENU ===")
#     print("1. Xin chào")
#     print("2. Tính chỉ số BMI")
#     print("3. Thoát")
#
#     choice_input = input("Chọn chức năng (1-3): ")
#
#     try:
#         choice = int(choice_input)
#     except ValueError:
#         print("Lỗi: Vui lòng nhập một SỐ từ 1 đến 3")
#         continue
#
#     if choice == 1:
#         print("Xin chào! Chúc học Python vui vẻ")
#     elif choice == 2:
#         tinh_bmi()
#     elif choice == 3:
#         print("Thoát chương trình, bái bai!")
#         break
#     else:
#         print("Lỗi: Vui lòng chọn số từ 1 đến 3")


# ===== BTTH3: Đọc file an toàn =====
# filename = input("Nhập tên file: ")
#
# # Kiểm tra file tồn tại
# file_exists = True
# try:
#     f = open(filename, "r", encoding="utf-8")
#     f.close()
# except FileNotFoundError:
#     print(f"File '{filename}' không tồn tại, hãy nhập đúng tên file và đường dẫn, hoặc chọn chức năng 'ghi'")
#     file_exists = False
#
#
# while True:
#     print("\n=== MENU ===")
#     print("1. Đọc toàn bộ file")
#     print("2. Đọc từng dòng")
#     print("3. Ghi đè file (write)")
#     print("4. Ghi thêm vào file (append)")
#     print("5. Thoát")
#
#     try:
#         choice = int(input("Chọn chức năng: "))
#     except ValueError:
#         print("Vui lòng nhập số từ 1–5")
#         continue
#
#     if choice == 1:
#         try:
#             with open(filename, "r", encoding="utf-8") as f:
#                 content = f.read()
#                 print("\n--- Nội dung file ---")
#                 print(content if content else "(File rỗng)")
#         except FileNotFoundError:
#             print("File chưa tồn tại, không thể đọc")
#
#     elif choice == 2:
#         try:
#             with open(filename, "r", encoding="utf-8") as f:
#                 print("\n--- Các dòng trong file ---")
#                 for line in f:
#                     print(line.strip())
#         except FileNotFoundError:
#             print("File chưa tồn tại, không thể đọc")
#
#     elif choice == 3:
#         data = input("Nhập nội dung để ghi vào file: ")
#         with open(filename, "w", encoding="utf-8") as f:
#             f.write(data + "\n")
#         print("Đã ghi file")
#
#     elif choice == 4:
#         data = input("Nhập nội dung để thêm: ")
#         with open(filename, "a", encoding="utf-8") as f:
#             f.write(data + "\n")
#         print("Đã thêm nội dung vào file")
#
#     elif choice == 5:
#         print("Bái bai")
#         break
#
#     else:
#         print("Vui lòng chọn số từ 1–5")
