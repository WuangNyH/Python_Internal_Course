# Khung chương trình training Python + FastAPI (6 buổi)

---

## Buổi 1 – Cấu trúc điều kiện, Vòng lặp, Hàm, String

1. **Cấu trúc điều kiện**

   * if, if-else, if-elif-else
   * Toán tử so sánh, toán tử logic trong điều kiện
   * Toán tử 3 ngôi (`x if condition else y`)
   * Nested if (if lồng nhau)

2. **Vòng lặp cơ bản**

   * for với range(), list, string
   * while: điều kiện lặp, tránh vòng lặp vô hạn
   * break, continue
   * Vòng lặp lồng nhau (nested loop)

3. **Hàm (function)**

   * Khái niệm hàm, lợi ích khi dùng hàm
   * Khai báo hàm với `def`, gọi hàm
   * Tham số (parameter) & đối số (argument)
   * return vs không return
   * Tham số mặc định (default parameter)

4. **String**

   * Chuỗi là immutable
   * Truy cập & cắt chuỗi: index, slicing
   * Các method thường dùng: `upper`, `lower`, `title`, `strip`, `replace`, `split`, `join`
   * f-string, format chuỗi với biểu thức
   * So sánh chuỗi: `==` vs `is` (nhấn mạnh dùng `==`)

---

## Buổi 2 – Cấu trúc dữ liệu (List, Tuple, Dict, Set) & Debug

1. **List & Tuple**

   * Tạo list, truy cập phần tử, slicing
   * Thêm/xóa/sửa: `append`, `insert`, `remove`, `pop`
   * Các hàm built-in: `len`, `sum`, `max`, `min`, `sorted`
   * List comprehension cơ bản
   * Tuple: tạo tuple, unpacking, dùng để return nhiều giá trị

2. **Dictionary**

   * Khái niệm key–value
   * Tạo dict, truy cập, thêm/sửa/xóa key
   * `get`, `keys`, `values`, `items`
   * Duyệt dict bằng for
   * Mô hình hóa "record" bằng dict; list[dict] ~ JSON

3. **Set**

   * Tạo set, loại bỏ phần tử trùng
   * Các phép toán tập hợp: union, intersection, difference

4. **Vòng lặp với cấu trúc dữ liệu**

   * Duyệt list, dict với for
   * `enumerate` để vừa có index, vừa có value
   * `zip` để duyệt song song nhiều list

5. **Debug cơ bản**

   * Debug bằng `print()`
   * Giới thiệu debug trong IDE: breakpoint, step into/over, xem biến
   * Tư duy tìm lỗi: kiểm tra type + giá trị trung gian

---

## Buổi 3 – File I/O, Exception, Module, DateTime/Time & OOP cơ bản

1. **Module & tổ chức code**

   * Khái niệm module (1 file .py)
   * `import`, `from ... import ...`, alias
   * Tách code thành nhiều file: `utils.py`, `main.py`, …

2. **File I/O**

   * Mở file với `open(path, mode, encoding)`
   * Các mode: `"r"`, `"w"`, `"a"`
   * Đọc file: `read`, `readline`, `readlines`
   * Ghi file: `write`
   * Dùng context manager: `with open(...) as f:`

3. **Exception Handling**

   * Khái niệm exception
   * `try / except` – bắt lỗi cơ bản (ValueError, FileNotFoundError, ZeroDivisionError, …)
   * `else`, `finally`
   * Thông báo lỗi thân thiện cho người dùng

4. **DateTime & đo thời gian thực thi**

   * `datetime.now()`, `datetime` cụ thể
   * Định dạng ngày giờ với `strftime`, parse với `strptime`
   * `timedelta` để cộng/trừ ngày giờ
   * `time.time()` để đo thời gian thực thi đoạn code

5. **OOP cơ bản**

   * Khái niệm class, object
   * `__init__`, `self`
   * Thuộc tính (attribute) & phương thức (method)
   * Ví dụ class `Student` với `name`, `age`, `score`
   * Dùng `list[Student]` + method/hàm xử lý danh sách student (tính điểm trung bình, tìm max/min, …)
   * Tham số `*args`, `**kwargs`
   * `__str__`, `__repr__`

---

## Buổi 4 – FastAPI Fundamentals: REST, Endpoint, Request/Response

1. **Tổng quan Web & REST API**

   * HTTP method: GET, POST, PUT, DELETE
   * Request, Response, JSON
   * Status code cơ bản: 200, 201, 400, 404, 500

2. **FastAPI Hello World**

   * Cài `fastapi`, `uvicorn`
   * Tạo `main.py` và cấu hình app FastAPI
   * Chạy server với `uvicorn main:app --reload`
   * Swagger UI: `/docs`, `/redoc`

3. **Path & Query Parameters**

   * Path param: `/items/{item_id}`
   * Query param: `/items?skip=0&limit=10`

4. **Pydantic Model – Request/Response**

   * Định nghĩa schema input/output
   * Validate dữ liệu tự động

5. **In-memory CRUD API**

   * Quản lý list items trong bộ nhớ
   * Endpoint: `GET /items`, `GET /items/{id}`, `POST /items`, `PUT /items/{id}`, `DELETE /items/{id}`

---

## Buổi 5 – FastAPI + Database (SQLAlchemy) & tổ chức project

1. **Kết nối cơ sở dữ liệu**

   * Chọn DB: SQLite (đơn giản) hoặc PostgreSQL
   * Cấu hình `SQLAlchemy`: `engine`, `SessionLocal`, `Base`

2. **Models & Schemas**

   * SQLAlchemy models (tầng persistence)
   * Pydantic schemas (tầng API contract)
   * Mapping giữa model & schema

3. **CRUD với DB trong FastAPI**

   * Dependency `get_db`
   * Đọc/ghi dữ liệu từ DB trong endpoint
   * Sử dụng `HTTPException` cho 404, 400, …

4. **Tổ chức cấu trúc project**

   * Thư mục `app/`: `main.py`, `models.py`, `schemas.py`, `database.py`, `routers/`
   * Tách router: `students`, `items`, …

5. **Hoàn thiện CRUD thực tế**

   * CRUD Student/Task với DB thật
   * Test bằng Swagger & (nếu kịp) Postman

---

## Buổi 6 – Auth cơ bản, pytest & Mini Project FastAPI

1. **Authentication cơ bản với FastAPI**

   * Khái niệm Authentication vs Authorization
   * JWT: khái niệm, payload cơ bản
   * Endpoint đăng ký (`/auth/register`), đăng nhập (`/auth/login`)
   * Sinh và kiểm tra token (ở mức đơn giản)
   * Bảo vệ route bằng dependency (yêu cầu token)

2. **Giới thiệu pytest cho FastAPI/Python**

   * Cài đặt `pytest`
   * Cấu trúc file test: `test_*.py`
   * Test function Python đơn giản
   * (Nếu kịp) Test endpoint FastAPI với `TestClient`

3. **Mini Project FastAPI**

   * Chọn domain: Student/Todo/Shop,…
   * Yêu cầu tối thiểu:

     * CRUD entity chính (students/todos/…)
     * Lưu DB thật bằng SQLAlchemy
     * Một số route yêu cầu đăng nhập (dùng JWT đơn giản)
     * Log thời gian tạo/sửa bản ghi (datetime)

4. **Tổng kết & Định hướng**

   * Ôn lại pipeline: Python core → FastAPI → DB → Auth → Test
   * Gợi ý học tiếp: pytest nâng cao, Alembic migration, Docker, CI/CD, triển khai production
