# ===== String là immutable =====
s = "python"
# s[0] = "P"

s = "P" + s[1:]  # tạo chuỗi mới từ kí tự 'P' + phần còn lại "ython"
print(s)  # Python

for ch in s:
    print(ch)

print("a" in "banana")


# ===== Truy cập & cắt chuỗi (index, slice) =====
print(s[0])
print(s[-1])
print(s[1:4])

s1 = "Hello World"
print(s1[:5])
print(s1[6:])
print(s1[:])

s2 = "abcdefg"
print(s2[::2])
print(s2[::-1])


# ===== upper(), lower(), title() =====
s3 = "hello world"

print(s3.upper()) # "HELLO WORLD"
print(s3.lower()) # "hello world"
print(s3.title()) # "Hello World"


# ===== strip(), replace() =====
s4 = "   hello world   "

print(s4.strip()) # "hello world" (bỏ khoảng trắng đầu & cuối)
print(s4.lstrip()) # "hello world   " (bỏ bên trái)
print(s4.rstrip()) # "   hello world" (bỏ bên phải)

print(s4.strip().replace("hello", "hi"))  # "hi world"


# ===== split() =====
s5 = "python is fun"
words = s5.split() # mặc định tách theo khoảng trắng
print(words) # ['python', 'is', 'fun']

s6 = "a,b,c,d"
items = s6.split(",") # tách theo dấu phẩy
print(items) # ['a', 'b', 'c', 'd']


# ===== join() =====
words2 = ["python", "is", "boring"]
sentence = " ".join(words2)
print(sentence)  # "python is boring"

items2 = ["a", "b", "c"]
print("-".join(items2)) # "a-b-c"


# ===== startswith(), endswith() =====
filename = "report.pdf"

print(filename.endswith(".pdf")) # True
print(filename.startswith("rep")) # True
print(filename.startswith("Report")) # False (phân biệt hoa thường)


# ===== So sánh chuỗi với == =====
a = "hello"
b = "hello"
c = "Hello"

print(a == b) # nội dung giống nhau => True
print(a == c) # khác hoa/thường => False


# ===== So sánh chuỗi lớn hơn/nhỏ hơn (<, >, …) =====
print("apple" < "banana") # True
print("abc" > "ab") # True (vì 'abc' dài hơn, 'ab' là prefix)
