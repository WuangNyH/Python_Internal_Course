# Bài tập 1: Dict tần suất từ trong file (Module + File I/O + Exception)

## Đề bài:
> Viết chương trình phân tích một file text (ví dụ: `article.txt`) và in ra tần suất xuất hiện của từng từ

### Yêu cầu chức năng
1. Chương trình hỏi người dùng:
```text
Nhập tên file cần phân tích:
```

2. Đọc toàn bộ nội dung file, chuẩn hóa:
* chuyển hết về chữ thường (`lower()`)
* bỏ các dấu câu cơ bản: `.,;:?!()[]` (có thể dùng `replace`)

3. Tách từ theo dấu cách, đếm số lần xuất hiện của từng từ
4. In ra:
* Tổng số từ
* Top 10 từ xuất hiện nhiều nhất cùng số lần xuất hiện

Ví dụ:

```text
Tổng số từ: 250
Top 10 từ xuất hiện nhiều nhất:
- python: 20
- code: 15
- file: 12
...
```

### Yêu cầu kỹ thuật
* Tách code thành ít nhất 2 file:
  * `file_utils.py`: chứa các hàm:
    ```python
        def read_file_content(filename: str) -> str: ...
        def count_word_frequency(text: str) -> dict[str, int]: ...
    ```
  * `main.py`: xử lý input người dùng, gọi hàm từ `file_utils`
* Phải dùng:
  * `with open(...)` để đọc file
  * `try/except` để xử lý:
    * `FileNotFoundError`: báo “File không tồn tại”
    * các lỗi khác: in “Có lỗi xảy ra: ...”
  * Không dùng thư viện ngoài (chỉ dùng built-in)

---

# Bài tập 2: Quản lý điểm sinh viên với File I/O + OOP + Exception

## Đề bài:
> Viết chương trình quản lý điểm sinh viên, dữ liệu được lưu trong file `students.txt`, mỗi dòng có format:

```text
Tên,Tuổi,Điểm
An,20,8.5
Binh,21,6.0
Chi,19,4.5
```

### Yêu cầu chức năng
1. Định nghĩa class `Student`:
```python
class Student:
    def __init__(self, name: str, age: int, score: float):
        self.name = name
        self.age = age
        self.score = score

    def is_passed(self) -> bool:  # đậu nếu score >= 5
        ...

    def __str__(self) -> str:
        # "An (20 tuổi) – Điểm: 8.5"
        ...
```

2. Viết hàm:

```python
def load_students_from_file(filename: str) -> list[Student]: ...
```

* Dùng `with open(...)` đọc file:
  * Bỏ qua các dòng trống
  * Xử lý lỗi:
    * Dòng sai format (thiếu cột, không parse được `age` hoặc `score`) => bỏ qua dòng đó và in cảnh báo

3. Viết các hàm xử lý:

* `def calc_avg_score(students: list[Student]) -> float`
* `def find_top_student(students: list[Student]) -> Student | None`
* `def filter_failed(students: list[Student]) -> list[Student]` (danh sách sinh viên rớt)

4. Trong `main.py`:
* Hỏi tên file:

```text
Nhập tên file điểm sinh viên:
```

* In ra:
  * Điểm trung bình lớp
  * Sinh viên điểm cao nhất
  * Danh sách sinh viên bị rớt

### Yêu cầu kỹ thuật
* Sử dụng OOP đúng nghĩa (class `Student`)
* Sử dụng list các object + các hàm xử lý list này
* Có `try/except` để:
  * Bắt lỗi không mở được file
  * Bắt lỗi khi parse dữ liệu từng dòng
* Nên dùng `type hint` cho hàm


---

# Bài tập 3: To-do List theo ngày với DateTime + File + OOP + Exception

## Đề bài:
> Xây dựng chương trình quản lý danh sách công việc (to-do list) theo ngày, lưu vào file `tasks.txt` với format mỗi dòng:

```text
Mô tả;YYYY-MM-DD;trạng_thái
Học Python;2025-01-10;todo
Đi tập gym;2025-01-09;done
Đi chơi;2025-01-08;todo
```

### Yêu cầu chức năng
1. Định nghĩa class `Task`:
```python
from datetime import datetime

class Task:
    def __init__(self, description: str, due_date: datetime, status: str = "todo"):
        self.description = description
        self.due_date = due_date # datetime
        self.status = status # "todo" hoặc "done"

    # Trả về True nếu quá hạn và chưa done
    def is_overdue(self, now: datetime) -> bool:
        ...

    def __str__(self) -> str:
        # Ví dụ: "[TODO] Học Python (Hạn: 2025-01-10)"
        ...

```

2. Viết hàm:

```python
def load_tasks(filename: str) -> list[Task]: ...
def save_tasks(filename: str, tasks: list[Task]) -> None: ...
```

* Dùng `datetime.strptime(due_str, "%Y-%m-%d")` để parse ngày
* Xử lý lỗi format ngày => bỏ qua dòng và in cảnh báo

3. Chương trình có menu:

```text
1. Xem tất cả task
2. Xem các task quá hạn
3. Thêm task mới
4. Đánh dấu task là done
5. Thoát
```

4. Chi tiết:
* “Xem tất cả task”: in lần lượt từng Task (dùng `__str__`)
* “Xem các task quá hạn”:
  * Dùng `datetime.now()` để lấy thời điểm hiện tại
  * In các task `is_overdue(now) == True`
* “Thêm task mới”:
  * Nhập: mô tả, ngày hạn dạng `YYYY-MM-DD`
  * Nếu ngày sai format => báo lỗi, không thêm
  * Thêm vào list và ghi lại file `tasks.txt`
* “Đánh dấu task là done”:
  * Hiển thị danh sách có đánh số:
    ```text
        1. [TODO] Học Python (Hạn: 2025-01-10)
        2. [TODO] Đi tập gym (Hạn: 2025-01-09)
    ```
  * Nhập số thứ tự, đổi `status` thành `"done"`, lưu lại file

### Yêu cầu kỹ thuật
* Bắt buộc dùng:
  * `datetime` (`now()`, `strptime`, `strftime` nếu muốn format khi in)
  * `with open` cho file I/O
  * `try/except` cho:
    * lỗi file
    * lỗi parse ngày
    * lỗi nhập số thứ tự không hợp lệ (`ValueError`)
* Tách code thành ít nhất 2 file:
  * `models.py` (chứa Task)
  * `task_service.py` (chứa hàm `load_tasks`, `save_tasks`, xử lý logic)
  * `main.py` (menu + luồng chương trình)
