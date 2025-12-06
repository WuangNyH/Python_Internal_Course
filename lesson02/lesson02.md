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

> `dict` (dictionary) là cấu trúc dữ liệu lưu trữ **các cặp `key: value`**.

* `key` (khóa):

  * Thường là `str`, `int` hoặc kiểu **bất biến** (immutable) như `tuple`
  * Không được trùng nhau trong cùng một dict
* `value` (giá trị): có thể là **bất kỳ kiểu dữ liệu** nào

Ví dụ đơn giản:

```python
student = {
    "name": "Nguyen Van A",
    "age": 20,
    "course": "Python Core",
}

print(student["name"])  # Nguyen Van A
print(student["age"])   # 20
```

> Dictionary rất phù hợp để biểu diễn **thông tin có nhãn**: thông tin người dùng, cấu hình, mapping từ mã sang nội dung,…

---

### 3.2 Khởi tạo dictionary

#### 3.2.1 Dùng cặp `key: value` trong ngoặc nhọn

```python
empty_dict = {}

student = {
    "name": "Nguyen Van A",
    "age": 20,
    "is_active": True,
}
```

#### 3.2.2 Dùng hàm `dict()`

```python
user = dict(name="An", age=25)
print(user)  # {'name': 'An', 'age': 25}
```

* Lưu ý: cách này chỉ dùng được khi `key` là chuỗi **hợp lệ như tên biến** (không có khoảng trắng, ký tự đặc biệt,…)

#### 3.2.3 Từ list/tuple các cặp 2 phần tử

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

* Nếu `key` không tồn tại → `KeyError`:

```python
print(student["address"])  # KeyError: 'address'
```

#### 3.3.2 Truy cập an toàn bằng `get()`

```python
print(student.get("name"))      # An
print(student.get("address"))   # None
print(student.get("address", "N/A"))  # N/A (giá trị mặc định)
```

> Khuyến khích dùng `get()` khi không chắc `key` có tồn tại hay không.

#### 3.3.3 Thêm mới / cập nhật

```python
student["age"] = 21           # cập nhật
student["address"] = "Hanoi"  # thêm mới

print(student)
# {'name': 'An', 'age': 21, 'address': 'Hanoi'}
```

* Nếu `key` đã tồn tại → bị **ghi đè** giá trị cũ.

---

### 3.4 Xóa phần tử trong dictionary

#### 3.4.1 Dùng `del`

```python
student = {"name": "An", "age": 20, "city": "Danang"}

del student["city"]
print(student)  # {'name': 'An', 'age': 20}
```

* Nếu `key` không tồn tại → `KeyError`.

#### 3.4.2 Dùng `pop()`

```python
age = student.pop("age")
print(age)      # 20
print(student)  # {'name': 'An'}
```

* Có thể truyền giá trị mặc định để tránh lỗi:

```python
city = student.pop("city", "Unknown")
print(city)  # Unknown
```

#### 3.4.3 Xóa toàn bộ

```python
student.clear()
print(student)  # {}
```

---

### 3.5 Duyệt dictionary

Cho dict mẫu:

```python
student = {
    "name": "Nguyen Van A",
    "age": 20,
    "city": "Danang",
}
```

#### 3.5.1 Duyệt theo key (mặc định)

```python
for key in student:
    print(key, "=>", student[key])
```

#### 3.5.2 Duyệt `.keys()`, `.values()`, `.items()`

```python
# Lấy danh sách key
print(student.keys())    # dict_keys(['name', 'age', 'city'])

# Lấy danh sách value
print(student.values())  # dict_values(['Nguyen Van A', 20, 'Danang'])

# Lấy cặp (key, value)
print(student.items())
# dict_items([('name', 'Nguyen Van A'), ('age', 20), ('city', 'Danang')])
```

Duyệt với `items()`:

```python
for key, value in student.items():
    print(key, ":", value)
```

---

### 3.6 Toán tử `in` với dict

* Kiểm tra **key** có tồn tại hay không:

```python
student = {"name": "An", "age": 20}

print("name" in student)   # True
print("address" in student)  # False
```

> Lưu ý: `in` kiểm tra **key**, không kiểm tra value.

---

### 3.7 Gộp / cập nhật nhiều phần tử với `update()`

```python
student = {"name": "An", "age": 20}
extra = {"age": 21, "city": "Hanoi"}

student.update(extra)
print(student)
# {'name': 'An', 'age': 21, 'city': 'Hanoi'}
```

* `age` bị cập nhật từ 20 → 21, `city` được thêm mới.

---

### 3.8 Dictionary lồng nhau (nested dict)

> Giá trị của dict có thể là **dict khác**.

Ví dụ: danh sách sinh viên, mỗi sinh viên là một dict:

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

print(students["SV01"]["name"])     # Nguyen Van A
print(students["SV02"]["scores"][1]) # 8.5
```

> Cần luyện tập truy cập theo tầng: `students["SV02"]["scores"][1]`.

---

### 3.9 Ứng dụng thực tế của dictionary

* Lưu thông tin cấu hình: `config["db_host"]`, `config["timeout"]`, …
* Mapping mã → nội dung:

```python
error_messages = {
    404: "Not Found",
    500: "Internal Server Error",
}
```

* Đếm tần suất xuất hiện (word count, name count,…)
* Biểu diễn JSON khi làm việc với API (vì JSON rất giống dict trong Python)

---

### 3.10 So sánh nhanh List vs Dict

| Tiêu chí        | List                          | Dict                                    |
| --------------- | ----------------------------- | --------------------------------------- |
| Cách truy cập   | Dùng **index** (0, 1, 2,…)    | Dùng **key** (chuỗi, số, tuple,…)       |
| Thứ tự          | Có thứ tự theo index          | Python 3.7+ giữ thứ tự insert (thực tế) |
| Dùng khi        | Dữ liệu dạng danh sách, mảng  | Dữ liệu có nhãn, cần truy cập theo tên  |
| Ví dụ điển hình | Danh sách điểm, danh sách tên | Thông tin user, config, bản ghi dữ liệu |

> Quy tắc đơn giản: **Nếu bạn muốn truy cập bằng số thứ tự → dùng list. Nếu muốn truy cập bằng tên/nhãn → dùng dict.**

---

### 3.11 Thực hành về Dictionary

#### BTTH7: Từ thông tin sinh viên

```python
student = {
    "name": "Nguyen Van A",
    "age": 20,
    "scores": [7.5, 8.0, 6.5, 9.0],
}
```

Yêu cầu:

1. In ra tên và tuổi của sinh viên theo format:

```text
Name : Nguyen Van A
Age  : 20
```

2. Tính điểm trung bình từ `scores` và thêm vào dict với key `"avg_score"`.
3. In lại toàn bộ dict sau khi thêm.

---

#### BTTH8: Đếm tần suất xuất hiện chữ cái

Cho chuỗi:

```python
s = "hello world"
```

* Hãy tạo một dict `counter` sao cho:

```python
{
  'h': 1,
  'e': 1,
  'l': 3,
  'o': 2,
  ' ': 1,
  'w': 1,
  'r': 1,
  'd': 1
}
```

Gợi ý:

```python
counter = {}
for ch in s:
    # nếu ch chưa có trong dict, gán = 1
    # nếu ch đã có, tăng lên 1
```

---

#### BTTH9: Quản lý danh sách sinh viên bằng dict

* Tạo dict `students` như sau:

```python
students = {
    "SV01": {"name": "Nguyen Van A", "age": 20},
    "SV02": {"name": "Tran Thi B", "age": 21},
}
```

Yêu cầu:

1. Thêm sinh viên mới `SV03` với tên và tuổi bất kỳ.
2. Cập nhật tuổi của `SV01` tăng thêm 1.
3. Duyệt `students` và in ra theo format:

```text
SV01: Nguyen Van A (20)
SV02: Tran Thi B (21)
SV03: ...
```

---

> Sau phần Dictionary, học viên cần nắm được:
>
> * Khái niệm cặp key–value
> * Cách tạo dict, truy cập, thêm/xóa/cập nhật phần tử
> * Cách duyệt dict với `keys()`, `values()`, `items()`
> * Ứng dụng thực tế: lưu thông tin, mapping, đếm tần suất
> * Phân biệt khi nào dùng list, khi nào dùng dict.
