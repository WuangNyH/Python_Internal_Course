# Buổi 4 – FastAPI Fundamentals

## 1) Kiến trúc Web: Client–Server, HTTP lifecycle, REST stateless, MVC

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
3. FastAPI xử lý theo pipeline MVC/service-layer:
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
| `422 Unprocessable Entity`  | Validation lỗi             | Rất phổ biến trong FastAPI khi body/query/path sai kiểu hoặc thiếu field |
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

## 1.5 Mô hình MVC trong kiến trúc Web Backend

> MVC (Model – View – Controller) là mô hình kiến trúc dùng để tách biệt trách nhiệm trong ứng dụng web/backend:
> * Model: Dữ liệu + cấu trúc dữ liệu
> * View: Dữ liệu trả về cho client 
> * Controller: Nhận request, điều phối xử lý

Trong FastAPI framework:
* Không render HTML
* View = JSON trả về cho client (Web / Mobile)
* Thường gọi là `MVC + Service Layer`

| Thành phần              | Ý nghĩa         | Thành phần thực tế                                           |
|-------------------------|-----------------|--------------------------------------------------------------|
| View                    | JSON Response   | JSON Response                                                |
| Controller              | API Endpoint    | `APIRouter` / Endpoint (`@router.get`, `@router.post`)       |
| Model                   | Schema / Entity | Pydantic Model (request/response)<br/> SQLAlchemy Model (DB) |
| (Service – mở rộng MVC) | Logic nghiệp vụ | custom layer, không phải FastAPI cung cấp sẵn                |

Luồng xử lý chuẩn với `Controller mỏng – Service dày` trong dự án FastAPI thực tế:

```text
HTTP Request
  ↓
Middleware (auth, logging, cors)
  ↓
Controller (Router)
  ↓
Dependency Injection (DB, current_user)
  ↓
Service Layer (business logic)
  ↓
Model / Data
  ↓
JSON Response
```

---

## 2) FastAPI

## 2.1 Cài đặt FastAPI & Uvicorn

### 2.1.1: Virtual Environment (.venv)

> * `.venv`: môi trường Python riêng cho từng project
> * Mỗi project có bộ thư viện độc lập
> * Không ảnh hưởng Python hệ thống

* Tạo `.venv`:

```bash
    python -m venv .venv
```

* Kích hoạt `.venv`
  * Windows: 
    * PowerShell / CMD: `.\.venv\Scripts\activate`
    * Git Bash: `source .venv/Scripts/activate`
  * Linux/Mac: `source .venv/bin/activate`

Sau khi kích hoạt, terminal sẽ có (`.venv`)

* Lưu ý KHÔNG commit `(.venv)`
  * Không chia sẻ qua Git
  * Dùng `requirements.txt` để install thư viện
    * `pip install -r requirements.txt`

Trước đây có `pip` và `pip3` do Python 2/3, nhưng hiện nay dùng `.venv` nên chỉ cần `pip`

### 2.1.2 Cài đặt FastAPI trong .venv:

FastAPI không chạy trực tiếp, mà cần một web server trung gian => `uvicorn`

```bash
    pip install fastapi uvicorn
```

Trong đó:
* `fastapi`: framework API
* `uvicorn`: server chạy ứng dụng FastAPI

Tạo / cập nhật file `requirements.txt`:
* Sau khi đã cài các thư viện cần thiết => chạy lệnh:
  * `pip freeze > requirements.txt`
  * Trong đó:
    * `pip freeze`: tạo danh sách các gói thư viện theo format chuẩn
    ```text
        fastapi==0.124.2
        uvicorn==0.38.0
        pydantic==2.12.5
        starlette==0.50.0
        anyio==4.12.0
        ...
    ```
    * Toán tử `>` (của terminal): chuyển toàn bộ nội dung đó vào file `requirements.txt`

Như vậy các máy của dev khác chỉ cần kích hoạt `.venv` và chạy `pip install -r requirements.txt` để cài toàn bộ thư viện 

---

## 2.2 Tạo file main.py

Tạo file `main.py` ở thư mục gốc dự án

```python
from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Hello World from FastAPI!"}
```

Trong đó:
* `from fastapi import FastAPI`: import class FastAPI từ package `fastapi`
* `app = FastAPI()`: tạo ứng dụng chính
* `@app.get("/")`: định nghĩa endpoint `GET` tại URL `/`
* `read_root()`: hàm xử lý request, trả về JSON

> FastAPI tự động convert Python dict => JSON

---

## 2.3 Chạy server FastAPI với Uvicorn

Trong terminal:

```bash
    uvicorn app.main:app --host 127.0.0.1 --port 8000
```

Trong đó:
* `main`: tên file main.py
* `app`: biến app = FastAPI()
* `--reload`: tự reload server khi code thay đổi

Sau khi chạy, terminal hiện: `Uvicorn running on http://127.0.0.1:8000`

Truy cập `http://127.0.0.1:8000` => thấy JSON Hello World

### 2.3.1 FastAPI Dev Mode

Ở môi trường local của dev, có thể chạy bằng `fastapi dev main.py`, nhưng KHÔNG dùng khi deploy
* Là CLI helper của FastAPI
* Bọc bên ngoài uvicorn
* Chỉ dùng cho local development
  * Cần cài đặt "fastapi[standard]": `pip install "fastapi[standard]"`

### 2.3.2 Run bằng PyCharm

1. Chọn đúng Python Interpreter (.venv)
  * Python Interpreter => Add Interpreter => Chọn 'select existing interpreter'
  * Python path: (cuối path)
    * Windows: `.venv\Scripts\python.exe`
    * macOS/Linux: `.venv/bin/python`

2. Tạo Run Configuration cho FastAPI
  * Cấu hình các trường
    * Name: tùy ý (ví dụ: FastAPI)
    * Python interpreter: kiểm tra path đã trỏ đúng (.venv)
    * Module: `uvicorn`
    * Parameters: `main:app --host 127.0.0.1 --port 8000 --reload`
    * Working directory: thư mục project

---

## 2.4 Documentation tự động: Swagger UI & ReDoc

FastAPI tự generate UI để test API:
* Swagger UI: `http://127.0.0.1:8000/docs`
* ReDoc: `http://127.0.0.1:8000/redoc`

> Đây là lý do FastAPI rất mạnh: chỉ cần viết code, tài liệu API tự sinh theo chuẩn OpenAPI

---

## 2.5 Demo một số endpoint

Thêm vào main.py:

```python
@app.get("/hello/{name}")
def say_hello(name: str) -> dict[str, str]:
    return {"message": f"Hello {name}!"}


class ErrorResponse(BaseModel):
    detail: str


# Thêm mã lỗi 400 trên Swagger UI
@app.get("/calculate/sum",
         responses={
             400: {"model": ErrorResponse, "description": "Business validation error"}
         })
def calculate_sum(a: int, b: int) -> dict[str, int]:
    if a < 0 or b < 0:
        raise HTTPException(
            status_code=400,
            detail="Negative numbers are not allowed")

    return {
        "a": a,
        "b": b,
        "sum": a + b
    }
```

> FastAPI tự parse kiểu dữ liệu => `name: str`

---

## 2.6 Path Operation Decorator

> Dòng `@app.get("/")` là Path Operation Decorator

* Trong FastAPI, mỗi endpoint = method HTTP + path
* Ví dụ:
  * `@app.get("/")`
  * `@app.post("/items")`
  * `@app.put("/users/{user_id}")`
* FastAPI dùng decorator để gắn hàm xử lý request

---

## 2.7 Response tự động thành JSON

> Trong FastAPI, chỉ cần return `dict`, `list`, `str`, `int`, `boolean`
> => FastAPI + Pydantic tự convert thành JSON

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

# 3) Path & Query Parameters

> Trong FastAPI, **tham số từ URL** là một trong những cách quan trọng nhất để API nhận dữ liệu từ client <br>
> FastAPI hỗ trợ lấy dữ liệu từ URL theo hai dạng chính:

| Loại               | Vị trí        | Bắt buộc       | Mục đích sử dụng                    |
|--------------------|---------------|----------------|-------------------------------------|
| `Path Parameters`  | Nằm trong URL | Bắt buộc       | Xác định đối tượng cụ thể           |
| `Query Parameters` | Sau dấu `?`   | Không bắt buộc | Lọc, tìm kiếm, phân trang, tuỳ chọn |

---

## 3.1 Path Parameters

> Path Parameter là phần **biến động** của URL, dùng để xác định tài nguyên cụ thể

* Ví dụ:
  * `/items/10`
  * `/users/3/orders/A001`

Trong đó `10`, `3`, `A001` chính là path parameters

### 3.1.1 Cú pháp

`{item_id}` trong URL **phải trùng tên** với tham số trong hàm

```python
@app.get("/items/{item_id}")
def get_item(item_id: int) -> dict[str, int]:
    return {"item_id": item_id}
```

Kết quả trả về:

```json
{ "item_id": 10 }
```

### 3.1.2 Thông tin chi tiết

> `{item_id}` là path param

FastAPI tự thực hiện:
* Tự động parse theo type hint `item_id: int`, `-> dict[str, int]`
* Tự validate dữ liệu
* Tự generate Swagger UI
  * Nếu truyền sai kiểu => FastAPI tự trả lỗi 422 => không cần viết code validate thủ công
  ```json
    {
      "detail": [
        {
          "loc": ["path", "item_id"],
          "msg": "Input should be a valid integer",
          "type": "int_parsing"
        }
      ]
    }
  ```

### 3.1.3 Nhiều tham số `/users/5/orders/ORD001`

Thứ tự trong URL phải đúng như định nghĩa route:

```python
@app.get("/users/{user_id}/orders/{order_id}")
def get_order(user_id: int, order_id: str) -> dict[str, int | str]:
    return {"user": user_id, "order": order_id}
```

Kết quả:

```json
{
  "user_id": 5,
  "order_id": "ORD001"
}
```

Lưu ý nếu khai báo sai kiểu trả về `-> dict[str, str]` 
=> FastAPI ném lỗi `ResponseValidationError: 1 validation error: ...`

Path parameter luôn dùng để định danh tài nguyên trong RESTful API:
* `/users/1`: Lấy user có `id = 1`
* `/users/5/orders/ORD001`: Lấy đơn hàng cụ thể của user cụ thể

---

## 3.2 Query Parameters

Query Parameters là các tham số nằm sau dấu `?`, thường dùng cho:
* Tìm kiếm
* Lọc
* Sắp xếp
* Phân trang
* Tuỳ chọn hiển thị

Ví dụ: `/search?keyword=python&limit=5`

### 3.1.1 Cú pháp

```python
@app.get("/search")
def search(keyword: str, limit: int = 10):
    return {
        "keyword": keyword,
        "limit": limit
    }
```

Kết quả:

```json
{
  "keyword": "python",
  "limit": 5
}
```

### 3.1.2 Giá trị mặc định

```python
def search(keyword: str, limit: int = 10)
```

* `keyword`: bắt buộc
* `limit`: không bắt buộc
  * Nếu không truyền `limit`, sẽ dùng giá trị mặc định 10

FastAPI tự dùng giá trị mặc định khi gọi `/search?keyword=fastapi`:

```json
{
  "keyword": "fastapi",
  "limit": 10
}
```

### 3.1.3 Query param không bắt buộc (Optional)

```python
@app.get("/filter")
def filter_items(
        category: str | None = None,
        active: bool | None = None
) -> dict[str, str | bool | None]:
    return {
        "category": category,
        "active": active
    }
```

Trong đó:
* `str | None = None`: tương đương cách viết cũ `Optional[str] = None`
* `= None`: FastAPI hiểu là tham số không bắt buộc
  * Khi client không truyền param `GET /filter` => trả response `{"category": null, "active": null}`
* Cách dùng SAI: Không có `= None` => FastAPI coi là bắt buộc
  * Khi gọi `GET /filter` => trả lỗi 422 với `"msg": "Field required"`

---

## 3.3 Kết hợp Path + Query Parameters

> Patern này rất phổ biến trong dự án thực tế

Quy tắc:
* `Path param`: luôn bắt buộc
* `Query param`: tuỳ chọn, có default

```python
@app.get("/products/{product_id}")
def get_product(
        product_id: int,
        price_filter: float | None = None,
        detailed: bool = False
) -> dict[str, int | float | bool | None]:
    return {
        "id": product_id,
        "price": price_filter,
        "detailed": detailed
    }
```

---

## 3.4 Best Practices quan trọng

* Điều nên làm:
  * Dùng Path param cho `id`
  * Dùng Query param cho filter/search
  * Đặt type hint rõ ràng
  * Có default value cho query
* KHÔNG nên:
  * Dùng query để thay thế path id
  * Viết validate kiểu dữ liệu thủ công
  * Dùng `str` cho mọi tham số

---

# 4) Pydantic Model: Request & Response

> Trong FastAPI, Pydantic là trung tâm của việc validate dữ liệu<br>
> Pydantic sẽ validate dữ liệu vào (request body) và chuẩn hóa dữ liệu ra (response)

## 4.1 Bản chất Pydantic Model

Là class Python mô tả cấu trúc dữ liệu, dùng để:
* Kiểm tra dữ liệu đầu vào (type validation)
* Chuẩn hóa dữ liệu request / response
* Tự động tạo tài liệu OpenAPI / Swagger schema

## 4.2 Tại sao Controller KHÔNG nên dùng dict cho request body

```python
@app.post("/users")
def create_user(user: dict):
    return user
```

### 4.2.1 Vấn đề

* Không validate kiểu
* Không biết field nào bắt buộc
* Swagger không rõ ràng
* Lỗi chỉ xuất hiện lúc runtime

### 4.2.2 Patern chuẩn với Pydantic

Controller nhận Pydantic Model:

```python
from fastapi import APIRouter
from schemas.request.user_schema import UserCreate

user_router = APIRouter()


@user_router.post("/users")
def create_user(user: UserCreate):
    return user
```

```python
# main.py
from fastapi import FastAPI
from controllers.user_controller import user_router

app = FastAPI()

# Đăng ký router
app.include_router(user_router, prefix="/users", tags=["Users"])
```

FastAPI lúc này:
* Validate tự động
* Trả lỗi 422 nếu sai
* Tạo Swagger rõ ràng
* Code clean

---

## 4.2 Request Schema: Dữ liệu client gửi lên

Sử dụng `BaseModel` của Pydantic cho request schema để tự động:
* Validate dữ liệu (nếu sai => 422)
* Parse JSON => object `User`
* Generate schema (OpenAPI/Swagger)

```python
# schemas/request/user_schema.py
from pydantic import BaseModel

class UserCreate(BaseModel):
    name: str
    age: int
    address: str | None = None
```

Client gửi request body JSON (`address` là optional):

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

## 4.3 Response Schema: Chuẩn hóa dữ liệu trả về (View)

> Dùng Response Schema để tránh lộ dữ liệu các field nhạy cảm trong DB model như `password`

### 4.3.1 Cách làm SAI

```python
return {
    "id": 1,
    "name": "An",
    "age": 20,
    "password": "123456"
}
```

### 4.3.2 Patter chuẩn

Định nghĩa Response Schema: 

```python
# schemas/response/user_out_schema.py
from pydantic import BaseModel

# Ví dụ ko muốn lộ address
class UserOut(BaseModel):
    id: int
    name: str
    age: int
```

Đối với dự án lớn có thể tạo `BaseOutSchema` với mục đích:
* chứa field chung
* config chung

```python
from pydantic import BaseModel

class BaseOutSchema(BaseModel):
    id: int
    created_at: datetime | None = None
    updated_at: datetime | None = None

    class Config:
        from_attributes = True
```

```python
class UserOut(BaseOutSchema):
    name: str
    age: int
```

Tạo ErrorResponse để trả lỗi:

```python
# schemas/response/error_response.py
from pydantic import BaseModel

class ErrorResponse(BaseModel):
    detail: str
```

---

## 4.4 Controller: Nhận Request và trả Response bằng Pydantic

Controller mỏng:
* Không kiểm tra logic nghiệp vụ `age`
* Không validate kiểu
* Chỉ nhận request schema => gọi service => trả response schema 

```python
# controllers/user_controller.py
from fastapi import APIRouter
from schemas.request.user_schema import UserCreate
from schemas.response.error_response import ErrorResponse
from schemas.response.user_out_schema import UserOut
from services import user_service

user_router = APIRouter()


@user_router.post(
    "",
    status_code=201,
    response_model=UserOut,
    responses={
        400: {"model": ErrorResponse, "description": "Invalid input on business logic"}
    },
)
def create_user(user: UserCreate) -> UserOut:
    return user_service.create_user(user)
```

---

## 4.5 Service: Xử lý nghiệp vụ (KHÔNG dùng Pydantic để validate)

Flow xử lý service:
* Tin rằng dữ liệu đã đúng kiểu
* Chỉ xử lý logic nghiệp vụ
* Không cần biết gì về HTTP / status code

```python
# services/user_service.py
from fastapi import HTTPException
from schemas.request.user_schema import UserCreate
from schemas.response.user_out_schema import UserOut

_users: list[dict] = []
_id_counter = 1


def create_user(user: UserCreate) -> UserOut:
    global _id_counter

    # Validation nghiệp vụ (khác với validation kiểu dữ liệu của Pydantic)
    if user.age < 18:
        # Tạm sử dụng HTTPException của FastAPI, buổi sau tự tạo Custom Exception
        raise HTTPException(status_code=400, detail="Age must be >= 18")

    stored_user = {
        "id": _id_counter,
        "name": user.name,
        "age": user.age,
        "address": user.address,  # lưu nội bộ, nhưng không trả ra UserOut
    }

    _users.append(stored_user)
    _id_counter += 1

    return UserOut(
        id=stored_user["id"],
        name=stored_user["name"],
        age=stored_user["age"],
    )
```

---

## 4.6 Validation nâng cao trong Schema

> Validation cơ bản:
> * Kiểm tra kiểu dữ liệu (`int`, `str`, ...)
> * Kiểm tra bắt buộc / optional
>
> Validation nâng cao:
> * Kiểm tra ràng buộc dữ liệu (constraints), logic liên quan giữa các field, và custom rule, không chỉ là type

### 4.6.1 Validation bằng Field (ràng buộc 1 field)

1. Giới hạn số

```python
from pydantic import BaseModel, Field

class UserCreate(BaseModel):
    age: int = Field(ge=0, le=120)
```

* `gt=0`: > 0
* `ge=0`: >= 0
* `le=120`: <= 120

2. Chuỗi: độ dài, regex

```python
class UserCreate(BaseModel):
    name: str = Field(
        min_length=2,
        max_length=50,
        pattern=r"^[A-Za-z ]+$",
        description="User name (2-50 characters) contains only letters",
        examples=["Taro Kun"]
    )
    age: int = Field(ge=0)
    address: str | None = None
```

* `description`: mô tả cho Swagger
* `example`: giá trị example

### 4.6.2 Validation bằng type đặc biệt của Pydantic

```python
from pydantic import BaseModel, EmailStr, HttpUrl

class UserOut(BaseModel):
    email: EmailStr
    avatar_url: HttpUrl | None = None
```

### 4.6.3 Custom validation bằng validator

1. Validate 1 field bằng `field_validator`

```python
from pydantic import BaseModel, Field, field_validator

class UserCreate(BaseModel):
    name: str = Field(min_length=2, max_length=50)
    age: int = Field(ge=1, le=150)
    address: str | None = None

    @field_validator("name")
    @classmethod
    def name_not_empty(cls, v: str):
        if not v.strip():
            raise ValueError("Name cannot be empty")
        return v.strip()
```

2. Validate nhiều field cùng lúc bằng `model_validator`

```python
from datetime import date
from pydantic import BaseModel, model_validator

class BookingCreate(BaseModel):
    start_date: date
    end_date: date

    @model_validator(mode="after")
    def check_date_range(self):
        if self.start_date >= self.end_date:
            raise ValueError("end_date must be after start_date")
        return self
```

* `mode="before"`: validate ngay khi nhận raw input, dữ liệu chưa parse (thường là dict)
* `mode="after"` (dùng phổ biến): validate sau khi parse JSON
