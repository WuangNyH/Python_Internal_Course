# Python Core – Buổi 1: Tổng quan về Python, cấu trúc Điều kiện, Vòng lặp, Hàm, String

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

---

## 2) Chương trình Python đầu tiên

* Tạo file hello.py:

```python
print("Hello, Techzen Academy!")
```

* Chạy chương trình
  * Run bằng IDE PyCharm (`shift + F10`)
  * Run bằng terminal: `python hello.py` hoặc `py hello.py`

> Hàm `print()`: dùng để in thông tin ra console

---

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

---

### 3.2 Toán tử cơ bản

* Số học: 
  * `+ - * /`
  * `//`: chia lấy nguyên
  * `%`: chia lấy dư
  * `**`: lũy thừa
* Gán: `=`, `+=`, `-=`, ...
* So sánh: `==`, `!=`, `>`, `<`, `>=`, `<=`
* Logic: `and`, `or`, `not`

---

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

* Các tham số thường dùng trong `print(*objects, sep=' ', end='\n', file=None, flush=False)`
  * `*objects`: Các đối tượng cần in (dấu `*`: truyền bao nhiêu `args` cũng được)
    ```python
        print("Hello", 123, True)
    ```
  * `sep`: Separator (chuỗi phân cách giữa các object)
    * Mặc định `sep=" "`
    * Nếu muốn thay dấu cách bằng dấu khác:
      ```python
        print("A", "B", "C", sep="-")
        print("A", "B", "C", sep="")
      ```
    * **Lưu ý**: `sep` chỉ có tác dụng khi in nhiều object
  * `end`: In gì sau khi kết thúc `print()`
    * Mặc định `end="\n"`
    * Nếu muốn không xuống dòng, dùng `end=""`
  * `file`: nơi để in dữ liệu ra
    * Mặc định in ra màn hình `sys.stdout` (màn hình console)
    * Có thể in ra file:
      ```python
        f = open("output.txt", "w")
        print("Hello", file=f)
      ```
  * `flush`: dùng để ép Python ghi ra màn hình hoặc file ngay lập tức
    * Mặc định `flush=false`

* Dùng `f-string`: 
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

---

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

---

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

---

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

---

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

```python
age = 20
has_id_card = True

if age >= 18 and has_id_card:
    print("Được vào")
else:
    print("Không được vào")
```

---

### 4.5 Lồng điều kiện (Nested if)

> Có thể đặt `if` bên trong `if`

```python
age = 20

if age >= 18:
    print("Đã đủ 18+")
    if age >= 60:
        print("Đã đủ tuổi hưu")
```

**Lưu ý**:
* Hạn chế lồng `if` quá sâu, nên tách logic thành hàm cho dễ đọc

---

### 4.6 Toán tử 3 ngôi (Ternary Operator)

* Python không có toán tử `? :` như C/Java <br> 
* Thay vào đó là cú pháp: 
  > giá_trị_if_true `if` điều_kiện `else` giá_trị_if_false

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

---

### 4.7 Thực hành nhanh về cấu trúc điều kiện

#### BTTH1: Kiểm tra tuổi

> Viết chương trình nhập tuổi:
> * In `Trẻ con` (0-11) / `Thiếu niên` (12-17) / `Thanh niên` (18-30) / `Người già` (trên 30) 

#### BTTH2: Kiểm tra chẵn lẻ - Dùng toán tử 3 ngôi

> Viết chương trình:
> * Nhập 1 số nguyên `n` từ bàn phím
> * In `Even` nếu `n` là số chẵn, `Odd` nếu là số lẻ

#### BTTH3: Kiểm tra năm nhuận

> Viết chương trình kiểm tra năm nhuận:
> * Rule: năm nhuận nếu:
>   * Chia hết cho 400, hoặc
>   * Chia hết cho 4 và không chia hết cho 100

---

## 5) Cấu trúc vòng lặp

### 5.1 Vòng lặp for với range

```python
for i in range(5): # 0, 1, 2, 3, 4
    print(i, end=" ") # end mặc định "\n"

print() # xuống dòng sau khi in

for i in range(1, 6): # 1, 2, 3, 4, 5
    print(i, end=" ")

print()
```

**Ý nghĩa**:
* `range(stop)`: từ 0 đến `stop - 1`
* `range(start, stop)`: từ start đến stop - 1

---

### 5.2 for-each duyệt list và string

```python
names = ["Doraemon", "Nobita", "Shizuka"]
for name in names:
    print(name, end=" ")
print()

string = "hello"
for character in string:
    print(character)
```

**Lưu ý**:
* Python ưu tiên `for-each` style (duyệt trực tiếp phần tử) thay vì dùng index

---

### 5.3 break và continue

```python
# break
for i in range(1, 11):
    if i == 5:
        break
    print(i, end=" ")
print()

# continue
for i in range(1, 11):
    if i % 2 == 0:
        continue
    print(i, end=" ")
print()
```

---

### 5.4 Vòng lặp while

```python
n = 5
while n > 0:
    print(n, end="\t")
    n -= 1
print()

# while True
while True:
    pwd = input("Nhập mật khẩu: ")
    if pwd == "123@techzen":
        print("Đúng rồi người đẹp")
        break # bắt buộc luôn có break/return trong while True
    print("Sai rồi! Chịu khó nhập lại đi em iu")
```

**Lưu ý**:
* Luôn đảm bảo điều kiện dừng, tránh `while True` mà không có `break`/`return`
* Không thể dùng `return` ở cấp độ module, `return` chỉ hợp lệ bên trong function

---

### 5.5 Vòng lặp lồng (Nested Loop)

> * Nested Loop: Một vòng lặp con được đặt bên trong vòng lặp cha
> * Khi vòng lặp cha thực hiện 1 bước lặp => vòng lặp con phải lặp lại từ đầu

```python
for i in range(3): # i = 0,1,2
    for j in range(2): # j = 0,1
        print(f"Vòng {i}: {j}")
```

* In hình chữ nhật bằng dấu `*` với `row=5`, `col=6`:
```python
"""
* * * * * *
* * * * * *
* * * * * *
* * * * * *
* * * * * *
"""
row, col = 5, 6
for i in range(row):
    for j in range(col):
        print("*", end=" ")
    print()
```

---

### 5.6 Thực hành nhanh về cấu trúc lặp

#### BTTH4: Tính tổng từ 1 đến n

> Viết chương trình nhập tuổi:
> * Nhập 1 số nguyên `n` từ bàn phím
> * Tính `1 + 2 + ... + n` 

#### BTTH5: Đếm số ký tự 'a' trong chuỗi

> Viết chương trình:
> * Nhập 1 chuỗi bất kỳ `string` từ bàn phím
> * Đếm số ký tự 'a' trong chuỗi `string`

#### BTTH6: In các hình sau

```python
"""
6a. Hình chữ nhật rỗng
* * * * * *
*         *
*         *
*         *
* * * * * *
"""

"""
6b. Hình tam giác vuông cân
*
* *
* * *
* * * *
* * * * *
"""
```

---

## 6) Hàm (Function)

### 6.1 Khai báo và gọi hàm

> Khái niệm:
> * Hàm là một khối lệnh có tên, có thể nhận tham số, có thể trả về giá trị
> * Giúp code tái sử dụng, dễ đọc, dễ test

* Cú pháp:

```python
def say_hello(name: str) -> None:
    print(f"Hello, {name}!")

# Gọi hàm
say_hello("Taro")
```

**Ý nghĩa**:
* `-> None`: Hàm `say_hello()` không trả về gì cả
* `name: str`: khai báo kiểu tham số
  * Python là ngôn ngữ dynamic, không cần kiểu tham số khi truyền => có thể viết `def say_hello(name)`
  * Theo chuẩn `PEP 484` (type hints), dự án thực tế nên khai báo kiểu dữ liệu cho tham số và kiểu trả về
    * IDE sẽ hiện cảnh báo khi truyền sai kiểu `say_hello(100)` => cảnh báo vàng

---

### 6.2 Tham số và giá trị trả về

```python
def add(a: int, b: int) -> int:
    return a + b

result = add(1, 2)
print(result)
```

**Lưu ý**:
* `return` kết thúc hàm và trả lại giá trị
* Nếu không có `return`, hàm trả về `None`

---

## 6.3 Tham số mặc định

* Có thể gán giá trị mặc định cho tham số khi định nghĩa hàm

```python
def power(base: int, exp: int = 2) -> int:
    return base ** exp

print(power(3)) # 9
print(power(3, 3)) # 27
```

---

## 6.4 Tham số có thể nhận None

> * Trong Python, có những trường hợp tham số không bắt buộc, hoặc khi muốn cho phép truyền vào giá trị thiếu
> * Khi đó dùng `None` như một giá trị đặc biệt

```python
def greet(name: str | None = None) -> None:
    if name is None:
        print("Hello, stranger!")
    else:
        print(f"Hello, {name}!")
        
greet() # Hello, stranger!
greet("Taro") # Hello, Taro!
```

* Thực tế thường được dùng để xử lý tham số `optional`

```python
def repeat_message(msg: str, times: int | None = None) -> None:
    # Cần xử lý None trong hàm
    # Nếu không truyền times => mặc định là 1
    if times is None:
        times = 1

    for _ in range(times):
        print(msg)

repeat_message("Hi") # không truyền times => ta đã gán lại thành 1
repeat_message("Hi", 3) # times = 3
repeat_message("Hi", None) # Người gọi cố tình truyền None => ta cũng đã xử lý
```

* Dấu `_` được dùng khi ta không cần sử dụng biến đó trong vòng lặp 
  * Nếu dùng `i` thì Python vẫn tạo biến `i`, dù trong vòng lặp không hề dùng nó 

---

### 6.4 Thực hành nhanh về hàm

#### BTTH7: Viết lại các bài tập đã làm bằng hàm

> 7a. Hàm tính tổng từ 1 đến n 
> * `sum_to_n(n: int) -> int`
> 
> 7b. Hàm kiểm tra năm nhuận
> * `is_leap_year(year: int) -> bool`
> 
> 7c. Hàm đếm ký tự
> * `count_char(string: str, char: str) -> int`

#### BTTH8: Viết hàm định dạng tên với optional middle name

> `format_name(first: str, last: str, middle: str | None = None) -> str`
> * Nếu `middle = None` → trả về dạng "first last"
> * Nếu có middle → trả về dạng "first middle last"

---

## 7) String & thao tác chuỗi

### 7.1 String là immutable

> Trong Python, string là kiểu dữ liệu bất biến (immutable)
> * Tức là: sau khi tạo chuỗi, không thể sửa trực tiếp từng ký tự bên trong nó

* Ví dụ:

```python
s = "python"
s[0] = "P"  # Lỗi: 'str' object does not support item assignment
```

* Muốn thay đổi một phần chuỗi, bắt buộc phải tạo ra chuỗi mới:

```python
s = "python"
s = "P" + s[1:]  # tạo chuỗi mới từ kí tự 'P' + nối phần còn lại "ython"
print(s)  # Python
```

* Chuỗi trong Python là một iterable => có thể duyệt từng ký tự bằng vòng lặp hoặc kiểm tra từng ký tự giống như duyệt list

```python
s = "python"
for ch in s:
    print(ch)

print("a" in "banana") # True
```

---

### 7.2 Truy cập & cắt chuỗi (index, slice)

* Index

```python
s = "python"
print(s[0])  # p
print(s[-1])  # n (index âm tính từ phải sang)
print(s[1:4])  # yth
```

* Slice: `s[start:end]`
  * Lấy từ `start` đến `end - 1`
  * Có thể bỏ `start` hoặc `end`

```python
s1 = "Hello World"
print(s1[:5]) # "Hello" (từ đầu đến index 4)
print(s1[6:]) # "World" (từ index 6 đến hết)
print(s1[:]) # "Hello World"

s2 = "abcdefg"
print(s2[::2]) # "aceg" (bỏ qua 1 ký tự)
print(s2[::-1]) # "gfedcba" (đảo ngược chuỗi)
```

---

### 7.3 Các phương thức thường dùng

#### 7.3.1 Thay đổi kiểu chữ: upper(), lower(), title()

```python
s3 = "hello world"

print(s3.upper()) # "HELLO WORLD"
print(s3.lower()) # "hello world"
print(s3.title()) # "Hello World"
```

#### 7.3.2 Xử lý khoảng trắng & thay thế: strip(), replace()

```python
s4 = "   hello world   "

print(s4.strip()) # "hello world" (bỏ khoảng trắng đầu & cuối)
print(s4.lstrip()) # "hello world   " (bỏ bên trái)
print(s4.rstrip()) # "   hello world" (bỏ bên phải)

print(s4.strip().replace("hello", "hi"))  # "hi world"
```

* `strip()`: bỏ khoảng trắng (hoặc ký tự chỉ định) ở đầu và cuối chuỗi
* `lstrip()` / `rstrip()`: bỏ bên trái / bên phải
* `replace(old, new)`: thay tất cả old bằng new trong chuỗi

#### 7.3.3 Tách & ghép chuỗi: split(), join()

* `split()` – tách chuỗi thành list các từ/phần tử

```python
s5 = "python is fun"
words = s5.split() # mặc định tách theo khoảng trắng
print(words) # ['python', 'is', 'fun']

s6 = "a,b,c,d"
items = s6.split(",") # tách theo dấu phẩy
print(items) # ['a', 'b', 'c', 'd']
```

* `join()` – ghép list chuỗi thành một chuỗi

```python
words2 = ["python", "is", "boring"]
sentence = " ".join(words2)
print(sentence)  # "python is boring"

items2 = ["a", "b", "c"]
print("-".join(items2)) # "a-b-c"
```

#### 7.3.4 Một số hàm & phương thức tiện dụng khác

* `len()` – độ dài chuỗi

```python
s = "hello"
print(len(s))  # 5
```

* `startswith()`, `endswith()` – kiểm tra đầu/cuối chuỗi

```python
filename = "report.pdf"

print(filename.endswith(".pdf")) # True
print(filename.startswith("rep")) # True
print(filename.startswith("Report")) # False (phân biệt hoa thường)
```

---

### 7.4 So sánh chuỗi

> Trong Python, so sánh chuỗi chủ yếu dùng toán tử so sánh

#### 7.4.1 So sánh bằng == (so sánh nội dung)

```python
a = "hello"
b = "hello"
c = "Hello"

print(a == b)  # nội dung giống nhau => True
print(a == c)  # khác hoa/thường => False
```

* Chuỗi được so sánh theo từng ký tự, phân biệt chữ hoa – chữ thường
* Nếu muốn so sánh không phân biệt hoa thường, cần đưa cả 2 về cùng `lower()` hoặc `upper()`

#### 7.4.2 So sánh lớn hơn/nhỏ hơn (<, >, …)

> Chuỗi được so sánh theo thứ tự từ điển (lexicographic)

```python
print("apple" < "banana") # True
print("abc" > "ab") # True (vì 'abc' dài hơn, 'ab' là prefix)
```

#### 7.4.3 Không dùng is để so sánh nội dung chuỗi

> `is` được dùng để so sánh object có cùng địa chỉ trong bộ nhớ hay không

---

### 7.5 Thực hành nhanh về chuỗi

#### BTTH9: Chuẩn hóa họ tên

* `"  nGuyEn vAn a   "` => `"Nguyen Van A"`

#### BTTH10: Kiểm tra chuỗi đối xứng

* `level`, `madam `, `122 1`

#### BTTH11: Đếm số lượng nguyên âm trong chuỗi

* Nguyên âm tiếng Anh gồm: a, e, i, o, u
