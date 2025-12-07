# Python Core – Buổi 3: Cấu trúc dữ liệu (List – Tuple – Dict – Set) & Debug

# 1) Module & Tổ Chức Code trong Python

## 1.1 Khái niệm Module

> **Module = 1 file `.py` chứa code** (hàm, biến, class…) và có thể được import vào file khác

Ví dụ:

```
math.py => module chuẩn của Python
utils.py => module do chúng ta tự tạo
main.py => file chính chạy chương trình
```

**Lợi ích của module:**

* Tách code thành nhiều phần nhỏ => dễ quản lý
* Tái sử dụng code giữa nhiều file
* Giảm trùng lặp
* Dễ bảo trì, mở rộng dự án

---

## 1.2 Import module

### Cú pháp 1: `import module_name`

```python
import math

print(math.sqrt(16))
```

### Cú pháp 2: `from module_name import function`

```python
from math import sqrt
print(sqrt(16))
```

### Cú pháp 3: `import module_name as alias`

```python
import math as m
print(m.pi)
```

### Cú pháp 4: Import nhiều hàm

```python
from math import sqrt, sin, cos
```

> **Lưu ý:** chỉ import những gì cần dùng để code rõ ràng hơn

---

## 1.3 Tự tạo module

* Chúng ta có thể tạo file **utils.py** như sau:

```python
def add(a, b):
    return a + b

def is_even(n):
    return n % 2 == 0
```

Trong **main.py**:

```python
import utils

print(utils.add(3, 4))
print(utils.is_even(10))
```

Hoặc:

```python
from utils import add, is_even
print(add(5, 7))
```

> **Quy tắc:** mỗi module chỉ nên giải quyết một nhóm chức năng nhất định

---

## 1.4 Tổ chức code theo thư mục (package)

**Package = thư mục chứa nhiều module** + file `__init__.py`

* Ví dụ cấu trúc dự án:

```
project/
│
├── main.py
├── utils/
│   ├── __init__.py
│   ├── math_utils.py
│   └── string_utils.py
```

* Trong `math_utils.py`:

```python
def add(a, b):
    return a + b
```

Dùng trong `main.py`:

```python
from utils.math_utils import add
print(add(3, 5))
```

> `__init__.py` giúp Python hiểu thư mục là 1 package có thể import

---

## 1.5 Biến `__name__ == '__main__'` để chạy trực tiếp

Trong `main.py`:

```python
def run():
    print("Chương trình chính đang chạy...")

if __name__ == '__main__':
    run()
```

Mục đích:

* Code **không chạy** khi file được import ở nơi khác
* Chỉ chạy khi file được chạy trực tiếp bằng command:

```
python main.py
```

---

## 1.6 Tổ chức code tốt khi dự án lớn dần

Ví dụ cấu trúc **tốt** hơn cho dự án nhỏ:

```
project/
│── main.py
│── services/
│     ├── __init__.py
│     ├── student_service.py
│     └── file_service.py
│── utils/
      ├── __init__.py
      └── helpers.py
```

**Nguyên tắc quan trọng:**

* Mỗi module chỉ làm 1 nhiệm vụ => *Single Responsibility*
* Tránh file quá dài (lên đến cả ngàn dòng)
* Đặt tên module rõ ràng: `student_service`, `file_service`, `helpers`, ...

---

## 1.7 Lỗi thường gặp khi import

### 1) ImportError: module không tồn tại

```
ImportError: No module named 'utils'
```

**Nguyên nhân:** sai tên file hoặc sai đường dẫn.

### 2) Circular import (import vòng tròn)

```
A import B, B import A => lỗi
```

Cách tránh:

* Đưa hàm chung vào file riêng
* Chỉ import những gì cần

---

# 2) File I/O – Đọc & Ghi File trong Python

## 2.1 Khái niệm File I/O

**File I/O (Input/Output)** là cách Python làm việc với file:

* Đọc dữ liệu từ file => Input
* Ghi dữ liệu vào file => Output

> Đây là kỹ năng cốt lõi giúp chương trình lưu trữ dữ liệu thay vì chỉ chạy trong RAM

Python cung cấp hàm `open()` để làm việc với file

Cú pháp: `open(path, mode, encoding)`

---

## 2.2 Các chế độ mở file (mode)

| Mode   | Ý nghĩa                           | Ghi chú                    |
|--------|-----------------------------------|----------------------------|
| `"r"`  | Đọc file                          | Lỗi nếu file không tồn tại |
| `"w"`  | Ghi mới (xóa toàn bộ nội dung cũ) | Tạo file mới nếu chưa có   |
| `"a"`  | Ghi nối thêm vào cuối file        | Không xóa nội dung cũ      |
| `"r+"` | Đọc + Ghi                         | File phải tồn tại          |
| `"b"`  | Binary mode                       | Dùng cho ảnh, pdf, mp3     |

Ví dụ:

```python
f = open("data.txt", "r", encoding="utf-8")
```

---

## 2.3 Đọc file

### 2.3.1 `read()`: đọc toàn bộ file thành một chuỗi

```python
with open("data.txt", "r", encoding="utf-8") as f:
    content = f.read()
print(content)
```

### 2.3.2 `readline()`: đọc từng dòng một

```python
with open("data.txt", "r", encoding="utf-8") as f:
    line1 = f.readline()
    line2 = f.readline()
```

### 2.3.3 `readlines()`: đọc tất cả dòng, trả về list

```python
with open("data.txt", "r", encoding="utf-8") as f:
    lines = f.readlines()

for line in lines:
    print(line.strip())
```

> `strip()` giúp loại bỏ ký tự xuống dòng

---

## 2.4 Ghi file

### 2.4.1 Ghi file bằng `write()`

Chế độ `"w"` => ghi mới hoàn toàn:

```python
with open("output.txt", "w", encoding="utf-8") as f:
    f.write("Xin chào Python!")
    f.write("Dòng thứ hai")
```

Chế độ `"a"` => ghi nối thêm:

```python
with open("output.txt", "a", encoding="utf-8") as f:
    f.write("Dòng mới được thêm vào")
```

### 2.4.2 Ghi list vào file

```python
lines = ["Hello", "Python", "File I/O"]
with open("list.txt", "w", encoding="utf-8") as f:
    for line in lines:
        f.write(line + "\n")
```

---

## 2.5 Vì sao nên dùng `with open(...) as f:`

**Context Manager** giúp:

* Tự đóng file, kể cả khi có lỗi xảy ra
* An toàn hơn `open()` + `close()`

Ví dụ không an toàn:

```python
f = open("data.txt", "r")
data = f.read()
f.close()
```

Ví dụ chuẩn cho file I/O:

```python
with open("data.txt", "r") as f:
    data = f.read()
```

> Quy tắc: **luôn dùng `with open()` khi thao tác file** trong Python

---

## 2.6 Xử lý ngoại lệ khi thao tác file

### File không tồn tại → `FileNotFoundError`

```python
try:
    with open("abc.txt", "r") as f:
        data = f.read()
except FileNotFoundError:
    print("Không tìm thấy file!")
```

### Báo lỗi cho người dùng

```python
filename = "data.txt"
try:
    with open(filename, "r", encoding="utf-8") as f:
        print(f.read())
except Exception as e:
    print("Có lỗi xảy ra khi đọc file:", e)
```

---

## 2.7 Làm việc với file nhị phân (binary file)

Dùng mode `"rb"` và `"wb"`:

```python
with open("photo.jpg", "rb") as f:
    data = f.read()

with open("copy.jpg", "wb") as f:
    f.write(data)
```

> Dùng cho ảnh, pdf, video

---

# 3) Exception Handling – Xử lý ngoại lệ trong Python

## 3.1 Khái niệm

**Exception = lỗi xảy ra trong lúc chương trình đang chạy (runtime error)** khiến chương trình dừng lại, trừ khi chúng ta xử lý nó

Ví dụ các lỗi thường gặp:

* `ValueError`: sai kiểu dữ liệu đầu vào
* `ZeroDivisionError`: chia cho 0
* `FileNotFoundError`: file không tồn tại
* `TypeError`: truyền sai kiểu tham số
* `IndexError`: truy cập index không tồn tại

Ví dụ:

```python
x = int("abc") # ValueError: invalid literal for int()
```

> Mục tiêu của Exception Handling: **giúp chương trình không bị crash** và **xử lý lỗi một cách an toàn và thân thiện**

---

## 3.2 Cú pháp try / except

```python
try:
    # đoạn code có nguy cơ lỗi
    x = 10 / 0
except ZeroDivisionError:
    print("Không thể chia cho 0!")
```

* Nhiều loại lỗi:

```python
try:
    raw = input("Nhập một số nguyên: ")
    x = int(raw)
    y = 10 / x
    print(f"Kết quả 10 / {x} =", y)
except ValueError:
    print("Lỗi: Bạn phải nhập một số nguyên hợp lệ!")
except ZeroDivisionError:
    print("Lỗi: Không thể chia cho 0!")
except Exception as e:
    print("Lỗi không xác định:", e)
```

> Một `try` có thể có nhiều khối `except` để xử lý từng loại lỗi

---

## 3.3 Bắt nhiều lỗi trong cùng một except

* Gom nhiều loại lỗi vào 1 khối `except` để xử lý chung  

```python
try:
    x = int("abc")
except (ValueError, TypeError):
    print("Lỗi nhập liệu!")
```

---

## 3.4 Bắt mọi lỗi

```python
def risky_code(a):
    print(1/a)

try:
    risky_code(0)
except Exception as e:
    print("Có lỗi xảy ra:", e)
```

> Hữu ích để debug hoặc log lỗi, nhưng không nên lạm dụng vì che giấu lỗi thật => khó debug lỗi

---

## 3.5 Khối else trong try/except

Chạy **khi không có lỗi**:

```python
try:
    x = int(input("Nhập số: "))
except ValueError:
    print("Bạn nhập sai!")
else:
    print("Bạn nhập:", x)
```

Trong thực tế ít dùng khối `else` trong `try/except`

---

## 3.6 Khối finally

* **Luôn chạy** dù có lỗi hay không
* Thường dùng để đóng tài nguyên (file, kết nối DB, ...)

Ví dụ:

```python
# Đóng kết nối DB
try:
    conn = connect_to_db() # mở kết nối DB
    result = conn.query("SELECT * FROM users")
    print(result)
except Exception as e:
    print("Lỗi khi truy vấn:", e)
finally:
    print("Đóng kết nối DB…")
    conn.close()

# Reset trạng thái hệ thống
state = "busy"

try:
    print("Đang chạy tác vụ quan trọng…")
    # risky_task()
except Exception:
    print("Tác vụ lỗi!")
finally:
    state = "idle"
    print("Trạng thái đã reset về:", state)
```

---







## 3.7 Tự tạo exception bằng `raise`

Khi muốn báo lỗi chủ động:

```python
def divide(a, b):
    if b == 0:
        raise ValueError("b không được = 0")
    return a / b

try:
    divide(5, 0)
except ValueError as e:
    print("Lỗi:", e)
```

> Dùng `raise` để kiểm soát logic chương trình rõ ràng hơn

---

## 3.8 Áp dụng Exception vào File I/O

```python
filename = input("Nhập tên file: ")

try:
    with open(filename, "r", encoding="utf-8") as f:
        print(f.read())
except FileNotFoundError:
    print("File không tồn tại!")
except PermissionError:
    print("Bạn không có quyền đọc file này!")
except Exception as e:
    print("Lỗi khác:", e)
```

---

## 3.9 Tư duy xử lý lỗi đúng cách

Khi viết code, hãy tự hỏi:

* Đoạn nào có nguy cơ lỗi → bọc try/except
* Người dùng cần biết gì? (Thông báo dễ hiểu)
* Có cần đóng file, giải phóng tài nguyên?
* Có nên dừng chương trình hay tiếp tục?

Sai lầm thường gặp:

* Bắt lỗi chung chung mà không xử lý gì
* Che dấu lỗi khiến debug khó hơn
* Bỏ qua `finally` khiến file không được đóng

---

## 3.10 Thực hành Exception Handling

### BTTH8 – Bắt lỗi nhập số

Viết chương trình:

1. Nhập một số nguyên từ người dùng
2. Nếu nhập sai → báo lỗi và yêu cầu nhập lại

Ví dụ chạy:

```
Nhập số: abc
Sai! Vui lòng nhập lại.
Nhập số: 123
Bạn đã nhập: 123
```

---

### BTTH9 – Hàm chia có xử lý lỗi

Viết hàm:

```python
def safe_divide(a, b):
    # nếu b = 0 → raise lỗi
```

Sử dụng try/except khi gọi hàm và in kết quả.

---

### BTTH10 – Đọc file an toàn

Viết chương trình:

* Hỏi người dùng tên file
* Nếu file tồn tại → in nội dung
* Nếu không tồn tại → báo lỗi thân thiện

---

### BTTH11 – Tạo menu và xử lý lỗi lựa chọn

Menu:

```
1. Xin chào
2. Tính tổng 2 số
3. Thoát
```

Yêu cầu:

* Nếu người dùng nhập ký tự không phải số → báo lỗi
* Nếu nhập số ngoài 1–3 → báo lỗi
* Nếu đúng → thực thi chức năng

---


