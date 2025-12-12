# Buổi 4 – FastAPI Fundamentals

## 1) Kiến trúc Web: Client–Server, HTTP lifecycle, REST stateless

## 1.1 Client–Server

* Client (Browser, Mobile app, Postman, ...) gửi HTTP request => FastAPI server xử lý => trả HTTP response
* Tách biệt trách nhiệm:
  * Client: UI/UX, gọi API, hiển thị dữ liệu
  * Server (FastAPI): business rules, validation, truy cập dữ liệu (DB/Cache), trả JSON
* Lợi ích: dễ scale mở rộng, thay thế từng phần (client/server) độc lập, dễ test API bằng Postman/Swagger

---

## 1.2 HTTP Lifecycle (Request → Response) trong FastAPI

1. Client tạo request (method, URL, headers, query/path params, body JSON)
2. Request đến FastAPI (chạy trên `uvicorn`)
3. FastAPI xử lý theo pipeline (thực tế khi tổ chức theo MVC/service-layer):
   * Middleware (logging, CORS, auth, timing, ...)
   * Router / Controller (endpoint: `@router.get`, `@router.post`, ...)
   * Dependency Injection (`Depends(...)`): lấy DB session, auth user, config ...
   * Service layer: xử lý nghiệp vụ
   * Repository / Data access: thao tác DB (SQLAlchemy) hoặc gọi service khác
   * Pydantic validation: validate request body + serialize response theo schema
4. FastAPI trả response (status code, headers, JSON body) => client hiển thị/tiếp tục gọi API khác

> Điểm mạnh của FastAPI: validation + OpenAPI docs tự sinh, giúp thấy ngay tài liệu API khi vào `/docs`

---

## 1.3 REST & Stateless

* REST: phong cách thiết kế API dựa trên HTTP, tài nguyên (resource) được mô hình hóa bằng URL
  * Ví dụ: `/users`, `/users/{id}`, `/items`, `/orders/{order_id}`
* Stateless: mỗi request tự chứa đủ context để server xử lý
  * Context ở: headers (Authorization), path/query params, body
  * Server không “nhớ” state của client giữa các request (hạn chế session server-side; ưu tiên token/JWT)
* Idempotent (hành vi gọi lặp không làm thay đổi kết quả cuối):
  * `GET`, `PUT`, `DELETE` nên idempotent
  * `POST` thường không idempotent (tạo bản ghi mới mỗi lần)

---

## 1.4 HTTP Protocol: methods, status codes, headers, body

### 1.4.1 Methods

| Method   | Dùng cho                     | Ghi chú theo REST/FastAPI |
|----------|------------------------------|---------------------------|
| `GET`    | Lấy tài nguyên               | Safe, Idempotent          |
| `POST`   | Tạo mới / thực thi hành động | Thường not idempotent     |
| `PUT`    | Cập nhật thay thế toàn bộ    | Idempotent                |
| `PATCH`  | Cập nhật một phần            | Không đảm bảo idempotent  |
| `DELETE` | Xóa tài nguyên               | Idempotent                |

Trong FastAPI, mapping trực tiếp:
* `@app.get("/...")`, `@app.post("/...")`, `@app.put("/...")`, `@app.patch("/...")`, `@app.delete("/...")`

### 1.4.2 Status codes

| Mã                          | Ý nghĩa                    | Khi nào dùng trong FastAPI                                               |
|-----------------------------|----------------------------|--------------------------------------------------------------------------|
| `200 OK`                    | Thành công                 | `GET`, `PUT`, `PATCH` trả dữ liệu                                        |
| `201 Created`               | Tạo mới thành công         | `POST` tạo resource                                                      |
| `204 No Content`            | Thành công không trả body  | `DELETE` không cần body                                                  |
| `400 Bad Request`           | Request sai/không hợp lệ   | Rule nghiệp vụ lỗi (không phải validation kiểu)                          |
| `401 Unauthorized`          | Thiếu/sai xác thực         | Thiếu/invalid token                                                      |
| `403 Forbidden`             | Không đủ quyền             | Token hợp lệ nhưng role/permission không cho phép                        |
| `404 Not Found`             | Không tìm thấy resource    | ID không tồn tại                                                         |
| `409 Conflict`              | Xung đột/vi phạm ràng buộc | Trùng unique, conflict state                                             |
| `422 Unprocessable Entity`  | **Validation lỗi**         | Rất phổ biến trong FastAPI khi body/query/path sai kiểu hoặc thiếu field |
| `500 Internal Server Error` | Lỗi server                 | Exception không xử lý                                                    |

> Lưu ý: 
> * `422`: Xuất hiện rất nhiều do Pydantic validate tự động
> * `400`: 
>   * Dù dữ liệu đúng kiểu, nhưng sai logic nghiệp vụ như `age < 18`, `amount < 0`, ...
>   * Dev chủ động raise exception với status code 400
> * `409`:
>   * Request hợp lệ nhưng xung đột với dữ liệu hiện có, ví dụ trùng dữ liệu (unique)
>   * Dev chủ động raise exception với status code 409

### 1.4.3 Headers & Body

* Headers (phổ biến):
  * Content-Type: application/json (khi gửi JSON body)
  * Accept: application/json
  * Authorization: Bearer <token>

* Body:
  * Trong REST hiện đại: chủ yếu là JSON
  * FastAPI parse JSON body vào Pydantic model để validate và dùng trong code

Ví dụ request body JSON:

```json
{
  "name": "An",
  "age": 20
}
```

FastAPI sẽ:
* Validate theo schema (`BaseModel`)
* Nếu sai => tự động trả `422` với chi tiết field lỗi

---

## 2) FastAPI

## 2.1 Cài đặt FastAPI & Uvicorn

FastAPI không chạy trực tiếp, mà cần một web server trung gian => `uvicorn`

### Lệnh cài đặt:

```bash
pip install fastapi uvicorn
```

Trong đó:
* `fastapi`: framework API
* `uvicorn`: server chạy ứng dụng FastAPI

---

## 2.2 Tạo file main.py

Tạo file **main.py** ở thư mục gốc dự án

```python
from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Hello World from FastAPI!"}
```

Giải thích từng dòng:

* `from fastapi import FastAPI` → import class FastAPI.
* `app = FastAPI()` → tạo ứng dụng chính.
* `@app.get("/")` → định nghĩa endpoint GET tại URL `/`.
* `read_root()` → hàm xử lý request; trả về JSON.

> FastAPI tự động convert Python dict → JSON.

---

## 2.3 Chạy server FastAPI với Uvicorn

Trong terminal:

```bash
uvicorn main:app --reload
```

Giải thích:

* `main` → tên file main.py
* `app` → biến app = FastAPI()
* `--reload` → tự reload server khi code thay đổi

### Sau khi chạy, terminal hiện:

```
Uvicorn running on http://127.0.0.1:8000
```

Truy cập:

* [http://127.0.0.1:8000](http://127.0.0.1:8000) → thấy JSON Hello World

---

## 2.4 Documentation tự động – Swagger UI & ReDoc

FastAPI tự sinh UI test API:

* Swagger UI: `http://127.0.0.1:8000/docs`
* ReDoc: `http://127.0.0.1:8000/redoc`

> Đây là lý do FastAPI rất mạnh: chỉ cần viết code, tài liệu API tự sinh chuẩn OpenAPI.

### Ví dụ giao diện Swagger:

* Thấy danh sách endpoint
* Nhấn vào endpoint `/` → Try it out → Execute → thấy response JSON

---

## 2.5 Thử tạo thêm endpoint Hello với tên người dùng

Thêm vào main.py:

```python
@app.get("/hello/{name}")
def say_hello(name: str):
    return {"message": f"Hello {name}!"}
```

Truy cập:

```
http://127.0.0.1:8000/hello/Thien
```

Kết quả:

```json
{"message": "Hello Thien!"}
```

> FastAPI tự parse kiểu dữ liệu → `name: str`.

---

## 2.6 Giải thích sâu hơn về Path Operation Decorator

Dòng:

```python
@app.get("/")
```

Gọi là **Path Operation Decorator**.
Trong FastAPI, mỗi endpoint = method HTTP + path.

Ví dụ:

* `@app.get("/")`
* `@app.post("/items")`
* `@app.put("/users/{user_id}")`

FastAPI dùng decorator để gắn hàm xử lý request.

---

## 2.7 Response tự động thành JSON

Trong FastAPI, chỉ cần return:

* dict
* list
* str
* int
* boolean

FastAPI + Pydantic tự convert thành JSON.

Ví dụ:

```python
return {"numbers": [1, 2, 3], "status": True}
```

Kết quả JSON:

```json
{
  "numbers": [1, 2, 3],
  "status": true
}
```

---

## 2.8 Thực hành

### BTTH1 – Tạo ứng dụng FastAPI đầu tiên

Yêu cầu:

1. Tạo file main.py
2. Tạo endpoint GET `/` trả về `{ "message": "Hello FastAPI" }`
3. Chạy server bằng `uvicorn main:app --reload`
4. Truy cập Swagger UI để test

---

### BTTH2 – Tạo endpoint với tên người dùng

Tạo endpoint:

```
GET /welcome/{name}
```

Trả về JSON:

```json
{ "welcome": "Xin chào {name}" }
```

---

### BTTH3 – Tạo endpoint trả về thời gian hiện tại

1. Import datetime
2. Tạo endpoint `/now`
3. Trả về JSON dạng:

```json
{
  "timestamp": "2025-01-01 10:20:30"
}
```

> Gợi ý: dùng `strftime` để format thời gian.

---

## 2.9 Kết luận phần Hello World

Học viên cần nắm được:

* Cách cài đặt FastAPI & Uvicorn
* Cách tạo file main.py và định nghĩa endpoint đầu tiên
* Cách chạy server với chế độ reload
* Biết sử dụng `/docs` để test API ngay lập tức
* Hiểu cách FastAPI tự convert JSON

> Đây là nền tảng để sang phần tiếp theo: **Path Parameters, Query Parameters, Request Body (Pydantic)** và CRUD API.

---

# 3) Path & Query Parameters (Chi tiết)

FastAPI hỗ trợ lấy dữ liệu từ URL theo hai dạng chính:

* **Path Parameters** → nằm trong URL, bắt buộc
* **Query Parameters** → sau dấu `?`, không bắt buộc (hoặc có giá trị mặc định)

---

## 3.1 Path Parameters

Dùng để định nghĩa phần **thay đổi** trong URL.

Ví dụ:

```python
@app.get("/items/{item_id}")
def get_item(item_id: int):
    return {"item_id": item_id}
```

Truy cập:

```
http://127.0.0.1:8000/items/10
```

Kết quả:

```json
{ "item_id": 10 }
```

### Giải thích:

* `{item_id}` là path param
* FastAPI tự convert kiểu nhờ annotation `item_id: int`
* Nếu truyền sai kiểu → FastAPI tự trả lỗi 422

Ví dụ 2 – nhiều tham số:

```python
@app.get("/users/{user_id}/orders/{order_id}")
def get_order(user_id: int, order_id: str):
    return {"user": user_id, "order": order_id}
```

---

## 3.2 Query Parameters

Nằm sau dấu `?` trong URL.

Ví dụ:

```python
@app.get("/search")
def search(keyword: str, limit: int = 10):
    return {"keyword": keyword, "limit": limit}
```

Truy cập:

```
http://127.0.0.1:8000/search?keyword=python&limit=5
```

### Tham số có giá trị mặc định

Nếu không truyền `limit`, sẽ dùng giá trị mặc định 10.

```
/search?keyword=fastapi
```

### Query param không bắt buộc

```python
@app.get("/filter")
def filter_items(category: str | None = None):
    return {"category": category}
```

---

## 3.3 Kết hợp Path + Query Parameters

```python
@app.get("/products/{product_id}")
def get_product(product_id: int, detailed: bool = False):
    return {
        "id": product_id,
        "detailed": detailed
    }
```

Ví dụ URL:

```
/products/8?detailed=true
```

---

## 3.4 Thực hành (BTTH)

### BTTH4 – Viết endpoint lấy thông tin sách

```
GET /books/{book_id}?include_author=true
```

Trả về JSON:

```json
{
  "id": 123,
  "include_author": true
}
```

---

### BTTH5 – Endpoint tìm kiếm người dùng

```
GET /users?name=an&age=20
```

Trả về đúng 2 tham số.

---

# 4) Pydantic Model – Request & Response

FastAPI dùng **Pydantic** để validate dữ liệu vào (request body) và chuẩn hóa dữ liệu ra (response).

---

## 4.1 Pydantic Model là gì?

Là class mô tả cấu trúc dữ liệu, dùng để:

* Kiểm tra dữ liệu đầu vào (validation)
* Gắn kiểu dữ liệu
* Tự động tạo tài liệu API

Ví dụ model User:

```python
from pydantic import BaseModel

class User(BaseModel):
    name: str
    age: int
```

---

## 4.2 Request Body – POST tạo mới dữ liệu

```python
@app.post("/users")
def create_user(user: User):
    return user
```

Gửi request body JSON:

```json
{
  "name": "An",
  "age": 20
}
```

FastAPI tự:

* parse JSON → object User
* validate dữ liệu (nếu age không phải số → 422)
* hiển thị model trong Swagger

---

## 4.3 Response Model – Chuẩn hóa dữ liệu trả về

```python
class UserOut(BaseModel):
    name: str
    age: int
    is_adult: bool

@app.post("/users", response_model=UserOut)
def create_user(user: User):
    return UserOut(
        name=user.name,
        age=user.age,
        is_adult=user.age >= 18,
    )
```

> response_model giúp API luôn trả về dữ liệu đúng format.

---

## 4.4 Thêm giá trị mặc định & kiểm tra nâng cao

```python
class Product(BaseModel):
    name: str
    price: float
    in_stock: bool = True
```

Pydantic hỗ trợ kiểm tra nâng cao bằng Field:

```python
from pydantic import Field

class Student(BaseModel):
    name: str
    score: float = Field(..., ge=0, le=10)
```

`score` phải nằm từ **0 đến 10**.

---

## 4.5 Thực hành Pydantic (BTTH)

### BTTH6 – Tạo model Book

Thuộc tính:

* title: str
* author: str
* year: int

Tạo endpoint POST `/books` nhận Book và trả lại Book.

---

### BTTH7 – Tạo response model cho Product

`ProductOut` có thêm trường `price_with_vat`.

---

# 5) In-memory CRUD API (Cực kỳ quan trọng)

Mục tiêu:

* Hiểu rõ cách CRUD hoạt động trong API.
* Quản lý dữ liệu trong RAM bằng list.
* Đây là nền để học CRUD với database ở Buổi 5.

---

## 5.1 Khởi tạo dữ liệu trong bộ nhớ

```python
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class Item(BaseModel):
    id: int
    name: str
    price: float

items: list[Item] = []  # database tạm
```

---

## 5.2 Create – POST /items

```python
@app.post("/items")
def create_item(item: Item):
    items.append(item)
    return item
```

---

## 5.3 Read – GET /items

```python
@app.get("/items")
def get_all_items():
    return items
```

Read by ID:

```python
@app.get("/items/{item_id}")
def get_item(item_id: int):
    for item in items:
        if item.id == item_id:
            return item
    return {"error": "Item not found"}
```

---

## 5.4 Update – PUT /items/{item_id}

```python
@app.put("/items/{item_id}")
def update_item(item_id: int, new_item: Item):
    for i, old_item in enumerate(items):
        if old_item.id == item_id:
            items[i] = new_item
            return new_item
    return {"error": "Item not found"}
```

---

## 5.5 Delete – DELETE /items/{item_id}

```python
@app.delete("/items/{item_id}")
def delete_item(item_id: int):
    for i, item in enumerate(items):
        if item.id == item_id:
            items.pop(i)
            return {"deleted": item_id}
    return {"error": "Item not found"}
```

---

## 5.6 Thực hành CRUD (BTTH)

### BTTH8 – CRUD Student

Model:

```python
class Student(BaseModel):
    id: int
    name: str
    score: float
```

Yêu cầu:

* POST /students
* GET /students
* GET /students/{id}
* PUT /students/{id}
* DELETE /students/{id}

---

### BTTH9 – CRUD Todo đơn giản

Model:

```python
class Todo(BaseModel):
    id: int
    task: str
    done: bool = False
```

API tương tự CRUD Item.

---

## 5.7 Tổng kết phần CRUD

Học viên cần nắm:

* Cấu trúc CRUD chuẩn của API
* Cách lưu trữ tạm bằng list (in-memory)
* Flow xử lý Request → Validate → CRUD → Response
* Chuẩn bị sẵn kiến thức để chuyển sang CRUD với database ở Buổi 5

---

## 5) In-memory CRUD API theo mô hình MVC (VIẾT LẠI TOÀN BỘ)

> Phần này được viết lại **theo tư duy MVC** để học viên hiểu đúng kiến trúc backend và chuẩn bị trực tiếp cho **Buổi 5: FastAPI + Database**.
>
> Lưu ý:
>
> * **Chưa dùng database**
> * Dữ liệu vẫn lưu trong bộ nhớ (list)
> * Nhưng **tách rõ vai trò: Model – Service – Controller**

---

### 5.1 Tổng quan MVC trong FastAPI

MVC (Model – View – Controller) là mô hình kiến trúc kinh điển của backend.

Ánh xạ MVC trong FastAPI:

| MVC        | Trong FastAPI                                       |
| ---------- | --------------------------------------------------- |
| Model      | Pydantic Model (Buổi 4) / SQLAlchemy Model (Buổi 5) |
| Controller | APIRouter (Endpoint)                                |
| Service    | Business Logic                                      |
| View       | JSON Response                                       |

> FastAPI không ép MVC, nhưng **dự án thực tế luôn tổ chức theo tư duy này**.

---

### 5.2 Cấu trúc thư mục (MVC giản lược)

```text
app/
│
├── main.py              # Entry point
│
├── models/
│   └── item.py          # Model (Pydantic)
│
├── services/
│   └── item_service.py  # Business logic (CRUD)
│
├── routers/
│   └── items.py         # Controller (API endpoints)
```

---

### 5.3 Model – Dữ liệu (M trong MVC)

File: `models/item.py`

```python
from pydantic import BaseModel

class Item(BaseModel):
    id: int
    name: str
    price: float
```

Giải thích:

* Model mô tả **cấu trúc dữ liệu**
* Không chứa logic HTTP
* Buổi 5: tách thành `schemas` và `models` (SQLAlchemy)

---

### 5.4 Service – Xử lý nghiệp vụ

File: `services/item_service.py`

```python
from models.item import Item

_items: list[Item] = []  # In-memory database


def create_item(item: Item) -> Item:
    _items.append(item)
    return item


def get_all_items() -> list[Item]:
    return _items


def get_item_by_id(item_id: int) -> Item | None:
    for item in _items:
        if item.id == item_id:
            return item
    return None


def update_item(item_id: int, new_item: Item) -> Item | None:
    for i, item in enumerate(_items):
        if item.id == item_id:
            _items[i] = new_item
            return new_item
    return None


def delete_item(item_id: int) -> bool:
    for i, item in enumerate(_items):
        if item.id == item_id:
            _items.pop(i)
            return True
    return False
```

Giải thích:

* Service **không biết gì về HTTP**
* Chỉ xử lý dữ liệu & nghiệp vụ

---

### 5.5 Controller – Router

File: `routers/items.py`

```python
from fastapi import APIRouter, HTTPException
from models.item import Item
from services import item_service

router = APIRouter(prefix="/items", tags=["Items"])

@router.post("")
def create(item: Item):
    return item_service.create_item(item)

@router.get("")
def get_all():
    return item_service.get_all_items()

@router.get("/{item_id}")
def get_by_id(item_id: int):
    item = item_service.get_item_by_id(item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    return item

@router.put("/{item_id}")
def update(item_id: int, item: Item):
    updated = item_service.update_item(item_id, item)
    if not updated:
        raise HTTPException(status_code=404, detail="Item not found")
    return updated

@router.delete("/{item_id}")
def delete(item_id: int):
    success = item_service.delete_item(item_id)
    if not success:
        raise HTTPException(status_code=404, detail="Item not found")
    return {"deleted": item_id}
```

---

### 5.6 main.py – Kết nối ứng dụng

```python
from fastapi import FastAPI
from routers import items

app = FastAPI()
app.include_router(items.router)
```

---

### 5.7 Luồng xử lý Request theo MVC

```text
Client
  ↓
Router (Controller)
  ↓
Service (Business Logic)
  ↓
Model (Data)
  ↓
JSON Response
```

---

### 5.8 Thực hành (BTTH – theo MVC)

**BTTH8 – CRUD Student theo MVC**

* Tạo `Student` model
* Tạo `student_service.py`
* Tạo `routers/students.py`
* Viết CRUD theo đúng MVC

---

### 5.9 Kết luận

Sau phần này, học viên cần:

* Hiểu rõ MVC trong FastAPI
* Phân biệt Controller / Service / Model
* Viết CRUD in-memory theo kiến trúc chuẩn
* Sẵn sàng chuyển sang CRUD với Database ở Buổi 5

> Từ đây, học viên đã có **tư duy backend thực tế**, không chỉ là viết endpoint.
