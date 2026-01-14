# ===== Khái niệm =====

numbers = {1, 2, 3, 3, 4}
print(numbers) # {1, 2, 3, 4} (3 chỉ xuất hiện 1 lần)


# ===== Khởi tạo set =====
# Dùng ngoặc nhọn
numbs = {1, 2, 3}
characters = {"a", "b", "c"}
mixed = {1, "hello", (2, 3)}

# Lỗi `TypeError: cannot use 'list' as a set element (unhashable type: 'list')`
# s = {1, [2, 3]}

# Set rỗng
empty_set = set() # set rỗng
empty_dict = {} # đây là dict rỗng, KHÔNG phải set

print(type(empty_set)) # <class 'set'>
print(type(empty_dict)) # <class 'dict'>

# Tạo set từ list/tuple/string
nums_list = [1, 2, 2, 3, 3, 3]
nums_set = set(nums_list)
print(nums_set) # {1, 2, 3}

text = "hello"
chars = set(text)
print(chars) # các ký tự không trùng lặp trong chuỗi


# ===== Thêm phần tử: `add()` và `update()` =====
fruits = {"apple", "banana"}
fruits.add("orange")
print(fruits) # {'apple', 'banana', 'orange'}

# update với nhiều phần tử (từ list, tuple, set khác, ...)
fruits.update(["mango", "banana"]) # 'banana' đã có nên không thêm trùng
print(fruits)


# ===== Xóa phần tử: `remove()` vs `discard()` =====
fruits = {"apple", "banana", "orange"}

fruits.remove("banana")
print(fruits) # {'apple', 'orange'}

# remove key không tồn tại => lỗi
# fruits.remove("mango") # KeyError

# discard an toàn hơn: không lỗi nếu không tồn tại
fruits.discard("mango") # không làm gì, không báo lỗi


# ===== Xóa phần tử: `pop()` & `clear()` =====
nums = {1, 2, 3}
value = nums.pop()
print(value) # lấy ra 1 phần tử "ngẫu nhiên"
print(nums)

nums.clear()
print(nums) # set() (rỗng)


# ===== Toán tử `in` với set =====
nums = {1, 2, 3, 4, 5}

print(3 in nums) # True
print(10 in nums) # False


# ===== Duyệt set bằng vòng lặp =====
fruits = {"apple", "banana", "orange"}

for f in fruits:
    print(f)


# ===== Các phép toán tập hợp thường dùng =====
A = {1, 2, 3, 4}
B = {3, 4, 5, 6}

# Hợp (union)
print(A | B) # {1, 2, 3, 4, 5, 6}
print(A.union(B)) # {1, 2, 3, 4, 5, 6}

# Giao (intersection)
print(A & B) # {3, 4}
print(A.intersection(B)) # {3, 4}

# Hiệu (difference)
print(A - B) # {1, 2} (trong A nhưng không trong B)
print(B - A) # {5, 6}

print(A.difference(B)) # {1, 2}

# Hiệu đối xứng (symmetric difference)
print(A ^ B) # {1, 2, 5, 6}
print(A.symmetric_difference(B)) # {1, 2, 5, 6}

# Quan hệ tập con / tập cha
A = {1, 2}
B = {1, 2, 3, 4}

print(A.issubset(B)) # True (A là tập con của B)
print(B.issuperset(A)) # True (B là tập cha của A)

C = {3, 4}
D = {1, 2}
print(C.isdisjoint(D)) # True (không có phần tử chung)


# ===== loại bỏ trùng lặp và sắp xếp lại =====
nums = [5, 1, 2, 5, 3, 2, 4]
unique_sorted = sorted(set(nums))
print(unique_sorted) # [1, 2, 3, 4, 5]
