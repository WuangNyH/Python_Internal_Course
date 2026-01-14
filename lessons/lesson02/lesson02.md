# Python Core – Buổi 2: Cấu trúc dữ liệu (List – Tuple – Dict – Set) & Debug

## 1) List - Danh sách trong Python

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

### 1.3 Cắt (slicing) list

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

* `remove(value)`: Xóa phần tử đầu tiên theo giá trị
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

* Khái niệm built-in
  * Là những hàm, kiểu dữ liệu, hằng số, exception, ...
  * Được tích hợp sẵn trong Python (cấp ngôn ngữ), dùng ngay mà không cần import

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

* Duyệt song song nhiều list bằng `zip()`:

Khi cần duyệt nhiều list cùng lúc (ví dụ: tên + tuổi, môn + điểm, ...), `zip()` giúp ghép các list lại với nhau để duyệt song song:

```python
students = ["A", "B", "C", "D"]
math = [9.0, 7.5, 8.0]
english = [8.5, 6.0, 9.0]

for s, m, e in zip(students, math, english):
    print(s, m, e)
```
  
**Lưu ý**: `zip()` sẽ dừng khi `list` ngắn nhất kết thúc

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

* Truy cập index không tồn tại => ném `IndexError`

* Dùng `remove()` cho phần tử không tồn tại => ném `ValueError`

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

---

## 2) Tuple – Bộ các giá trị bất biến

### 2.1 Khái niệm

> Tuple gần giống `list`, nhưng **bất biến (immutable)** => sau khi tạo ra **không thể sửa được** từng phần tử bên trong

* Đặc điểm của tuple:

  * Có thứ tự => mỗi phần tử có `index` giống `list`
  * **Immutable** => không cho phép gán lại `tuple[index] = value`
  * Chứa được mọi kiểu dữ liệu: số, chuỗi, list, tuple khác, ...
  * Thường dùng để:
    * Nhóm các giá trị cố định (như toạ độ, ngày tháng, ...)
    * Trả về nhiều giá trị từ một hàm
    * Làm **key** cho `dict` (vì `tuple` là immutable, còn `list` thì không)

```python
point = (10, 20)
print(point[0]) # 10
print(point[1]) # 20
```

---

### 2.2 Khởi tạo tuple

#### 2.2.1 Tuple nhiều phần tử

```python
nums = (1, 2, 3)
colors = ("red", "green", "blue")
mixed = (1, "hello", True, 3.14)
```

* Có thể bỏ ngoặc tròn trong một số trường hợp, Python sẽ tự hiểu là tuple:

```python
nums = 1, 2, 3  # vẫn là tuple
print(type(nums))  # <class 'tuple'>
```

#### 2.2.2 Tuple rỗng

```python
empty = ()
```

#### 2.2.3 Tuple 1 phần tử (LƯU Ý DẤU PHẨY)

> Dễ nhầm giữa `()` dùng cho `tuple` và toán tử / group biểu thức

```python
x = (5) # KHÔNG phải tuple, chỉ là số 5
x_tuple = (5,) # Đây mới là tuple 1 phần tử

print(type(x)) # <class 'int'>
print(type(x_tuple)) # <class 'tuple'>
```

* **Quy tắc:** `tuple` 1 phần tử **bắt buộc phải có dấu phẩy** ở cuối

---

### 2.3 Truy cập phần tử trong tuple

* Cú pháp giống list: `tuple[index]`

```python
fruits = ("apple", "banana", "orange")

print(fruits[0]) # apple
print(fruits[2]) # orange
print(fruits[-1]) # orange (index âm từ phải sang trái)
```

* Nếu truy cập index không tồn tại => `IndexError` giống `list`:

```python
fruits = ("apple", "banana", "orange")
print(fruits[10])  # IndexError: tuple index out of range
```

---

### 2.4 Slicing với tuple

> Slicing hoạt động y hệt `list`, chỉ khác là kết quả trả về cũng là một `tuple` mới

```python
nums = (10, 20, 30, 40, 50)

print(nums[1:4]) # (20, 30, 40)
print(nums[:3]) # (10, 20, 30)
print(nums[2:]) # (30, 40, 50)
print(nums[::2]) # bước nhảy 2 => (10, 30, 50)
print(nums[::-1]) # nghịch đảo => (50, 40, 30, 20, 10)
```

* Vì `tuple` immutable, mọi thao tác slice đều tạo **`tuple` mới**, không thay đổi `tuple` cũ

---

### 2.5 Tuple là immutable: không sửa được phần tử

```python
nums = (1, 2, 3)
nums[1] = 100  # TypeError: 'tuple' object does not support item assignment
```

* Không thể:
  * Thay đổi giá trị phần tử: `nums[0] = ...`
  * Thêm phần tử: không có `append`, `insert`
  * Xóa phần tử: không có `remove`, `pop`

* Nhưng có thể **tạo tuple mới** từ tuple cũ:

```python
nums = (1, 2, 3)
nums2 = nums + (4, 5)
print(nums2)  # (1, 2, 3, 4, 5)
```

> Tư duy: `tuple` giống như một “gói dữ liệu cố định” => chỉ dùng, không thay đổi bên trong

---

### 2.6 Unpacking: Bóc tách tuple thành nhiều biến

> `Unpacking` là kỹ thuật gán từng phần tử của tuple vào từng biến tương ứng

```python
point = (10, 20)
x, y = point

print(x)  # 10
print(y)  # 20
```

* Số biến (vế trái) phải **khớp** với số phần tử trong tuple:

```python
p = (1, 2, 3)
a, b, c = p # OK
# a, b = p # ValueError: too many values to unpack
```

#### 2.6.1 Unpacking với `_`: bỏ bớt giá trị không dùng

```python
student = ("Taro", 20, "Tokyo")
name, age, _ = student  # bỏ qua city

print(name, age)  # Taro 20
```

#### 2.6.2 Unpacking với `*`: gom phần còn lại

```python
nums = (1, 2, 3, 4, 5)
first, *middle, last = nums

print(first) # 1
print(middle) # [2, 3, 4]
print(last) # 5
```

> `*middle` sẽ nhận “phần còn lại” dưới dạng `list`

---

### 2.7 Dùng tuple để trả về nhiều giá trị từ hàm

> Là **use case quan trọng** của tuple

```python
def get_min_max(numbers: list[float]) -> tuple[float, float]:
    minimum = min(numbers)
    maximum = max(numbers)
    return minimum, maximum  # Python tự gói thành tuple

scores = [7.5, 8.0, 6.5, 9.0, 8.5]
min_score, max_score = get_min_max(scores)

print("Min:", min_score)
print("Max:", max_score)
```

* Bên trong hàm: `return minimum, maximum` thực ra trả về một tuple `(minimum, maximum)`
* Bên ngoài: dùng unpacking `min_score, max_score = ...` để gán từng phần

---

### 2.8 Dùng tuple làm key cho dict

> Vì tuple là immutable => có thể dùng làm **key** trong `dictionary`, trong khi `list` thì không

Ví dụ: dùng `tuple` làm key ghép nhiều thông tin (first_name, last_name):

```python
students = {}

key1 = ("Nguyen", "An")
key2 = ("Tran", "Binh")

students[key1] = 8.5
students[key2] = 9.0

print(students[("Nguyen", "An")])  # 8.5
```

* Nếu dùng list làm key sẽ bị lỗi:

```python
key = ["Nguyen", "An"]
my_dict = {key: 8.5}  # TypeError: cannot use 'list' as a dict key (unhashable type: 'list')
```

---

### 2.9 Một số hàm & thao tác thường dùng với tuple

Dù immutable nhưng `tuple` vẫn dùng được khá nhiều thao tác giống `list`:

```python
nums = (4, 7, 1, 9)

print(len(nums)) # 4
print(min(nums)) # 1
print(max(nums)) # 9
print(sum(nums)) # 21
print(sorted(nums)) # [1, 4, 7, 9]  (trả về LIST mới => ko thay đổi nums)

# duyệt tuple
for x in nums:
    print(x)

# duyệt index + value
for i, value in enumerate(nums):
    print(i, value)

# duyệt tuple song song với zip()
a = (1, 2, 3)
b = ("A", "B", "C")

for x, y in zip(a, b):
    print(x, y)
```

> Lưu ý: `sorted(nums)` là 1 hàm built-in trả về `list`, **không phải** `tuple`

---

### 2.10 Khi nào dùng tuple, khi nào dùng list?

* Dùng `tuple` khi:
  * Bộ các giá trị mang ý nghĩa như một "bản ghi" cố định, không đổi:
    * Toạ độ `(x, y)`
    * Ngày tháng `(year, month, day)`
    * Màu RGB `(r, g, b)`
  * Trả về nhiều giá trị từ hàm
  * Dùng làm `key` trong `dictionary`

* Dùng `list` khi:
  * Dữ liệu có thể thay đổi (thêm / xóa / sửa)
  * Cần nhiều method thao tác: `append`, `insert`, `remove`, ...
  * Sử dụng nhiều thao tác `sort`, `filter`, `list comprehension`, ...

> Quy tắc cần nhớ: 
> Nếu dữ liệu là “cố định” theo ý nghĩa logic => ưu tiên `tuple` 
> Nếu dữ liệu “động”, có thể thay đổi => dùng `list`

---

### 2.11 Thực hành nhanh về tuple

#### BTTH4: Unpacking tuple

```python
student_info = ("Nguyen Van A", 20, "Python Core")
```

* Hãy unpacking tuple trên thành 3 biến: `name`, `age`, `course` và in ra theo dạng:

```text
Name : Nguyen Van A
Age : 20
Course: Python Core
```

---

#### BTTH5: Hàm trả về nhiều giá trị

* Cho danh sách `scores = [7.5, 8.0, 6.5, 9.0, 8.5]`

* Viết hàm `calculate_stats(scores: list[float]) -> tuple[float, float, float]` trả về:
  * điểm trung bình
  * điểm nhỏ nhất
  * điểm lớn nhất

---

#### BTTH6: Danh sách học viên (Kết hợp list + tuple)

* Cho danh sách học viên, mỗi phần tử là một `tuple` gồm 3 giá trị: `(name, age, score)`:

```python
students = [
    ("Nguyen Van A", 20, 8.5),
    ("Tran Thi B", 19, 7.0),
    ("Le Van C", 21, 9.0),
]
```

* a. Dùng vòng lặp `for` + `unpacking tuple` để in ra từng học viên theo format `Name: ..., Age: ..., Score: ...`
* b. Tạo một list mới `scores` chỉ chứa điểm số của học viên, bằng:
  * Cách 1: dùng vòng lặp `for` bình thường
  * Cách 2: dùng `list comprehension `với `unpacking tuple`
* c. Tìm học viên có điểm cao nhất, in ra `Top student: <name>, Score: <score>`

---

## 3) Dictionary (cặp key–value)

### 3.1 Khái niệm

> `dict` (dictionary) là cấu trúc dữ liệu lưu trữ các cặp `key: value`

* Khóa `key`:
  * Thường là `str`, `int` hoặc kiểu **bất biến** (immutable) như `tuple`
  * `key` **không** được trùng nhau trong cùng một `dict`
* `value` (giá trị): có thể là **bất kỳ kiểu dữ liệu** nào

* Ví dụ:

```python
student = {
    "name": "Nguyen Van A",
    "age": 20,
    "course": "Python Core",
}

print(student["name"]) # Nguyen Van A
print(student["age"]) # 20
```

* `dict` rất phù hợp để biểu diễn **thông tin có nhãn**: thông tin người dùng, mapping từ mã sang nội dung, ...

```python
status = {
    "A": "Đang học",
    "P": "Tạm nghỉ",
    "G": "Đã tốt nghiệp",
}

print(status["G"])  # Đã tốt nghiệp
```

---

### 3.2 Khởi tạo dictionary

#### 3.2.1 Dùng cặp `key: value` trong ngoặc nhọn

```python
empty_dict = {}

student = {
    "name": "Nguyen Van A",
    "age": 20
}
```

#### 3.2.2 Dùng hàm `dict()`

```python
user = dict(name="An", age=25)
print(user)  # {'name': 'An', 'age': 25}
```

* Lưu ý: cách này chỉ dùng được khi `key` là chuỗi **hợp lệ như tên biến** (không có khoảng trắng, ký tự đặc biệt, ...)

#### 3.2.3 Từ `list`/`tuple` các cặp 2 phần tử

```python
pairs = [("a", 1), ("b", 2), ("c", 3)]
my_dict = dict(pairs)
print(my_dict)  # {'a': 1, 'b': 2, 'c': 3}
```

---

### 3.3 Truy cập & cập nhật giá trị

#### 3.3.1 Truy cập bằng `[]`

```python
student = {"name": "An", "age": 20}
print(student["name"])  # An
```

* Nếu `key` không tồn tại => `KeyError`:

```python
student = {"name": "An", "age": 20}
print(student["address"])  # KeyError: 'address'
```

#### 3.3.2 Truy cập an toàn bằng `get()`

```python
student = {"name": "An", "age": 20}
print(student.get("name")) # An
print(student.get("address")) # None

# Fallback trả giá trị mặc định
user = dict(name="An", age=25)
print(user.get("email", "N/A")) # nếu thiếu, mặc định là N/A
print(user.get("active", False))
```

> Best practice: Dùng `get()` khi không chắc `key` có tồn tại hay không

#### 3.3.3 Thêm mới / cập nhật

```python
student = {"name": "An", "age": 20}
student["age"] = 21 # cập nhật
student["address"] = "Hanoi" # thêm mới

print(student) # {'name': 'An', 'age': 21, 'address': 'Hanoi'}
```

* Nếu `key` đã tồn tại => sẽ **ghi đè** giá trị cũ

---

### 3.4 Xóa phần tử trong dictionary

#### 3.4.1 Dùng `del`

```python
student = {"name": "An", "age": 20, "city": "Danang"}

del student["city"]
print(student)  # {'name': 'An', 'age': 20}
```

* Nếu `key` không tồn tại => `KeyError`

#### 3.4.2 Dùng `pop()`: xóa và trả về giá trị 

```python
student = {"name": "An", "age": 20, "city": "Danang"}

age = student.pop("age")
print(age) # 20
print(student)  # {'name': 'An', 'city': 'Danang'}
```

* Có thể truyền giá trị mặc định để tránh lỗi:

```python
student = {"name": "An", "age": 20, "city": "Danang"}

city = student.pop("city", "Unknown")
print(city)  # Unknown
```

#### 3.4.3 Xóa toàn bộ

```python
student = {"name": "An", "age": 20, "city": "Danang"}
student.clear()
print(student)  # {}
```

---

### 3.5 Duyệt dictionary

#### 3.5.1 Duyệt theo key (mặc định)

```python
student = {
    "name": "Nguyen Van A",
    "age": 20,
    "city": "Danang",
}

for key in student:
    print(key, "=>", student[key])
```

#### 3.5.2 Duyệt `.keys()`, `.values()`, `.items()`

```python
student = {
    "name": "Nguyen Van A",
    "age": 20,
    "city": "Danang",
}

# Lấy danh sách key
print(student.keys()) # dict_keys(['name', 'age', 'city'])

# Lấy danh sách value
print(student.values()) # dict_values(['Nguyen Van A', 20, 'Danang'])

# Lấy cặp (key, value)
print(student.items())
# dict_items([('name', 'Nguyen Van A'), ('age', 20), ('city', 'Danang')])

# Duyệt với `items()`
for key, value in student.items():
    print(key, ":", value)
```

---

### 3.6 Toán tử `in` với dict

* Kiểm tra `key` có tồn tại hay không:

```python
student = {"name": "An", "age": 20}

print("name" in student) # True
print("address" in student) # False
```

> Lưu ý: `in` kiểm tra `key`, **không** kiểm tra `value`

---

### 3.7 Gộp / cập nhật nhiều phần tử với `update()`

```python
student = {"name": "An", "age": 20}
extra = {"age": 21, "city": "Danang"}

student.update(extra)
student.update(hobby="football")
print(student) # {'name': 'An', 'age': 21, 'city': 'Danang', 'hobby': 'football'}
```

* `age` bị cập nhật từ 20 → 21, `city` được thêm mới

---

### 3.8 Dictionary lồng nhau (nested dict)

> Giá trị của dict có thể là **dict khác**

* Ví dụ: danh sách sinh viên, mỗi sinh viên là một `dict`:

```python
students = {
    "SV01": {
        "name": "Nguyen Van A",
        "age": 20,
        "scores": [8.0, 7.5, 9.0],
    },
    "SV02": {
        "name": "Tran Thi B",
        "age": 21,
        "scores": [7.0, 8.5, 8.0],
    },
}

print(students.get("SV01").get("name")) # Nguyen Van A
print(students.get("SV02").get("scores")[1]) # 8.5
```

> Trong thực tế `Nested dict` được dùng rất nhiều 
> => cần làm quen với truy cập theo tầng: `students.get("key1").get("key2")[index]`

---

### 3.9 Ứng dụng thực tế của dictionary

* Lưu thông tin cấu hình: `config["db_host"]`, `config["timeout"]`, ...
* Mapping mã thành nội dung
* Đếm tần suất xuất hiện (word count, name count,…)
* Biểu diễn JSON khi làm việc với API (vì JSON rất giống dict trong Python)

---

### 3.10 So sánh nhanh List vs Dict

| Tiêu chí        | List                          | Dict                                    |
|-----------------|-------------------------------|-----------------------------------------|
| Cách truy cập   | Dùng `index` (0, 1, 2, ...)   | Dùng `key` (chuỗi, số, tuple, ...)      |
| Thứ tự          | Có thứ tự theo `index`        | Giữ thứ tự insert thực tế               |
| Dùng khi        | Dữ liệu dạng danh sách, mảng  | Dữ liệu có nhãn, cần truy cập theo tên  |
| Ví dụ điển hình | Danh sách điểm, danh sách tên | Thông tin user, config, bản ghi dữ liệu |

> Quy tắc đơn giản: 
> * Nếu muốn truy cập bằng số thứ tự => dùng `list`
> * Nếu muốn truy cập bằng tên/nhãn => dùng `dict`

---

### 3.11 Thực hành về Dictionary

#### BTTH7: Thông tin sinh viên

* Cho `dict` sau:

```python
from typing import Any

student: dict[str, Any] = {
    "name": "Nguyen Van A",
    "age": 20,
    "scores": [7.5, 8.0, 6.5, 9.0],
}
```

* Yêu cầu:
  * a. In ra tên và tuổi của sinh viên theo format:
    ```text
    Name : Nguyen Van A
    Age : 20
    ```

  * b. Tính điểm trung bình từ `scores` và thêm vào dict với key `"avg_score"`

---

#### BTTH8: Đếm tần suất xuất hiện ký tự

* Cho chuỗi `s = "hello world"`
* Hãy tạo một dict `counter` để đếm số lần xuất hiện ký tự trong chuỗi `s`
  * Kết quả:
  ```
  {'h': 1, 'e': 1, 'l': 1, 'o': 1, ' ': 1, 'w': 1, 'r': 1, 'd': 1}
  ```

---

#### BTTH9: Quản lý danh sách sinh viên bằng dict

* Cho dict `students` như sau:

```python
from typing import Any

students: dict[str, dict[str, Any]] = {
    "SV01": {"name": "Nguyen Van A", "age": 20},
    "SV02": {"name": "Tran Thi B", "age": 21},
}
```

* Yêu cầu:
* a. Thêm sinh viên mới `SV03` với tên và tuổi bất kỳ
* b. Cập nhật tuổi của `SV01` tăng thêm 1
* c. Duyệt `students` và in ra theo format:
  ```text
  SV01: Nguyen Van A (20)
  SV02: Tran Thi B (21)
  SV03: ...  
  ```

---

## 4) Set – Tập hợp không trùng lặp

### 4.1 Khái niệm

> `set` là cấu trúc dữ liệu lưu trữ các phần tử **không trùng lặp**, **không quan tâm thứ tự**

* Đặc điểm của `set`:
  * Không có thứ tự => không truy cập được bằng `index` như `list`
  * Không chứa phần tử trùng lặp
  * Các phần tử bên trong phải là **immutable**
    * `int`, `float`, `str`, `tuple` => OK
    * 'list', 'dict', `set` => NG
      * Ví dụ `s = {[1, 2, 3]}` =>  lỗi `TypeError: cannot use 'list' as a set element (unhashable type: 'list')`
  * `set` **mutable** => có thể thêm/xóa phần tử

```python
numbers = {1, 2, 3, 3, 4}
print(numbers) # {1, 2, 3, 4} (3 chỉ xuất hiện 1 lần)
```

> Thường dùng `set` khi cần **loại bỏ trùng lặp** hoặc làm các phép toán tập hợp (hợp, giao, hiệu, ...)

---

### 4.2 Khởi tạo set

#### 4.2.1 Dùng ngoặc nhọn `{}`

```python
nums = {1, 2, 3}
characters = {"a", "b", "c"}
mixed = {1, "hello", (2, 3)}
```

> Lưu ý: Không được dùng list/dict làm phần tử set vì chúng **mutable**:

```python
# Lỗi `TypeError: cannot use 'list' as a set element (unhashable type: 'list')`
s = {1, [2, 3]}
```

#### 4.2.2 Set rỗng

* Lưu ý KHÔNG dùng `{}` cho `set` rỗng

```python
empty_set = set() # set rỗng
empty_dict = {} # đây là dict rỗng, KHÔNG phải set

print(type(empty_set)) # <class 'set'>
print(type(empty_dict)) # <class 'dict'>
```

#### 4.2.3 Tạo set từ list/tuple/string

```python
nums_list = [1, 2, 2, 3, 3, 3]
nums_set = set(nums_list)
print(nums_set) # {1, 2, 3}

text = "hello"
chars = set(text)
print(chars) # các ký tự không trùng lặp trong chuỗi
```

---

### 4.3 Thêm & xóa phần tử trong set

#### 4.3.1 Thêm phần tử: `add()` và `update()`

```python
fruits = {"apple", "banana"}
fruits.add("orange")
print(fruits) # {'apple', 'banana', 'orange'}

# update với nhiều phần tử (từ list, tuple, set khác, ...)
fruits.update(["mango", "banana"]) # 'banana' đã có nên không thêm trùng
print(fruits)
```

#### 4.3.2 Xóa phần tử: `remove()` vs `discard()`

```python
fruits = {"apple", "banana", "orange"}

fruits.remove("banana")
print(fruits) # {'apple', 'orange'}

# remove key không tồn tại => lỗi
# fruits.remove("mango") # KeyError

# discard an toàn hơn: không lỗi nếu không tồn tại
fruits.discard("mango") # không làm gì, không báo lỗi
```

#### 4.3.3 `pop()` & `clear()`

```python
nums = {1, 2, 3}
value = nums.pop()
print(value) # lấy ra 1 phần tử "ngẫu nhiên"
print(nums)

nums.clear()
print(nums) # set() (rỗng)
```

> Vì set không có thứ tự nên `pop()` không đảm bảo lấy phần tử nào

---

### 4.4 Toán tử `in` với set

> Kiểm tra phần tử rất nhanh (tối ưu hơn list khi dữ liệu lớn)

```python
nums = {1, 2, 3, 4, 5}

print(3 in nums) # True
print(10 in nums) # False
```

---

### 4.5 Duyệt set bằng vòng lặp

```python
fruits = {"apple", "banana", "orange"}

for f in fruits:
    print(f)
```

> Thứ tự in ra có thể khác nhau giữa các lần chạy => **không dựa vào thứ tự của set**

---

### 4.6 Các phép toán tập hợp thường dùng

Cho trước A và B như sau:

```python
A = {1, 2, 3, 4}
B = {3, 4, 5, 6}
```

#### 4.6.1 Hợp (union)

```python
print(A | B) # {1, 2, 3, 4, 5, 6}
print(A.union(B)) # {1, 2, 3, 4, 5, 6}
```

#### 4.6.2 Giao (intersection)

```python
print(A & B) # {3, 4}
print(A.intersection(B)) # {3, 4}
```

#### 4.6.3 Hiệu (difference)

```python
print(A - B) # {1, 2} (trong A nhưng không trong B)
print(B - A) # {5, 6}

print(A.difference(B)) # {1, 2}
```

#### 4.6.4 Hiệu đối xứng (symmetric difference)

* Phần tử thuộc A hoặc B nhưng **không** thuộc cả hai

```python
print(A ^ B) # {1, 2, 5, 6}
print(A.symmetric_difference(B)) # {1, 2, 5, 6}
```

#### 4.6.5 Quan hệ tập con / tập cha

```python
A = {1, 2}
B = {1, 2, 3, 4}

print(A.issubset(B)) # True (A là tập con của B)
print(B.issuperset(A)) # True (B là tập cha của A)

C = {3, 4}
D = {1, 2}
print(C.isdisjoint(D)) # True (không có phần tử chung)
```

---

### 4.7 Ứng dụng thực tế của set

* Loại bỏ phần tử trùng lặp trong list
* Kiểm tra một phần tử có nằm trong tập cho phép không (whitelist/blacklist)
* Tìm phần giao/hợp giữa nhiều tập dữ liệu (học viên lớp A, lớp B, ...)
* Xử lý các bài toán toán học về tập hợp

Ví dụ: loại bỏ trùng lặp và sắp xếp lại:

```python
nums = [5, 1, 2, 5, 3, 2, 4]
unique_sorted = sorted(set(nums))
print(unique_sorted) # [1, 2, 3, 4, 5]
```

---

### 4.8 So sánh nhanh List – Tuple – Set

| Tiêu chí            | List                | Tuple                      | Set                                   |
|---------------------|---------------------|----------------------------|---------------------------------------|
| Thứ tự              | Có                  | Có                         | Không đảm bảo                         |
| Trùng lặp           | Cho phép            | Cho phép                   | Không cho phép                        |
| Khả năng thay đổi   | Có (mutable)        | Không (immutable)          | Có (mutable, nhưng phần tử immutable) |
| Truy cập            | Theo index          | Theo index                 | Không có index, duyệt bằng vòng lặp   |
| Trường hợp hay dùng | Danh sách có thứ tự | Bộ giá trị cố định/bản ghi | Loại bỏ trùng, phép toán tập hợp      |

---

### 4.9 Thực hành về Set

#### BTTH10: Loại bỏ trùng lặp trong list

* Cho list `nums = [1, 2, 2, 3, 4, 4, -1, 5]`
* Yêu cầu:
  * a. Dùng `set` để loại bỏ các số trùng lặp
  * b. Tạo lại một list mới `unique_nums` đã được **sắp xếp giảm dần**
* Kết quả mong muốn: `unique_nums = [5, 4, 3, 2, 1]`

---

#### BTTH11: Kiểm tra phần tử thuộc tập cho phép

* Cho các dữ liệu:

```python
allowed_roles = {"admin", "editor", "viewer"}
user_role = input("Nhap role nguoi dung: ")
```

* Yêu cầu: Viết đoạn code kiểm tra:
  * Chuẩn hóa dữ liệu input 
  * Nếu `user_role` thuộc `allowed_roles` => in ra `"Role hop le"`
  * Ngược lại => in ra `"Role khong hop le"`

---

#### BTTH12: Phân tích học viên giữa 2 lớp

* Cho 2 set mã học viên:

```python
class_A = {"SV01", "SV02", "SV03", "SV04"}
class_B = {"SV03", "SV04", "SV05"}
```

* Yêu cầu:
  * a. Tìm học viên học **cả 2 lớp** (giao)
  * b. Tìm học viên **chỉ học lớp A** (hiệu)
  * c. Tìm **tất cả học viên** (hợp) của 2 lớp
  * d. Tìm học viên **chỉ học 1 trong 2 lớp** (hiệu đối xứng)

---

## 5) Debug trong Python

### 5.1 Bug là gì? Debug là gì?

* **Bug**: lỗi trong chương trình khiến:
  * chương trình không chạy được, hoặc
  * chạy nhưng cho kết quả sai so với mong đợi
* **Debug** (gỡ lỗi): quá trình **tìm nguyên nhân** và **fix lỗi**

> Kỹ năng debug quan trọng **không kém** kỹ năng viết code, đặc biệt khi lượng code rất nhiều, có thể ảnh hưởng nhiều nơi 

---

### 5.2 Các loại lỗi thường gặp

#### 5.2.1 Lỗi cú pháp (SyntaxError)

Ví dụ:

```python
if x > 0
    print("x > 0")
```

* Thiếu dấu `:` => IDE báo lỗi ngay khi đang viết code
* Nếu vẫn cố chạy => Python báo `SyntaxError` ngay khi chạy

#### 5.2.2 Lỗi runtime (chạy chương trình mới lỗi)

* Ví dụ: chia cho 0

```python
x = 10
print(x / 0) # ZeroDivisionError: division by zero
```

* Ví dụ: truy cập sai index

```python
nums = [1, 2, 3]
print(nums[10])  # IndexError: list index out of range
```

#### 5.2.3 Lỗi logic (kết quả sai, không báo lỗi)

```python
# Tính trung bình nhưng quên chia cho số lượng phần tử
nums = [1, 2, 3]
avg = sum(nums) # sai logic
print(avg) # 6, đáng lẽ phải là 2.0
```

> Lỗi logic khó phát hiện hơn vì **chương trình vẫn chạy** nhưng kết quả không đúng

---

### 5.3 Cách đọc traceback (thông báo lỗi)

Ví dụ chạy code sau:

```python
nums = [1, 2, 3]
print(nums[5])
```

Python in ra dạng gần như:

```text
Traceback (most recent call last):
  File "debug_study.py", line 23, in <module>
    print(nums[5])
IndexError: list index out of range
```

* Dòng cuối cùng: **loại lỗi** và **mô tả** => `IndexError: list index out of range`
* Dòng trước đó: file, dòng code gây lỗi => `line 23, print(nums[5])`

> Khi thấy lỗi: **đọc từ dưới lên trên**, tìm dòng code của mình và xem đang truy cập gì sai

---

### 5.4 Debug bằng `print()`

* Đây là cách debug đơn giản nhất

Ví dụ: chương trình tính tổng số chẵn trong list nhưng ra kết quả sai:

```python
nums = [1, 2, 3, 4, 5]
result = 0
for n in nums:
    if n % 2 == 0:
        result = n # sai: lẽ ra phải result += n

print("result =", result)
```

* Cách debug:

```python
nums = [1, 2, 3, 4, 5]
result = 0
for n in nums:
    print("Dang xu ly n =", n) # in giá trị đang xử lý
    if n % 2 == 0:
        print("  -> n la so chan")
        result = n

print("result =", result)
```

* Quan sát log để xem code đang làm gì => phát hiện chỗ gán sai

> Quy tắc: khi nghi ngờ chỗ nào, hãy **in ra biến** hoặc **in ra checkpoint** (`print("Code already here")`) để xác định chương trình đã chạy đến đâu

---

### 5.5 Một số lỗi thường gặp với List / Tuple / Dict / Set

#### 5.5.1 `IndexError: list index out of range`

* Truy cập index không tồn tại trong list/tuple.

```python
nums = [10, 20, 30]
print(nums[3]) # sai, index hợp lệ: 0, 1, 2
```

#### 5.5.2 `KeyError` với dict

```python
student = {"name": "An"}
print(student["age"]) # KeyError: 'age'
```

* Cách an toàn:

```python
student = {"name": "An"}
age = student.get("age")  # None nếu không có
if age is None:
    print("Khong co thong tin tuoi")
```

#### 5.5.3 `TypeError` khi dùng sai kiểu

```python
nums = [1, 2, 3]
print(nums["1"]) # TypeError: list indices must be integers or slices, not str
```

---

### 5.6 Dùng Debugger trong PyCharm

> Phần này giới thiệu **khái niệm**, không cần đi quá sâu trong buổi 2

Các bước cơ bản khi dùng debugger (ví dụ trong VS Code):

1. Đặt **breakpoint** tại dòng cần dừng
2. Chạy chương trình ở chế độ debug
3. Khi chương trình dừng tại breakpoint, có thể:
   * Xem giá trị của biến ở panel Variables.
   * Dùng các nút:
     * **Step Over F8**: chạy từng dòng
     * **Step Into F7**: đi sâu vào hàm được gọi
     * **Step Out**: thoát ra khỏi hàm hiện tại
4. Quan sát giá trị biến thay đổi sau mỗi bước để tìm chỗ sai

