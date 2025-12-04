# Python Core – Buổi 2: Cấu trúc dữ liệu (List – Tuple – Dict – Set) & Debug

## 1) List – Danh sách trong Python

### 1.1 Khái niệm

> List là một trong những cấu trúc dữ liệu quan trọng nhất trong Python

* Đặc điểm của List:
  * Có thứ tự => mỗi phần tử có index
  * Thay đổi được (mutable) => có thể thêm, xóa, sửa phần tử
  * Chứa được mọi kiểu dữ liệu, kể cả list khác (list lồng list)
  * Duyệt rất dễ bằng vòng lặp

* Khởi tạo list:

```python
numbers = [1, 2, 3, 4, 5]
mixed = [1, "hello", True, 3.14]
empty = []
```

---

### 1.2 Truy cập phần tử

> Python dùng cú pháp `list[index]`

* Index dương (tính từ trái sang phải)

```python
fruits = ["apple", "banana", "orange"]
print(fruits[0]) # apple
print(fruits[2]) # orange
```

* Index âm (tính từ phải sang trái)

```python
fruits = ["apple", "banana", "orange"]
print(fruits[-1]) # orange
print(fruits[-2]) # banana
```
* Lỗi thường gặp

```python
fruits = ["apple", "banana", "orange"]
print(fruits[10])  
# IndexError: list index out of range
```

---

### 1.3 Cắt list

* Cú pháp: `list[start:end]` lấy từ `start` đến `end-1`

```python
numbers = [10, 20, 30, 40, 50]

print(numbers[1:4]) # [20, 30, 40]
print(numbers[:3]) # [10, 20, 30]
print(numbers[2:]) # [30, 40, 50]
print(numbers[:]) # copy list
print(numbers[::2]) # [10, 30, 50] => bỏ qua 1 phần tử
print(numbers[::-1]) # đảo list
```

---

### 1.4 Thay đổi phần tử

* List là mutable, khác string (immutable)

```python
nums = [1, 2, 3]
nums[1] = 100
print(nums) # [1, 100, 3]
```

---

### 1.5 Thêm phần tử

* `append()`: Thêm cuối list
* `insert()`: Chèn vào vị trí bất kỳ
* `extend()`: Nối 2 list

---

### 1.6 Xóa phần tử

* `remove(value)`: Xóa theo giá trị
* `pop(index)`: Xóa theo vị trí (và trả về phần tử)
  * `pop()`: không truyền index => xóa phần tử cuối.
* `del`: Xóa phần tử hoặc xóa cả list

---

### 1.7 Tìm kiếm trong list

```python
colors = ["red", "green", "blue"]
print("green" in colors) # True
print("yellow" in colors) # False
```

---

### 1.8 Các hàm built-in thường dùng

```python
nums = [4, 7, 1, 9]

print(len(nums)) # số phần tử
print(sum(nums)) # tổng
print(sorted(nums)) # trả về list mới đã sort
```

* Sắp xếp tại chỗ: `nums.sort()`

---

### 1.9 Duyệt list

* Duyệt phần tử:

```python
nums = [4, 7, 1, 9]
for x in nums:
    print(x)
```

* Duyệt theo index:

```python
nums = [4, 7, 1, 9]
for i in range(len(nums)):
    print(i, nums[i])
```

* Duyệt index + value bằng `enumerate()` (vừa lấy index, vừa value):

```python
nums = [4, 7, 1, 9]
for i, value in enumerate(nums, start=1):
    print(i, value)
```

> `enumerate()` giúp lấy cả chỉ số (index) và giá trị (value) cùng lúc, mà không cần phải dùng `range(len())`

---

### 1.10 List comprehension: Cách viết list gọn

> Là cú pháp cho phép tạo list mới bằng một dòng ngắn gọn, thay thế cho cách viết vòng lặp kiểu truyền thống

* Cấu trúc cơ bản: [expression `for` element `in` iterable `if` condition]
  * `expression`: biểu thức tạo ra phần tử mới
  * `element`: biến đại diện cho từng phần tử trong `iterable`
  * `iterable`: list, string, range, tuple, ...

* Ví dụ

```python
nums = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]

# Cách truyền thống
new_list = []
for n in nums:
    new_list.append(n + 1)

# Tăng mỗi số lên 1
new_list = [n + 1 for n in nums]
print(new_list)

# Lọc phần tử theo điều kiện
evens = [x for x in nums if x % 2 == 0]
print(evens) # [0, 2, 4, 6, 8]

# Nested list comprehension
pairs = [(x, y) for x in [1, 2] for y in [3, 4]]
print(pairs) # [(1, 3), (1, 4), (2, 3), (2, 4)]
```

---

### 1.11 List lồng nhau (2D list)

```python
matrix = [
    [1, 2, 3],
    [4, 5, 6]
]

print(matrix[1][2]) # 6

# Duyệt 2 chiều
for row in matrix:
    for value in row:
        print(value, end=" ")
    print()
```

---

### 1.12 Lưu ý khi thao tác với list

* Copy list

```python
a = [1, 2, 3]
b = a
b[0] = 100
print(a) # bị thay đổi theo!

# Copy đúng cách
b = a.copy()
# hoặc 
b = a[:]
```

* Thay đổi list khi đang duyệt

```python
a = [1, 2, 3, 4]
for x in a:
    a.remove(x) # gây lỗi logic
```

Python duyệt list theo index nội bộ (0, 1, 2, ...)
=> Khi `remove(x)`, list bị thay đổi kích thước, phần tử bị dồn lại 
=> vòng lặp bị nhảy qua phần tử

Kết quả chỉ xóa 1 và 3 => trả về `[2, 4]`

Giải pháp: duyệt bản copy

```python
a = [1, 2, 3, 4]
for x in a[:]: # dùng bản copy
    a.remove(x)
```

---

### 1.13 Thực hành nhanh về list

#### BTTH1: Cho list điểm `scores = [7.5, 8.0, 6.5, 9.0, 8.5]`

* Hãy tính
  * điểm trung bình
  * điểm cao nhất
  * điểm thấp nhất

* Tính bằng 2 cách:
    * Tự duyệt list
    * Dùng hàm built-in

#### BTTH2: Xóa tất cả số âm khỏi list

* `nums = [5, -2, 8, -1, 0, 3, -10]` => `[5, 8, 0, 3]`

#### BTTH3: Làm phẳng list lồng nhau

* `[[1,2,3],[4,5],[6]]` => `[1,2,3,4,5,6]`