# Bài 7: Đổi chữ hoa thành chữ thường và ngược lại bằng mã ASCII

character = input("Nhập một ký tự: ")

# Kiểm tra số lượng ký tự (phải nhập đúng 1 ký tự)
if len(character) != 1:
    print("Bạn phải nhập đúng 1 ký tự!")
else:
    code = ord(character) # Lấy mã ASCII

    # Kiểm tra có phải chữ cái hay không
    if 65 <= code <= 90: # chữ hoa A-Z
        converted = chr(code + 32) # chuyển sang chữ thường
        print(f"Ký tự sau khi chuyển đổi: {converted}")

    elif 97 <= code <= 122: # chữ thường a-z
        converted = chr(code - 32) # chuyển sang chữ hoa
        print(f"Ký tự sau khi chuyển đổi: {converted}")

    else:
        print("Bạn đã nhập sai (không phải chữ cái)")
