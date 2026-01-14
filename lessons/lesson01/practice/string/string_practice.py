#### ===== BTTH9: Chuẩn hóa họ tên =====
def normalize_name(name: str) -> str:
    name = name.strip()
    return name.title()

name1 = "  nGuyEn vAn a   "
print(normalize_name(name1))


#### ===== BTTH10: Kiểm tra chuỗi đối xứng =====
def is_palindrome(s: str) -> bool:
    s = s.lower().strip().replace(" ", "")
    return s == s[::-1]

print(is_palindrome("level"))
print(is_palindrome("madam "))
print(is_palindrome("122 1"))
print(is_palindrome("hello"))


#### ===== BTTH11: Đếm số lượng nguyên âm trong chuỗi =====
def count_vowels(s: str) -> int:
    vowels = "aeiou"
    count = 0
    for char in s.lower():
        if char in vowels:
            count += 1
    return count

print(count_vowels("Hello World"))
print(count_vowels("Python"))
print(count_vowels("AEiOU"))
