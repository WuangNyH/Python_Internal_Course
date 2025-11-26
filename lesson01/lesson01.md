# Python Core – Buổi 1: Cài đặt môi trường, tổng quan về Python, cấu trúc điều kiện

## 1) Cài đặt môi trường

### 1.1 Python & pip 

* Tải Python phiên bản 3.14 (hoặc version ổn định) từ python.org
* Khi cài nhớ chọn “Add Python to PATH” để cài đặt sẵn biến môi trường
* Kiểm tra cài đặt Python thành công trong Terminal

```bash
  py --version
  pip --version
```

### 1.2 PyCharm Community

* Tạo project mới: `PythonInternalCourse`
* Project = thư mục chứa nhiều file `.py`
* File `.py` = 1 chương trình / module
* Code convention: tên thư mục, file, biến, hàm nên đặt theo chuẩn PEP8: `snake_case`
  * Chỉ dùng chữ thường, số, _, không dấu, không khoảng trắng

## 2) Chương trình Python đầu tiên

* Tạo file hello.py:

```python
print("Hello, Techzen Academy!")
```

* Chạy chương trình
  * Run bằng IDE PyCharm (`shift + F10`)
  * Run bằng terminal: `python hello.py` hoặc `py hello.py`

> Hàm `print()`: dùng để in thông tin ra console

## 3) Tổng quan về Python: biến, kiểu dữ liệu, toán tử, nhập/xuất thông tin

### 3.1 Biến & kiểu dữ liệu cơ bản

* Biến: vùng nhớ lưu giá trị, không cần khai báo kiểu trước
* Quy tắc đặt tên biến:
  * Không bắt đầu bằng số, không chứa khoảng trắng, không dùng tiếng Việt có dấu
  * Ví dụ: `age`, `student_name`, `total_score`
* Kiểu dữ liệu cơ bản:
  * `int`: số nguyên
  * `float`: số thực
  * `str`: chuỗi
  * `bool`: `True`/`False`

```python
# hello.py
age = 20
height = 1.7
name = "Taro"
is_student = True

# In ra kiểu dữ liệu
print(type(age), type(height), type(name), type(is_student))
```

### 3.2 Toán tử cơ bản

* Số học: 
  * `+ - * /`
  * `//`: chia lấy nguyên
  * `%`: chia lấy dư
  * `**`: lũy thừa
* Gán: `=`, `+=`, `-=`, ...
* So sánh: `==`, `!=`, `>`, `<`, `>=`, `<=`
* Logic: `and`, `or`, `not`

### 3.3 Nhập & xuất dữ liệu

#### 3.3.1 Nhập từ bàn phím

Sử dụng `input()`: nó luôn trả về chuỗi => cần ép kiểu:

```python
# Nhập dữ liệu từ bàn phím
name = input("Nhập tên: ")
age = int(input("Nhập tuổi: ")) # cần ép sang int
```

#### 3.3.2 Xuất dữ liệu in ra console
  
* `print()` đơn giản
    
```python
name = input("Nhập tên: ")
age = int(input("Nhập tuổi: "))
# Xuất dữ liệu đơn giản
print("Xin chào", name, "- Bạn", age, "tuổi")
```  

* Dùng f-string: 
  * Là cách viết chuỗi có dạng `f"...{variable / expression}..."`
  * Nó cho phép nhét trực tiếp giá trị của biến hoặc biểu thức vào trong chuỗi thông qua `{}`

```python
# f"...{variable}..."
name = input("Nhập tên: ")
age = int(input("Nhập tuổi: "))
# Xuất dữ liệu với f-string
print(f"Xin chào {name}\nBạn {age} tuổi")

# f"...{expression}..."
a, b = 5, 7
print(f"Tổng của {a} và {b} là {a + b}")
print(f"Tên in hoa: {name.upper()}")
```

## 4) Cấu trúc điều kiện (if / elif / else, toán tử 3 ngôi)

> Cấu trúc điều kiện giúp chương trình ra quyết định, tức là thực hiện một đoạn code chỉ khi điều kiện đúng

### 4.1 Cú pháp cơ bản của if

Trong Python:
* Không có dấu ngoặc `()` như C/Java
* Phải có dấu `:` sau điều kiện
* Phải thụt lề 4 spaces (tab) cho phần body
* Không có dấu `{ }` bọc phần body, Python dùng thụt lề để xác định khối lệnh

```python
"""
Xếp loại học viên:
    Điểm < 5: Yếu
    Điểm >= 5: Khá
"""
score = int(input("Nhập điểm: "))

# Câu điều kiện thiếu
if score < 5:
    print("Yếu")

if score >= 5:
    print("Khá")
```

### 4.2 if kết hợp else

Câu điều kiện đủ: có cả nhánh if-else
* Nếu điều kiện không đúng, chương trình sẽ chạy vào nhánh else

```python
score = int(input("Nhập điểm: "))

# Câu điều kiện đủ
if score < 5:
    print("Yếu")
else:
    print("Khá")
```

> Nên sử dụng if-else vì chương trình chỉ kiểm tra điều kiện `score < 5` một lần => performance tối ưu hơn

### 4.3 Kiểm tra nhiều điều kiện elif

`elif` là viết tắt của `else-if`
* Dùng khi cần kiểm tra nhiều trường hợp khác nhau theo thứ tự

```python
"""
Xếp loại học viên:
    Điểm < 5: Yếu
    Điểm >= 5 và điểm < 7: Trung bình
    Điểm >= 7 và điểm < 8.5: Khá
    Điểm >= 8.5: Giỏi
"""
score = float(input("Nhập điểm: "))

if score < 5:
    print("Yếu")
elif score < 7:
    print("Trung bình")
elif score < 8.5:
    print("Khá")
else:
    print("Giỏi")
```

> Lưu ý:
> * `elif` sẽ chỉ chạy điều kiện đầu tiên đúng, và bỏ qua toàn bộ phía dưới, dù có đúng hay không
> * Thứ tự kiểm tra rất quan trọng

Ví dụ SAI về thứ tự kiểm tra:

```python
score = 4.0

if score < 8.5:
    print("Giỏi")
elif score < 7:
    print("Khá")
elif score < 5:
    print("Trung bình")
else:
    print("Yếu")
```

### 4.4 Các toán tử dùng trong if

| Nhóm       | Toán tử           | Ví dụ            | Ý nghĩa        |
|------------|-------------------|------------------|----------------|
| So sánh    | `==`              | a == b           | bằng           |
|            | `!=`              | a != b           | khác           |
|            | `>` `<` `>=` `<=` | a > b            | so sánh        |
| Logic      | `and`             | a > 0 and a < 10 | cả hai đúng    |
|            | `or`              | a == 0 or a == 1 | 1 trong 2 đúng |
|            | `not`             | not is_student   | phủ định       |
| Thành viên | `in`              | x in list        | có trong       |
|            | `not in`          | x not in list    | không có trong |

### 4.5 Lồng điều kiện (Nested if)

> Có thể đặt if bên trong if

```python
age = 20

if age >= 18:
    print("Đã đủ 18+")
    if age >= 60:
        print("Đã đủ tuổi hưu")
```

### 4.6 Toán tử 3 ngôi (Ternary Operator)

> Python không có toán tử `? :` như C/Java <br> 
> Thay vào đó là cú pháp: `giá_trị_if_true if điều_kiện else giá_trị_if_false`

* Ví dụ 1
```python
age = 20
status = "18+" if age >= 18 else "Chưa đủ tuổi"
print(status)
```

* Ví dụ 2
```python
a, b = 10, 5
max_value = a if a > b else b
print(max_value)
```
