# ===== Đọc file =====

# read(): đọc toàn bộ file, trả về một chuỗi
with open("data.txt", "r", encoding="utf-8") as f:
    content = f.read()
print(content)

# readline(): đọc từng dòng một
# with open("data.txt", "r", encoding="utf-8") as f:
#     line1 = f.readline()
#     line2 = f.readline()
#     line3 = f.readline().strip()
#     line4 = f.readline().strip()
#
# print(line1)
# print(line2)
# print(line3)
# print(line4)

# readlines(): đọc tất cả dòng, trả về list
# with open("data.txt", "r", encoding="utf-8") as f:
#     lines = f.readlines()
#
# for line in lines:
#     print(line.strip())


# ===== Ghi file =====

# Ghi file bằng write() với chế độ "w"
# with open("output.txt", "w", encoding="utf-8") as f:
#     f.write("Xin chào Python!\n")
#     f.write("Dòng thứ hai\n")

# Ghi file bằng write() với chế độ "a"
# with open("output.txt", "a", encoding="utf-8") as f:
#     f.write("Dòng mới được thêm vào\n")


# ===== Ghi list vào file =====

# write với vòng lặp
lines = ["Hello", "Python", "File I/O"]
with open("list.txt", "w", encoding="utf-8") as f:
    for line in lines:
        f.write(line + "\n")

# writelines
with open("list.txt", "w", encoding="utf-8") as f:
    lines = ["Xin chào Python!\n", "Dòng thứ hai\n"]
    f.writelines(lines)


# ===== Xử lý ngoại lệ khi thao tác file =====

# FileNotFoundError
# try:
#     with open("abc.txt", "r") as f:
#         data = f.read()
# except FileNotFoundError:
#     print("Không tìm thấy file!")
