# Buổi 6: Custom Exception & Exception Handler, Authen & Author, Pytest

## 1) Custom Exception & Exception Handler

### 1.1 Vấn đề khi dùng HTTPException trực tiếp trong Service

Code từ buổi 5 (tạm sử dụng):

```python
from fastapi import HTTPException, status

if not student:
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Student not found",
    )
```

Hạn chế nghiêm trọng:

| Vấn đề                       | Giải thích                                  |
|------------------------------|---------------------------------------------|
| Service phụ thuộc FastAPI    | Service **không còn thuần logic nghiệp vụ** |
| Khó test                     | Phải mock `HTTPException`                   |
| Khó tái sử dụng              | Không thể dùng Service ngoài HTTP context   |
| Không đồng bộ error response | Mỗi chỗ raise một kiểu                      |
| Khó mở rộng                  | Khi thêm error_code, trace_id, metadata     |

> Nguyên tắc kiến trúc: <br>
> Service không nên biết HTTP <br>
> Service chỉ nên raise domain exception

---

### 1.2 Phân loại Exception trong Backend chuẩn

#### 1.2.1 Nhóm 1: Business Exception (quan trọng nhất)

* Do rule nghiệp vụ
* Có thể dự đoán
* Client có thể sửa request để gửi lại

Ví dụ:
* Không tìm thấy dữ liệu
* Email đã tồn tại
* Tuổi < 18
* Không đủ quyền thao tác

#### 1.2.2 Nhóm 2 – System Exception

* Do lỗi hệ thống
* Không dự đoán trước 
* Client không tự sửa được

Ví dụ:
* DB mất kết nối
* Bug code
* Exception không catch

---

### 1.3 Thiết kế Custom Exception (Business Layer)

#### 1.3.1 Nguyên tắc thiết kế

* Exception độc lập FastAPI
* Chỉ mang:
  * Ý nghĩa nghiệp vụ
  * Metadata cần thiết
* Không chứa HTTP logic

#### 1.3.2 Base Exception Nghiệp vụ

Tạo file `core/exceptions/base.py`:

```python
# core/exceptions/base.py
class BusinessException(Exception):
    """
    Base class for entire business exception
    """

    def __init__(
        self,
        *,
        message: str,
        error_code: str,
        status_code: int = 400,
        extra: dict | None = None,
    ):
        self.message = message
        self.error_code = error_code
        self.status_code = status_code
        self.extra = extra or {}
        super().__init__(message)
```

Giải thích chi tiết:
* `message`: thông báo cho client
* `error_code`: mã lỗi nghiệp vụ (rất quan trọng cho frontend)
* `status_code`: HTTP status sẽ map ở handler
* `extra`: metadata bổ sung (debug / log)

---

### 1.4 Custom Exception cụ thể

Tạo file ``

```python
# core/exceptions/student_exception.py
from core.exceptions.base import BusinessException


class StudentNotFoundException(BusinessException):
    def __init__(self, student_id: int):
        super().__init__(
            message=f"Student {student_id} not found",
            error_code="STUDENT_NOT_FOUND",
            status_code=404,
            extra={"student_id": student_id},
        )


class StudentEmailAlreadyExistsException(BusinessException):
    def __init__(self, email: str):
        super().__init__(
            message="Email already exists",
            error_code="EMAIL_ALREADY_EXISTS",
            status_code=409,
            extra={"email": email},
        )


class InvalidStudentAgeException(BusinessException):
    def __init__(self, age: int):
        super().__init__(
            message="Age must be >= 18",
            error_code="INVALID_STUDENT_AGE",
            status_code=400,
            extra={"age": age},
        )
```

---

### 1.5 Refactor Service Layer dùng Custom Exception

#### 1.5.1 Refactor StudentService

```python
from sqlalchemy.orm import Session

from core.exceptions.student_exception import StudentNotFoundException, InvalidStudentSearchAgeRangeException, \
    StudentEmailAlreadyExistsException, InvalidStudentAgeException
from models.student import Student
from repositories.student_repository import StudentRepository
from schemas.request.student_schema import StudentCreate, StudentUpdate

import logging

logger = logging.getLogger(__name__)


class StudentService:

    def __init__(self):
        self.repo = StudentRepository()

    # -------- READ --------
    def get_student(self, db: Session, student_id: int) -> Student:
        student = self.repo.get_by_id(db, student_id)
        if not student:
            raise StudentNotFoundException(student_id)
        return student

    def list_students(self, db: Session, offset: int = 0, limit: int = 100) -> list[Student]:
        return self.repo.list(db, offset=offset, limit=limit)

    def search_students(
            self,
            db: Session,
            *,
            keyword: str | None = None,
            min_age: int | None = None,
            max_age: int | None = None,
            offset: int = 0,
            limit: int = 100,
    ) -> list[Student]:
        # Rule nghiệp vụ đơn giản: min_age không được lớn hơn max_age
        if min_age is not None and max_age is not None and min_age > max_age:
            raise InvalidStudentSearchAgeRangeException(min_age, max_age)

        return self.repo.search(
            db,
            keyword=keyword,
            min_age=min_age,
            max_age=max_age,
            offset=offset,
            limit=limit,
        )

    # -------- WRITE --------
    def create_student(self, db: Session, data: StudentCreate) -> Student:
        # Rule nghiệp vụ: email unique
        existed = self.repo.get_by_email(db, str(data.email))
        if existed:
            raise StudentEmailAlreadyExistsException(str(data.email))

        # Rule nghiệp vụ: tuổi hợp lệ
        if data.age < 18:
            raise InvalidStudentAgeException(data.age)

        student = Student(**data.model_dump())
        return self.repo.create(db, student)

    # PATCH
    def update_student(self, db: Session, student_id: int, data: StudentUpdate) -> Student:
        student = self.get_student(db, student_id)

        # Rule nghiệp vụ: không cho update age dưới 18
        if data.age is not None and data.age < 18:
            raise InvalidStudentAgeException(data.age)

        # exclude_unset=True: chỉ lấy field client gửi
        updated_data = data.model_dump(exclude_unset=True)

        return self.repo.update(db, student, updated_data)

    def delete_student(self, db: Session, student_id: int) -> None:
        student = self.get_student(db, student_id)
        self.repo.delete(db, student)
```

Kết quả đạt được:
* Service không import FastAPI
* Dễ test
* Rõ ràng nghiệp vụ
* Chuẩn bị tốt cho Pytest

---

### 1.6 Chuẩn hóa Error Response Schema

```python
# schemas/response/error_response.py
from pydantic import BaseModel


class ErrorResponse(BaseModel):
    success: bool = False
    error_code: str
    message: str
    trace_id: str | None = None
    extra: dict | None = None
```

---

### 1.7 Global Exception Handler

BusinessException Handler là nơi duy nhất trong hệ thống:
* Bắt các lỗi nghiệp vụ (business rule)
* Chuyển lỗi đó thành HTTP response chuẩn
* Trả lỗi đồng nhất cho client

Nhờ đó:
> Service chỉ “ném lỗi” => Handler là nơi dịch lỗi sang HTTP

Nếu KHÔNG có BusinessException Handler, chúng ta buộc phải làm thế này:

```python
try:
    service.create_student(...)
except InvalidStudentAgeException:
    raise HTTPException(status_code=400, detail="Age must be >= 18")
except StudentNotFoundException:
    raise HTTPException(status_code=404, detail="Student not found")
```

Hậu quả:
* Router đầy `try/except`
* Mỗi API xử lý lỗi một kiểu
* Rất khó bảo trì
* Code dài và rối

=> BusinessException Handler sinh ra để giải quyết vấn đề này

#### 1.7.1 Vị trí của BusinessException Handler trong kiến trúc

Luồng xử lý:

```
Client
  ↓
Router
  ↓
Service
  ↓
raise BusinessException
  ↓
BusinessException Handler  <= ở đây
  ↓
HTTP Response (JSON)
```

Lưu ý quan trọng:
* Router KHÔNG bắt lỗi
* Service KHÔNG biết HTTP
* Handler đứng giữa hai thế giới

---

#### 1.7.2 BusinessException Handler

```python
# core/exceptions/exception_handlers.py
from fastapi import Request
from fastapi.responses import JSONResponse

from core.exceptions.base import BusinessException
from schemas.response.base import ErrorResponse


async def business_exception_handler(
    request: Request,
    exc: BusinessException,
):
    trace_id = getattr(request.state, "trace_id", None)

    response = ErrorResponse(
        error_code=exc.error_code,
        message=exc.message,
        trace_id=trace_id,
        extra=exc.extra,
    )

    return JSONResponse(
        status_code=exc.status_code,
        content=response.model_dump(),
    )
```

Giải thích chi tiết:
* `exc: BusinessException`: handler nhận `BusinessException` => handler bắt được tất cả
  * Bất kỳ exception nào:
    * `StudentNotFoundException`
    * `InvalidStudentAgeException`
    * `InvalidSearchAgeRangeException`
  * đều kế thừa từ `BusinessException`
* `request`: cho phép handler truy cập thông tin của request hiện tại
  * Lấy được:
    * `trace_id`: bằng cách `getattr(request.state, "trace_id", None)`
      * Mỗi request có một `trace_id` riêng
      * Dùng để debug & tracking log
    * user (sau này)
    * request path
* `return JSONResponse`: Handler phải trả raw HTTP response
  * Không dùng `response_model` ở đây
  * Đây là tầng infrastructure, không phải API contract
  * `status_code=exc.status_code`: Mapping `BusinessException` => HTTP Response
    * Service KHÔNG cần biết HTTP, nhưng vẫn trả đúng HTTP code
  * `content=response.model_dump()`: dùng ErrorResponse để build body cho `JSONResponse.content`

> Best practice:
> * Router: trả `SuccessResponse[T]` khi thành công
> * Service: raise `BusinessException`
> * Exception handler: chuyển `BusinessException` => `FailedResponse` (body) + `status_code` (HTTP)

---

#### 1.7.3 Catch-all Exception Handler (System Error)

Đây là handler dùng để:
* Bắt mọi lỗi không mong muốn
* Những lỗi KHÔNG phải lỗi nghiệp vụ
* Tránh việc server trả về lỗi “vỡ trang” hoặc stacktrace cho client

> Quy tắc cần nhớ:
> * BusinessException => lỗi do người dùng / nghiệp vụ
> * Catch-all Exception => lỗi do hệ thống / bug / hạ tầng

1. Các System Error trong thực tế (các lỗi này không phải do client):
* Lỗi code (`NoneType has no attribute ...`)
* Lỗi SQL (constraint, syntax, timeout)
* Lỗi DB mất kết nối
* Lỗi logic chưa lường trước
* Lỗi bên thứ ba (API timeout)

=> Client không thể sửa request để hết lỗi

2. Vấn đề khi KHÔNG có Catch-all Handler:
Mặc định FastAPI sẽ:
* Trả `500 Internal Server Error`
* Có thể:
  * Log không đầy đủ
  * Trả stacktrace (ở debug)
  * Response không đúng format chung

=> Hậu quả:
* Frontend không parse được lỗi
* Log khó trace
* Không đồng bộ với `BusinessException`

3. Vị trí của Catch-all Handler trong hệ thống
Luồng xử lý:

```
Client
  ↓
Router
  ↓
Service
  ↓
Exception (không được xử lý)
  ↓
Catch-all Exception Handler  <= ở đây
  ↓
HTTP 500 + FailedResponse
```

=> Đây được coi là lưới an toàn cuối cùng của hệ thống

4. Tạo hàm `unhandled_exception_handler`:

```python
async def unhandled_exception_handler(
    request: Request,
    exc: Exception,
):
    trace_id = getattr(request.state, "trace_id", None)

    logger.exception("Unhandled exception", exc_info=exc)

    response = ErrorResponse(
        error_code="INTERNAL_SERVER_ERROR",
        message="Internal server error",
        trace_id=trace_id,
    )

    return JSONResponse(
        status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
        content=response.model_dump(),
    )
```

Giải thích chi tiết:
* `Exception`: cha của mọi loại lỗi => tuyến phòng ngự cuối cùng
  * Nếu ko có nó, lỗi sẽ trôi lên tự do => khó kiểm soát
* `logger.exception(...)`: lưu ý KHÔNG bao giờ trả stacktrace cho client => nguyên tắc bảo mật bắt buộc
* `ErrorResponse.message`: nội dung message lỗi loại này phải chung chung vì:
  * Không lộ:
    * cấu trúc DB
    * logic code
    * thông tin hệ thống
  * Tránh lỗ hổng bảo mật
  * Client chỉ cần biết “có lỗi hệ thống”

---

#### 1.7.4 Tổng hợp Business vs System Error

| Tiêu chí        | BusinessException | Catch-all Exception |
|-----------------|-------------------|---------------------|
| Nguyên nhân     | Rule nghiệp vụ    | Bug / hệ thống      |
| Client sửa được | OK                | NG                  |
| Status code     | 4xx               | 500                 |
| Message         | Rõ ràng           | Chung chung         |
| Log             | Info / Warning    | Error + Stacktrace  |

---

### 1.8 Đăng ký Exception Handler trong `main.py`

Thứ tự rất quan trọng:
1. `BusinessException`
2. `Exception` (catch-all)

Lý do:
* FastAPI chọn handler theo độ cụ thể
* Nếu bắt `Exception` trước:
  * `BusinessException` sẽ bị nuốt
  * Client luôn nhận `500`

```python
# Đăng ký Exception Handler => thứ tự bắt buộc
app.add_exception_handler(BusinessException, business_exception_handler)
app.add_exception_handler(Exception, unhandled_exception_handler)
```

---

### 1.9 Một số quy ước log

1. Ko nên log lỗi nghiệp vụ ở tầng Service
> Service layer chỉ nên có 1 nhiệm vụ duy nhất: <br>
> Kiểm tra rule nghiệp vụ => nếu sai thì raise BusinessException

2. Lỗi nghiệp vụ nên log ở đâu
   * Nên log ở Exception Handler (nếu cần)
Nhưng lưu ý: KHÔNG phải lúc nào cũng log

3. Mặc định: KHÔNG cần thiết phải log BusinessException
   * Vì BusinessException xảy ra rất thường xuyên (như nhập sai pass, ...) => gây nhiễu log
   * Clien cũng đã nhận error response rồi

4. Khi NÀO thì nên log BusinessException
Chỉ log khi:
   * Business error bất thường
   * Có dấu hiệu:
     * bị user nào đó lạm dụng
     * data inconsistency
     * nghi ngờ bug nghiệp vụ

Ví dụ log có kiểm soát:

```python
if exc.error_code.startswith("SECURITY_"):
    logger.warning(
        "Security-related business error",
        extra={
            "error_code": exc.error_code,
            "extra": exc.extra,
            "trace_id": trace_id,
        },
    )
```

=> Log có điều kiện, không log tràn lan

Quy tắc log cần nhớ:

| Loại sự kiện                  | Log ở đâu            | Mức log            |
|-------------------------------|----------------------|--------------------|
| Business rule fail (expected) | Không log            | —                  |
| Business rule bất thường      | Exception handler    | WARNING            |
| System error / bug            | Catch-all handler    | ERROR              |
| DB / infra lỗi                | Catch-all handler    | ERROR + stacktrace |
| Security violation            | Handler / middleware | WARNING / ERROR    |

---

## 2) Authentication & Authorization (JWT)

### 2.1 Khái niệm

#### 2.1.1 Authentication (Authen)

Xác định người dùng là ai:

* Kết quả: một identity (`user_id`, `tenant_id`, `roles`/`scopes` ...)

#### 2.1.2 Authorization (Author)

Kiểm tra người dùng được quyền làm gì trên tài nguyên nào:

* Kết quả: `allow`/`deny` (RBAC/ABAC), kèm policy và audit

#### 2.1.3 Phân biệt 401 vs 403

* `401 Unauthorized`: thiếu token / token sai / token hết hạn 
* `403 Forbidden`: token hợp lệ nhưng không đủ quyền

> 401 = “chưa đăng nhập đúng” <br>
> 403 = “đăng nhập rồi nhưng không có quyền”

---

### 2.2 JWT (JSON Web Token)

JWT gồm 3 phần: Header – Payload (Claims) – Signature

#### 2.2.1 Access token vs Refresh token

* Access token: sống ngắn (5–15 phút)
* Refresh token: sống dài (7–30 ngày hoặc hơn) để cấp lại access token

#### 2.2.2 Thông tin xác thực (claims) tối thiểu

Trong access token cần có thông tin (pattern chuẩn enterprise):

* `sub` (Subject): Đại diện cho danh tính chính của token, luôn map với `user_id` (field bắt buộc)
  * `user_id` ở model `User` đang kiểu `int`, dự án thực tế cần đổi sang dùng `UUID`
* `exp` (Expiration Time): thời hạn token
* `iat` (Issued At): thời điểm token được tạo
* (tùy dự án có/ko) `iss`, `aud`
  * `iss` (Issuer): ai phát hành token, ví dụ:
    * Token từ Google => `iss = https://accounts.google.com`
    * Token nội bộ => `iss = auth-service`
  * `aud` (Audience): token dành cho service nào
    * Mỗi service chỉ accept token có `aud` phù hợp, ví dụ auth server cấp token cho:
      * `student-api`
      * `order-api`
* `roles` hoặc `permissions`/`scopes`
  * `roles`: Role-based Authorization (RBAC)
  * `permissions`/`scopes`: Permission-based Authorization
* `tid` (`tenant_id`): Xác định user thuộc tổ chức nào

Mẫu JWT chuẩn:

```json
{
  "sub": "123",
  "iat": 1712340000,
  "exp": 1712340900,
  "iss": "https://auth.mycompany.com",
  "aud": "student-api",
  "roles": ["teacher"],
  "permissions": ["student:read", "student:write"],
  "tid": "company_001"
}
```

---

### 2.3 Kiến trúc chuẩn tách lớp

#### A) Edge / API Layer

* Router chỉ khai báo endpoint cần gì
* Dùng dependency để:
  * lấy `CurrentUser`
  * check permission/policy
* Không nhúng logic JWT/role trực tiếp trong router

#### B) Auth Module (Security Layer)

* Token verification (JWT)
* Load user (từ DB/cache)
* Build Principal / CurrentUser
* Expose dependency: `get_current_user()`

#### C) Authorization Module (Policy Layer)

* RBAC: role-based (`admin`, `teacher`, `viewer`)
* ABAC: attribute-based (owner check, tenant check, resource state)
* Expose dependency: `require_permission("student:write")` hoặc `authorize(policy, resource)`

#### D) Domain/Service Layer

* Service vẫn có thể thêm business authorization nếu cần (khi rule nghiệp vụ phức tạp)
* Thường policy check ở API layer để fail fast

---

### 2.4 Các loại token phổ biến

#### Option 1 (phổ biến nhất): OAuth2 + JWT Access Token

* Access token ngắn hạn (5–15 phút)
* Refresh token dài hạn (7–30 ngày)
* Chuẩn enterprise:
  * dễ rotate keys
  * dễ tích hợp SSO (Single Sign-On: đăng nhập một lần, truy cập được nhiều hệ thống khác nhau mà không cần đăng nhập lại)
  * microservice-friendly

#### Option 2: Session (cookie-based)

* Phù hợp hệ thống web truyền thống (SSR)
* Nhưng khó scale cho mobile/microservices nếu không có shared store

> Với FastAPI backend kiểu API, thường chọn Access JWT + Refresh

---

### 2.5 Authorization chuẩn: kết hợp RBAC + ABAC

#### 2.5.1 RBAC (role)

* admin: full
* staff: write
* viewer: read

#### 2.5.2 ABAC (attribute)

* “Owner can update own profile”
* “User chỉ xem dữ liệu trong tenant của mình”
* “Chỉ sửa student thuộc lớp mình quản lý”

> Patter enterprise thường dùng: <br>
> * RBAC để coarse-grained: quyền ở mức thô, rộng => “Role này có được phép vào API / chức năng này không?”
> * ABAC để fine-grained: quyền chi tiết, theo ngữ cảnh => “Trong điều kiện hiện tại, người này có được phép không?”

#### 2.5.3 Ví dụ kết hợp RBAC + ABAC

> Bài toán thực tế: Ai được sửa thông tin student?

RBAC (coarse)

```text
admin, teacher => được vào API update student
user => bị chặn
```

ABAC (fine)

```text
teacher chỉ được sửa student do mình phụ trách
admin sửa tất cả
```

Logic minh họa

```python
# RBAC (coarse)
if user.role not in ["admin", "teacher"]:
    deny()

# ABAC (fine)
if user.role == "teacher" and student.teacher_id != user.id:
    deny()
```

---

### 2.6 Triển khai Authen/Author trong FastAPI

#### 2.6.1 Dependency: `get_current_user()`

* Parse `Authorization: Bearer <token>`
* Verify token + exp + aud/iss
* Load user từ DB/cache (đảm bảo user chưa bị disable)
* Trả về `CurrentUser` (principal)

#### 2.6.2 Dependency: `require_permissions([...])`

* Nhận `CurrentUser`
* Check permission/role
* Nếu fail: raise `ForbiddenException`

#### 2.6.3 Pattern exception chuẩn

* `AuthTokenMissingException` (401): thiếu token
* `ForbiddenException` (403): token OK nhưng không đủ quyền
* `InvalidTokenException` (401)
* `TokenExpiredException` (401)

=> Tất cả kế thừa `BusinessException` để đi qua exception handler

---

### 2.7 Các hạng mục Security

* Password hashing: bcrypt/argon2 (không bao giờ lưu plain text)
* Refresh token:
  * store hashed refresh token (hoặc token id)
  * revoke/rotate khi refresh
* Rate limit login
* Audit log (ít nhất cho: login fail, permission denied)
* CORS policy rõ ràng
* HTTPS bắt buộc (môi trường PROD)
* “Least privilege” cho permissions
  * không cấp dư
  * không cho tiện
  * không “để sau sửa”

---

### 2.8 Kiến trúc Hybrid (Middleware + Depends)

#### 2.8.1 Mục đích của Hybrid

* **Middleware**: chạy cho mọi request, làm việc cross-cutting cho toàn requests
  * tạo `trace_id`
  * parse token (nếu có) => gắn `claims` vào `request.state`
  * không query DB, không check quyền, không chặn request (hoặc chỉ chặn rất hạn chế)
* **Depends**: enforce chặn theo từng route
  * `get_current_user()` => `401` nếu thiếu/invalid token, có thể load user DB
  * `require_permissions(...)` => `403` nếu thiếu quyền
  * hỗ trợ ABAC (owner/tenant/resource)

#### 2.8.2 Sơ đồ luồng xử lý

```
Client (request)
  ↓
[TraceIdMiddleware]  -> request.state.trace_id
  ↓
[TokenContextMiddleware] -> request.state.token_claims
  - đọc token nếu có
  - verify chữ ký + decode claims
  - request.state.token_claims = claims | None
  ↓
Router (FastAPI)
  ↓
Depends:
  - get_current_user() -> 401 nếu thiếu/invalid token, (optional) load user DB
  - require_permissions(...) -> RBAC/ABAC check -> 403 nếu thiếu quyền
  ↓
Service (business logic) -> raise BusinessException
  ↓
Exception Handlers -> ErrorResponse + trace_id
  ↓
Response (body + X-Trace-Id header)
```

#### 2.8.3 TokenContextMiddleware (chỉ parse token, không enforce)

Trách nhiệm:
* đọc token từ header/cookie
* verify chữ ký, decode claims
* set `request.state.token_claims = claims | None`

Không làm:
* không query DB
* không check permission
* không quyết định `401`/`403` cho mọi route

---

### 2.9 Code triển khai

#### 2.9.1 Data model cho RBAC

Bảng cần thiết:
* `users`
* `roles`
* `permissions`
* `user_roles` (N-N)
* `role_permissions` (N-N)

SQLAlchemy models:

```python
# models/associations.py
from sqlalchemy import Table, Column, ForeignKey, UniqueConstraint

from models.base import Base

# Base.metadata dùng để khai báo table thuần
user_roles = Table(
    "user_roles",
    Base.metadata,
    Column("user_id", ForeignKey("users.id", ondelete="CASCADE"), primary_key=True),
    Column("role_id", ForeignKey("roles.id", ondelete="CASCADE"), primary_key=True),
    UniqueConstraint("user_id", "role_id", name="uq_user_role"),
)

role_permissions = Table(
    "role_permissions",
    Base.metadata,
    Column("role_id", ForeignKey("roles.id", ondelete="CASCADE"), primary_key=True),
    Column("permission_id", ForeignKey("permissions.id", ondelete="CASCADE"), primary_key=True),
    UniqueConstraint("role_id", "permission_id", name="uq_role_permission"),
)
```

```python
# models/role.py
from typing import TYPE_CHECKING

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models.base import Base
from models.associations import user_roles, role_permissions
from models.time_mixin import TimeMixin

if TYPE_CHECKING:
    from models.user import User
    from models.permission import Permission


class Role(TimeMixin, Base):
    __tablename__ = "roles"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)

    users: Mapped[list[User]] = relationship(
        secondary=user_roles,
        back_populates="roles",
        lazy="selectin",
    )

    permissions: Mapped[list[Permission]] = relationship(
        secondary=role_permissions,
        back_populates="roles",
        lazy="selectin",
    )
```

```python
# models/user.py
from typing import TYPE_CHECKING

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models.base import Base
from models.associations import user_roles
from models.time_mixin import TimeMixin

if TYPE_CHECKING:
    from models.role import Role


class User(TimeMixin, Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(nullable=False)
    is_active: Mapped[bool] = mapped_column(nullable=False, default=False)
    token_version: Mapped[int] = mapped_column(nullable=False, default=1)

    roles: Mapped[list[Role]] = relationship(
        secondary=user_roles,
        back_populates="users",
        lazy="selectin",
    )
```

```python
# models/permission.py
from typing import TYPE_CHECKING

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models.base import Base
from models.associations import role_permissions
from models.time_mixin import TimeMixin

if TYPE_CHECKING:
    from models.role import Role


class Permission(TimeMixin, Base):
    __tablename__ = "permissions"

    id: Mapped[int] = mapped_column(primary_key=True)
    code: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)

    roles: Mapped[list[Role]] = relationship(
        secondary=role_permissions,
        back_populates="permissions",
        lazy="selectin",
    )
```

Giải thích chi tiết:
* Cần import trong `if TYPE_CHECKING` để tránh circular import:
  * `TYPE_CHECKING`: hằng số đặc biệt trong module typing
    * Compile time (IDE/Type checker): `TYPE_CHECKING=True`
    * Run time (Python runtime): `TYPE_CHECKING=False`
  * Chỉ import model quan hệ ở compile time => giúp IDE hiểu kiểu dữ liệu của model quan hệ (ví dụ `Role`) 
  * Ko import model quan hệ khi Python chạy chương trình thật => tránh lỗi import vòng lặp 
* `users: Mapped[list[User]] = relationship(...)`: Một Role có thể được gán cho NHIỀU User
  * Quan hệ N–N giữa `User` và `Role` => `role.users`: list tất cả user đang có role này
  * `relationship(...)`: ko tạo cột mới trong DB, chỉ dùng để liên kết các bảng lại với nhau trong code => cho phép viết `role.users`, `user.roles`
    * `secondary=user_roles`: `User` và `Role` ko nối trực tiếp với nhau, mà nối qua bảng trung gian `user_roles`
    * `back_populates="roles"`: tạo liên kết 2 chiều giữa 2 model
      * Bên `Role`: `role.users`
      * Bên `User` (phải có): `user.roles`
    * `lazy="selectin"`: cách dữ liệu được load từ DB (giúp tránh N+1 problem)
      * SQLAlchemy sẽ load Role trước
      * Khi cần users sẽ chạy 1 query bổ sung cho tất cả role
      * Nếu ko có `lazy="selectin"`: 
        * Khi truy cập `role.users`
        * SQLAlchemy có thể chạy thêm nhiều query lặp => N+1 problem
* `token_version`: dùng cho cơ chế soft-revoke token
  * Tăng `token_version` trong DB để:
    * vô hiệu hoá tất cả access token cũ của user
    * không cần chờ access token hết hạn
  * Các tình huống thực tế:
    * User đổi mật khẩu
    * Admin khóa/mở tài khoản
    * User logout toàn bộ thiết bị
    * Phát hiện token bị lộ

Tạo thêm model cho refresh_token:

```python
# models/refresh_session.py
from datetime import datetime

from sqlalchemy import (
    ForeignKey,
    String,
    DateTime,
    Index,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models.base import Base
from models.time_mixin import TimeMixin


class RefreshSession(TimeMixin, Base):
    __tablename__ = "refresh_sessions"

    id: Mapped[int] = mapped_column(primary_key=True)

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # ---- Token storage (hash only) ----
    token_hash: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        unique=True,
        comment="Hashed refresh token (never store plain token)",
    )

    # ---- Lifecycle ----
    # Nếu user không refresh trong expires_at phút -> hết session -> login lại
    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )
    
    # Dù refresh liên tục, sau absolute_expires_at ngày kể từ login -> hết session
    absolute_expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )

    revoked_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    rotated_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    # ---- Metadata (tùy dự án) ----
    # Quản lý đa thiết bị / đa phiên đăng nhập (Chrome / Windows ...)
    user_agent: Mapped[str | None] = mapped_column(String(255), nullable=True)
    ip_address: Mapped[str | None] = mapped_column(String(45), nullable=True)

    # ---- Relationship ----
    user = relationship("User", lazy="selectin")

    __table_args__ = (
        UniqueConstraint("token_hash", name="uq_refresh_sessions_token_hash"),
        Index("ix_refresh_sessions_user_active", "user_id", "revoked_at"),
    )
```

---

#### 2.9.2 Password Hashing

Cài thư viện `argon2`:

```bash
    pip install passlib[argon2-cffi]
```

Tạo Password utility:

```python
# security/password.py
from passlib.context import CryptContext

_pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")


def hash_password(plain_password: str) -> str:
    if not plain_password or plain_password.strip() == "":
        raise ValueError("Password must not be empty")  # Tầng service sẽ xử lý
    return _pwd_context.hash(plain_password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    if not plain_password or not hashed_password:
        return False
    return _pwd_context.verify(plain_password, hashed_password)


def needs_rehash(hashed_password: str) -> bool:
    if not hashed_password:
        return False
    return _pwd_context.needs_update(hashed_password)
```

Giải thích chi tiết:
* `CryptContext(schemes=["bcrypt"], deprecated="auto")`: khởi tạo context
  * `schemes=["bcrypt"]`: dùng thuật toán hash chuyên cho password, gồm các thành phần:
    * auto salt: mỗi password tự sinh salt => không trùng
    * adaptive cost: có thể tăng độ khó theo thời gian
  * `deprecated="auto"`: cho phép đánh dấu hash cũ là không an toàn
* `.verify(plain_password, hashed_password)`: so sánh password user nhập và password đã hash trong DB
* `needs_rehash(hashed_password: str)`: tư duy chuẩn enterprise
  * Hệ thống tự nâng cấp bảo mật (ví dụ hiện tại `bcrypt cost = 10` lên `cost = 12`)
  * Đáp ứng được yêu cầu "ko thể bắt user đổi password hàng loạt"
    ```python
        if verify_password(password, user.hashed_password):
            if needs_rehash(user.hashed_password):
                user.hashed_password = hash_password(password)
                db.commit()
    ```

---

#### 2.9.3 Schemas cho login và logout

```python
# schemas/request/login_schema.py
from pydantic import BaseModel, EmailStr, Field


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=1, max_length=128)
```

```python
# schemas/response/login_out_schema.py
from pydantic import BaseModel


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "Bearer"
    expires_in: int  # seconds
```

```python
# schemas/auth/logout_out_schema.py
from pydantic import BaseModel


class LogoutAllResult(BaseModel):
    revoked_sessions: int
```

> Pattern chuẩn cho Web App <br>
> * `access_token`: trả luôn trong body => giúp client toàn quyền quản lý `access_token`
> * `refresh_token`: ko trả trong body, set vào cookie => tránh bị đánh cắp `refresh_token`
> * Login trả token, không trả full user profile
>   * Lấy profile thì gọi endpoint `/me`

---

#### 2.9.4 AuthRepository & RefreshSessionRepository

AuthRepository: query user + snapshot roles/permissions

```python
# repositories/auth_repository.py
from sqlalchemy.orm import Session, selectinload
from sqlalchemy import select

from models.user import User
from models.role import Role


class AuthRepository:
    def get_user_credentials_by_email(self, db: Session, email: str) -> User | None:
        stmt = select(User).where(User.email == email)
        return db.execute(stmt).scalars().first()

    def get_authz_snapshot(self, db: Session, user_id: int) -> tuple[list[str], list[str], int]:
        stmt = (
            select(User)
            .where(User.id == user_id)
            .options(
                selectinload(User.roles).selectinload(Role.permissions)
            )
        )
        user = db.execute(stmt).scalars().first()
        if not user:
            # Service sẽ quyết định raise gì
            return [], [], 0

        roles = [r.name for r in user.roles]
        permissions = sorted({p.code for r in user.roles for p in r.permissions})
        token_version = getattr(user, "token_version", 1)
        return roles, permissions, token_version
```

* `selectinload(User.roles)`: cơ chế load dữ liệu thông minh để tránh N+1, SQLAlchemy sẽ làm các bước:
  * Bước 1: chạy query chính `SELECT * FROM users;`
    * Kết quả: `users = [User(id=1), User(id=2),]`
    * Lúc này SQLAlchemy chưa load roles
  * Bước 2: nội bộ SQLAlchemy tự chạy truy vấn bảng trung gian `user_roles`
    * `SELECT user_id, role_id FROM user_roles WHERE user_id IN (1, 2);`
    * Kết quả được danh sách role: `list_of_role_ids = [10, 20]`
  * Bước 3: chạy query phụ `SELECT * FROM roles WHERE roles.id IN (10, 20);`
  * Bước 4: ORM tự ghép dữ liệu lại từ kết quả bảng trung gian
    * `User(id=1).roles = [Role(id=10), Role(id=20)]`
    * `User(id=2).roles = [Role(id=20)]`

RefreshSessionRepository: thao tác với bảng `refresh_sessions`

```python
# repositories/refresh_session_repository.py
from datetime import datetime, timezone
from typing import Final

from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from models.refresh_session import RefreshSession


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class RefreshSessionRepository:
    MODEL: Final = RefreshSession

    # Create / Issue
    def create_session(
            self,
            db: Session,
            *,
            user_id: int,
            token_hash: str,
            expires_at: datetime,
            absolute_expires_at: datetime,
            user_agent: str | None = None,
            ip_address: str | None = None,
            now: datetime | None = None,
    ) -> RefreshSession:
        now = now or _utcnow()

        session = RefreshSession(
            user_id=user_id,
            token_hash=token_hash,
            expires_at=expires_at,
            absolute_expires_at=absolute_expires_at,
            user_agent=user_agent,
            ip_address=ip_address,
            created_at=now,
            updated_at=now,
        )
        db.add(session)
        db.flush()  # lấy session.id ngay trong transaction
        return session

    # Read / Validate
    def get_active_by_token_hash(
            self,
            db: Session,
            *,
            token_hash: str,
            now: datetime | None = None,
            for_update: bool = False,
    ) -> RefreshSession | None:
        """
        Lấy refresh session còn hiệu lực:
        - token_hash match
        - revoked_at is NULL
        - expires_at > now

        for_update=True dùng cho flow refresh/rotate để tránh race-condition
        """
        now = now or _utcnow()

        stmt = (
            select(RefreshSession)
            .where(
                RefreshSession.token_hash == token_hash,
                RefreshSession.revoked_at.is_(None),
                RefreshSession.expires_at > now,
                RefreshSession.absolute_expires_at > now,
            )
        )

        if for_update:
            stmt = stmt.with_for_update(of=RefreshSession)

        return db.execute(stmt).scalars().first()

    # Rotate
    def rotate_session(
            self,
            db: Session,
            *,
            old_token_hash: str,
            new_token_hash: str,
            new_expires_at: datetime,
            now: datetime | None = None,
    ) -> RefreshSession | None:
        """
        Rotate refresh token theo pattern enterprise:
        - Lock row theo old_token_hash (FOR UPDATE) để tránh concurrent refresh
        - Nếu session không còn active -> return None
        - Update token_hash + expires_at + rotated_at + updated_at

        Lưu ý: rotate theo kiểu "update-in-place" (1 row)
        Do token_hash unique, new_token_hash phải chưa tồn tại
        """
        now = now or _utcnow()

        # Lock & validate session
        current = self.get_active_by_token_hash(
            db,
            token_hash=old_token_hash,
            now=now,
            for_update=True,
        )
        if not current:
            return None

        # Update tại chỗ
        current.token_hash = new_token_hash
        current.rotated_at = now
        current.updated_at = now
        # Gia hạn expires_at nhưng KHÔNG vượt quá absolute_expires_at
        current.expires_at = min(new_expires_at, current.absolute_expires_at)

        db.flush()
        return current

    # Revoke
    def revoke_by_token_hash(
            self,
            db: Session,
            *,
            token_hash: str,
            now: datetime | None = None,
    ) -> bool:
        """
        Revoke 1 session theo token_hash
        """
        now = now or _utcnow()

        session = self.get_active_by_token_hash(
            db,
            token_hash=token_hash,
            now=now,
            for_update=True,
        )
        if not session:
            return False

        session.revoked_at = now
        session.updated_at = now
        db.flush()
        return True

    def revoke_all_for_user(
            self,
            db: Session,
            *,
            user_id: int,
            now: datetime | None = None,
    ) -> int:
        """
        Revoke tất cả session của 1 user (logout all devices)
        Return: số session bị revoke
        """
        now = now or _utcnow()

        stmt = (
            select(RefreshSession)
            .where(
                RefreshSession.user_id == user_id,
                RefreshSession.revoked_at.is_(None),
            )
            .with_for_update()
        )

        sessions = db.execute(stmt).scalars().all()
        if not sessions:
            return 0

        for s in sessions:
            s.revoked_at = now
            s.updated_at = now

        db.flush()
        return len(sessions)

    # Cleanup
    def delete_expired_sessions(
            self,
            db: Session,
            *,
            before: datetime | None = None,
    ) -> int:
        """
        Dọn dẹp session hết hạn (enterprise chạy cron/job)
        Return: số session bị xóa
        """
        before = before or _utcnow()

        # Lấy danh sách id cần xóa
        id_stmt = select(RefreshSession.id).where(
            (RefreshSession.expires_at <= before) |
            (RefreshSession.absolute_expires_at <= before)
        )
        ids = db.execute(id_stmt).scalars().all()
        if not ids:
            return 0

        # Xóa theo ids (an toàn, không phụ thuộc rowcount)
        del_stmt = delete(RefreshSession).where(RefreshSession.id.in_(ids))
        db.execute(del_stmt)

        return len(ids)
```

---

#### 2.9.5 JWT service (verify/decode)

Cài đặt thư viện JWT: có 2 thư viện phổ biến `python-jose` / `PyJWT`
* Hiện tại `python-jose` được sử dụng gần như mặc định cho FastAPI vì có nhiều tính năng ưu việt hơn

```bash
    pip install "python-jose[cryptography]"
```

Tạo JWT service (Access token only):

```python
# security/jwt_service.py
from datetime import datetime, timedelta, timezone
from typing import Any

from jose import jwt
from jose.exceptions import ExpiredSignatureError, JWTError

from configs.settings.security import JwtSettings


class JwtService:
    def __init__(self, settings: JwtSettings):
        self._settings = settings

    def create_access_token(
        self,
        *,
        subject: str,
        token_version: int = 1,
        extra_claims: dict[str, Any] | None = None,
    ) -> str:
        now = datetime.now(timezone.utc)

        payload: dict[str, Any] = {
            "sub": subject,
            "iss": self._settings.issuer,
            "aud": self._settings.audience,
            "iat": now,
            "exp": now + timedelta(minutes=self._settings.access_token_ttl_minutes),
            "tv": token_version,
        }
        if extra_claims:
            payload.update(extra_claims)

        return jwt.encode(
            payload,
            self._settings.secret_key.get_secret_value(),
            algorithm=self._settings.algorithm,
        )

    def decode_access_token(self, token: str) -> tuple[dict[str, Any] | None, str | None]:
        try:
            claims = jwt.decode(
                token,
                self._settings.secret_key.get_secret_value(),
                algorithms=[self._settings.algorithm],
                audience=self._settings.audience,
                issuer=self._settings.issuer,
                options={
                    "require_aud": True,
                    "require_iss": True,
                },
            )
            return claims, None
        except ExpiredSignatureError:
            return None, "expired"
        except JWTError:
            return None, "invalid"
```

**Lưu ý**: Đối với các dòng dự án cần bảo mật cao => thường dùng RS256 + JWKS

---

#### 2.9.6 Quản lý Refresh token

Util tạo token + hash:

```python
# security/refresh_token.py
import secrets
import hashlib

def generate_refresh_token() -> str:
    # 43~86 chars: đủ mạnh
    return secrets.token_urlsafe(64)

def hash_refresh_token(token: str) -> str:
    # DB chỉ lưu hash (che dấu token)
    return hashlib.sha256(token.encode("utf-8")).hexdigest()
```

Chuẩn hoá set cookie:

```python
# security/cookie_policy.py
from fastapi import Response

from configs.settings.security import RefreshCookieSettings


class RefreshCookiePolicy:
    def __init__(self, settings: RefreshCookieSettings):
        self._settings = settings

    @property
    def name(self) -> str:
        return self._settings.name

    @property
    def path(self) -> str:
        return self._settings.path

    def set(self, response: Response, token: str) -> None:
        response.set_cookie(
            key=self._settings.name,
            value=token,
            httponly=True,
            secure=self._settings.secure,
            samesite=self._settings.samesite,
            max_age=self._settings.max_age_seconds,
            path=self._settings.path,
        )

    def clear(self, response: Response) -> None:
        response.delete_cookie(key=self._settings.name, path=self._settings.path)
```

Cấu hình các thông tin dành cho security:

```python
# configs/settings/security.py
from typing import Literal
from pydantic import BaseModel, ConfigDict, Field, SecretStr

from configs.settings.cors import CorsSettings

SameSite = Literal["lax", "strict", "none"]
JwtAlgorithm = Literal["HS256", "RS256"]


class JwtSettings(BaseModel):
    """
    JWT policy:
    - HS256: dùng secret key (internal)
    - RS256: dùng private/public key (SSO/microservices)
    """
    model_config = ConfigDict(frozen=True)

    algorithm: JwtAlgorithm = Field(default="HS256")
    secret_key: SecretStr | None = None  # HS256
    issuer: str = Field(default="techzen-company")
    audience: str = Field(default="academy-api")

    access_token_ttl_minutes: int = Field(default=15)


class RefreshSessionSettings(BaseModel):
    """
    Refresh session policy:
    - TTL tính theo minutes (đồng bộ với env)
    - rotate_on_refresh: luôn rotate để chống replay
    """
    model_config = ConfigDict(frozen=True)

    ttl_minutes: int = Field(default=60 * 24 * 14)
    rotate_on_refresh: bool = Field(default=True)


class RefreshCookieSettings(BaseModel):
    """
    Settings cho refresh token cookie:
    - path: đặt ở scope /api hoặc /api/v1/auth (tránh hard-code endpoint cụ thể /refresh)
    - secure=True trong prod (HTTPS)
    - samesite=strict nếu same-site; nếu cross-site SPA thì thường phải cân nhắc none+lax tùy kiến trúc
    """

    model_config = ConfigDict(frozen=True)

    name: str = Field(default="refresh_token")
    path: str = Field(default="/api/v1/auth")  # cookie chỉ gửi cho các route /auth
    secure: bool = Field(default=True)  # secure=true: cookie CHỈ được gửi qua HTTPS
    samesite: SameSite = Field(default="strict")  # dùng để giảm nguy cơ CSRF (Cross-Site Request Forgery)
    max_age_seconds: int = Field(default=60 * 60 * 24 * 14)  # 14 days


class SecuritySettings(BaseModel):
    """
    Nhóm cấu hình security, có thể mở rộng thêm:
    - cookie_domain
    - etc...
    """

    model_config = ConfigDict(frozen=True)

    jwt: JwtSettings  # vì JwtSettings có field required -> được map từ env trong Settings
    refresh_session: RefreshSessionSettings = Field(default_factory=RefreshSessionSettings)
    refresh_cookie: RefreshCookieSettings = Field(default_factory=RefreshCookieSettings)
    cors: CorsSettings = Field(default_factory=CorsSettings)
```

* `SameSite`: cấu hỉnh để trình duyệt biết cách xử lý "Khi request đến từ site khác, có gửi cookie hay không?" (CSRF)
  * `SameSite=Strict`: cấp bảo mật chặt nhất
    * Browser chỉ gửi cookie nếu:
      * user truy cập trực tiếp site
    * KHÔNG gửi cookie nếu:
      * click link từ site khác
      * request đến từ iframe / form / fetch cross-site
  * `SameSite=Lax`: cấu hình mức bảo mật cân bằng (là default của browser)
    * Gửi cookie khi:
      * user click link `GET` từ site khác
    * KHÔNG gửi cookie khi:
      * `POST` / `PUT` / `DELETE` cross-site
      * fetch / ajax cross-site
  * `SameSite=None`: mức bảo mật mở nhất
    * Gửi cookie trong mọi request
    * Bao gồm cross-site, iframe, SSO
    * CHỈ dùng cho các trường hợp:
      * Frontend và Backend khác domain
      * SSO

```python
# configs/env.py
from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field

from configs.settings.security import SecuritySettings


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    environment: str = Field(..., validation_alias="ENVIRONMENT")
    database_url: str = Field(..., validation_alias="DATABASE_URL")
    security: SecuritySettings = Field(default_factory=SecuritySettings)

    jwt_algorithm: str = Field(default="HS256", validation_alias="JWT_ALGORITHM")
    jwt_secret_key: str = Field(..., validation_alias="JWT_SECRET_KEY")
    jwt_issuer: str = Field(..., validation_alias="JWT_ISSUER")
    jwt_audience: str = Field(..., validation_alias="JWT_AUDIENCE")
    
    access_token_expired_minutes: int = Field(..., validation_alias="ACCESS_TOKEN_EXPIRED_MINUTES")

    tz: str = Field(default="UTC", validation_alias="TZ")

    pool_size: int = Field(default=10, validation_alias="DB_POOL_SIZE")
    max_overflow: int = Field(default=20, validation_alias="DB_MAX_OVERFLOW")


@lru_cache
def settings_config() -> Settings:
    # noinspection PyArgumentList
    return Settings()
```

Tạo factory DI provider để lấy policy từ Settings:

```python
# security/dependencies.py
from functools import lru_cache

from configs.env import settings_config
from security.cookie_policy import RefreshCookiePolicy


@lru_cache
def get_refresh_cookie_policy() -> RefreshCookiePolicy:
    settings = settings_config()
    return RefreshCookiePolicy(settings.security.refresh_cookie)
```

---

#### 2.9.7 Cấu hình CORS (Cross-Origin Resource Sharing)

> CORS là một cơ chế bảo mật của trình duyệt web với cách hoạt động theo các bước sau:
> 1. Ví dụ Web client chạy tại: http://localhost:5173 và gọi `GET http://127.0.0.1:8000/students?offset=0&limit=100` 
> 2. Browser xác định đây là request cross-origin vì khác host và port
> 3. Browser quyết định có cần preflight (OPTIONS) không
>    * Method: `GET` => OK
>    * Có header `Authorization`
>    * => cần gửi preflight
> 4. Browser gửi request `OPTIONS` (preflight)
>    * Browser chưa gửi GET thật, mà gửi trước preflight để xin phép:

```http request
OPTIONS /students?offset=0&limit=100 HTTP/1.1
Host: 127.0.0.1:8000
Origin: http://localhost:5173
Access-Control-Request-Method: GET
Access-Control-Request-Headers: Authorization
```

> 5. CORS Middleware của FastAPI xử lý OPTIONS
>   * CORS middleware chạy ngoài cùng:
>     * Bắt request OPTIONS
>     * KHÔNG đi vào router
>     * KHÔNG cần DB
>     * KHÔNG cần auth
>   * Middleware đối chiếu cấu hình để so sánh với `CorsSettings`:
>     * `Origin` có thuộc `allow_origins` ko
>     * `GET` có thuộc `allow_methods` ?
>     * `Authorization` có thuộc `allow_headers` ?
>     * Nếu tất cả khớp => cho phép
> 6. Server trả response cho preflight 

```http
HTTP/1.1 200 OK
Access-Control-Allow-Origin: http://localhost:5173
Access-Control-Allow-Methods: GET,POST,PUT,PATCH,DELETE,OPTIONS
Access-Control-Allow-Headers: Authorization,Content-Type
Access-Control-Allow-Credentials: true
Access-Control-Max-Age: 600
```

> 7. Browser quyết định: CHO PHÉP hay CHẶN
>   * Browser kiểm tra response:
>     * Có Access-Control-Allow-Origin khớp origin gửi đi
>     * Có Authorization trong Allow-Headers
>     * Có Allow-Credentials (vì request có credentials)
>   * Nếu thiếu 1 header => browser CHẶN tại đây => `GET` thật KHÔNG bao giờ được gửi
>   * Nếu đủ tất cả => gửi `GET` thật đi

Cấu hình CORS:
* Chỉ allow đúng origin của SPA, không dùng `*`
* Bật `allow_credentials=True` vì dùng cookie (refresh token)
* Preflight (OPTIONS) phải đi qua được (KHÔNG chặn `OPTIONS` bằng auth)
* Khai báo headers cần thiết: `Authorization`, `Content-Type`, `X-Trace-Id`
* Expose header để client đọc X-Trace-Id

1. Tạo CORS settings theo chuẩn config-driven:

```python
# configs/settings/cors.py
from pydantic import BaseModel, ConfigDict, Field


class CorsSettings(BaseModel):
    """
    CORS settings (enterprise):
    - allow_origins: whitelist origin của SPA, KHÔNG dùng '*'
    - allow_credentials=True để browser gửi cookie (refresh token)
    - expose_headers: để FE đọc X-Trace-Id
    """
    model_config = ConfigDict(frozen=True)

    enabled: bool = Field(default=True)

    # môi trường prod: ["https://app.company.com"]
    # dev: ["http://localhost:5173", "http://localhost:3000"]
    allow_origins: list[str] = Field(default_factory=list)

    allow_methods: list[str] = Field(default_factory=lambda: [
        "GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"
    ])

    # Header FE gửi:
    # - Authorization (access token)
    # - Content-Type
    allow_headers: list[str] = Field(default_factory=lambda: [
        "Authorization", "Content-Type"
    ])

    # Header FE cần đọc:
    expose_headers: list[str] = Field(default_factory=lambda: [
        "X-Trace-Id"
    ])

    allow_credentials: bool = Field(default=True)

    # Cache preflight 10 phút
    max_age: int = Field(default=600)
```

2. Mở rộng SecuritySettings để có `cors`:

```python
# configs/settings/security.py
from typing import Literal
from pydantic import BaseModel, ConfigDict, Field

from configs.settings.cors import CorsSettings

SameSite = Literal["lax", "strict", "none"]


class RefreshCookieSettings(BaseModel):
    """
    Settings cho refresh token cookie:
    - path: đặt ở scope /api hoặc /api/v1/auth (tránh hard-code endpoint cụ thể /refresh)
    - secure=True trong prod (HTTPS)
    - samesite=strict nếu same-site; nếu cross-site SPA thì thường phải cân nhắc none+lax tùy kiến trúc
    """

    model_config = ConfigDict(frozen=True)

    name: str = Field(default="refresh_token")
    path: str = Field(default="/api/v1/auth")  # cookie chỉ gửi cho các route /auth
    secure: bool = Field(default=True)  # secure=true: cookie CHỈ được gửi qua HTTPS
    samesite: SameSite = Field(default="strict")  # dùng để giảm nguy cơ CSRF (Cross-Site Request Forgery)
    max_age_seconds: int = Field(default=60 * 60 * 24 * 14)  # 14 days


class SecuritySettings(BaseModel):
    """
    Nhóm cấu hình security, có thể mở rộng thêm:
    - access_token_ttl_seconds
    - refresh_token_ttl_seconds
    - cookie_domain
    - etc...
    """

    model_config = ConfigDict(frozen=True)

    refresh_cookie: RefreshCookieSettings = Field(default_factory=RefreshCookieSettings)
    cors: CorsSettings = Field(default_factory=CorsSettings)
```

3. Cấu hình values theo môi trường (prod/dev)

```dotenv
# file .env
API_PREFIX=/api/v1

ENVIRONMENT=DEV

DATABASE_URL=postgresql+psycopg2://postgres:123456%40root@localhost:5432/techzen_academy
TZ=Asia/Ho_Chi_Minh
DB_POOL_SIZE=10
DB_MAX_OVERFLOW=20

JWT_ALGORITHM=HS256
JWT_SECRET_KEY=techzen-academy-example-secret-key
JWT_ISSUER=techzen-company
JWT_AUDIENCE=techzen-academy-api

ACCESS_TOKEN_EXPIRED_MINUTES=15
REFRESH_SESSION_TTL_MINUTES=20160
REFRESH_SESSION_ABSOLUTE_TTL_MINUTES=43200

REFRESH_COOKIE_SECURE=false
REFRESH_COOKIE_SAMESITE=lax
REFRESH_COOKIE_PATH=/api/v1/auth
REFRESH_COOKIE_MAX_AGE_SECONDS=1209600

CORS_ALLOW_ORIGINS=http://localhost:5173,http://localhost:3000
```

```python
# configs/env.py
from functools import lru_cache
from typing import Any

from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, SecretStr

from configs.settings.cors import CorsSettings
from configs.settings.security import SecuritySettings, SameSite, JwtSettings, JwtAlgorithm, RefreshCookieSettings, \
    RefreshSessionSettings


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    api_prefix: str = Field(default="/api/v1", validation_alias="API_PREFIX")
    environment: str = Field(..., validation_alias="ENVIRONMENT")
    database_url: str = Field(..., validation_alias="DATABASE_URL")

    cors_allow_origins_raw: str | None = Field(default=None, validation_alias="CORS_ALLOW_ORIGINS")

    jwt_algorithm: JwtAlgorithm = Field(default="HS256", validation_alias="JWT_ALGORITHM")
    jwt_secret_key: SecretStr = Field(..., validation_alias="JWT_SECRET_KEY")
    jwt_issuer: str = Field(..., validation_alias="JWT_ISSUER")
    jwt_audience: str = Field(..., validation_alias="JWT_AUDIENCE")
    access_token_expired_minutes: int = Field(default=15, validation_alias="ACCESS_TOKEN_EXPIRED_MINUTES")
    refresh_token_expired_minutes: int = Field(default=20160, validation_alias="REFRESH_SESSION_TTL_MINUTES")
    refresh_token_absolute_expired_minutes: int = Field(default=43200,
                                                        validation_alias="REFRESH_SESSION_ABSOLUTE_TTL_MINUTES")
    refresh_cookie_secure: bool | None = Field(default=None, validation_alias="REFRESH_COOKIE_SECURE")
    refresh_cookie_samesite: SameSite | None = Field(default=None, validation_alias="REFRESH_COOKIE_SAMESITE")
    refresh_cookie_path: str | None = Field(default=None, validation_alias="REFRESH_COOKIE_PATH")
    refresh_cookie_max_age_seconds: int | None = Field(default=None, validation_alias="REFRESH_COOKIE_MAX_AGE_SECONDS")

    security: SecuritySettings | None = Field(default=None)

    tz: str = Field(default="UTC", validation_alias="TZ")

    pool_size: int = Field(default=10, validation_alias="DB_POOL_SIZE")
    max_overflow: int = Field(default=20, validation_alias="DB_MAX_OVERFLOW")

    # Pydantic hook để mapping CORS origins, JWT, refresh session TTL, refresh cookie settings
    def model_post_init(self, __context):
        # Validate & normalize api_prefix
        if not self.api_prefix.startswith("/"):
            raise ValueError("Invalid API_PREFIX: must start with '/'")
        if self.api_prefix != "/" and self.api_prefix.endswith("/"):
            self.api_prefix = self.api_prefix.rstrip("/")

        # Derive refresh cookie path if not provided
        if not self.refresh_cookie_path:
            self.refresh_cookie_path = f"{self.api_prefix}/auth"

        # Build security settings
        jwt_settings = self._build_jwt_settings()
        cors_settings = self._build_cors_settings()
        refresh_session_settings = self._build_refresh_session_settings()
        refresh_cookie_settings = self._build_refresh_cookie_settings()

        # Compose full SecuritySettings
        self.security = SecuritySettings(
            jwt=jwt_settings,
            cors=cors_settings,
            refresh_session=refresh_session_settings,
            refresh_cookie=refresh_cookie_settings,
        )

    def _build_cors_settings(self) -> CorsSettings:
        base = CorsSettings()
        if not self.cors_allow_origins_raw:
            return base

        origins = [o.strip() for o in self.cors_allow_origins_raw.split(",") if o.strip()]
        return base.model_copy(update={"allow_origins": origins})

    def _build_jwt_settings(self) -> JwtSettings:
        issuer = (self.jwt_issuer or "").strip()
        audience = (self.jwt_audience or "").strip()
        secret = self.jwt_secret_key.get_secret_value().strip()

        if not issuer:
            raise ValueError("Invalid JWT config: JWT_ISSUER must not be empty")
        if not audience:
            raise ValueError("Invalid JWT config: JWT_AUDIENCE must not be empty")
        if not secret:
            raise ValueError("Invalid JWT config: JWT_SECRET_KEY must not be empty")
        if self.access_token_expired_minutes <= 0:
            raise ValueError("Invalid JWT config: ACCESS_TOKEN_EXPIRED_MINUTES must be > 0")

        return JwtSettings(
            algorithm=self.jwt_algorithm,
            secret_key=self.jwt_secret_key,
            issuer=issuer,
            audience=audience,
            access_token_ttl_minutes=self.access_token_expired_minutes,
        )

    def _build_refresh_session_settings(self) -> RefreshSessionSettings:
        if self.refresh_token_expired_minutes <= 0:
            raise ValueError("Invalid refresh session config: REFRESH_SESSION_TTL_MINUTES must be > 0")
        if self.refresh_token_absolute_expired_minutes <= 0:
            raise ValueError("Invalid refresh session config: REFRESH_SESSION_ABSOLUTE_TTL_MINUTES must be > 0")
        if self.refresh_token_absolute_expired_minutes < self.refresh_token_expired_minutes:
            raise ValueError("Invalid refresh session config: ABSOLUTE_TTL must be >= TTL (idle timeout)")

        base = RefreshSessionSettings()
        return base.model_copy(
            update={
                "ttl_minutes": self.refresh_token_expired_minutes,
                "absolute_ttl_minutes": self.refresh_token_absolute_expired_minutes,
            }
        )

    def _build_refresh_cookie_settings(self) -> RefreshCookieSettings:
        base = RefreshCookieSettings()

        updates: dict[str, Any] = {}
        if self.refresh_cookie_secure is not None:
            updates["secure"] = self.refresh_cookie_secure
        if self.refresh_cookie_samesite is not None:
            updates["samesite"] = self.refresh_cookie_samesite
        if self.refresh_cookie_path:
            updates["path"] = self.refresh_cookie_path.strip()
        if self.refresh_cookie_max_age_seconds is not None:
            if self.refresh_cookie_max_age_seconds <= 0:
                raise ValueError("Invalid cookie config: REFRESH_COOKIE_MAX_AGE_SECONDS must be > 0")
            updates["max_age_seconds"] = self.refresh_cookie_max_age_seconds

        cookie = base.model_copy(update=updates) if updates else base

        # Cross-field validate
        if cookie.samesite == "none" and cookie.secure is not True:
            raise ValueError("Invalid cookie policy: SameSite=None requires Secure=true")

        return cookie


@lru_cache
def settings_config() -> Settings:
    # noinspection PyArgumentList
    return Settings()
```

4. Thêm CORSMiddleware trong main.py:

```python
# main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from configs.env import settings_config
from controllers.health_controller import health_router
from controllers.student_controller import student_router
from controllers.user_controller import user_router
from core.app_logging import setup_logging
from core.exceptions.base import BusinessException
from core.exceptions.exception_handlers import business_exception_handler, unhandled_exception_handler
from core.middlewares.db_session import DBSessionMiddleware
from core.middlewares.trace_id import TraceIdMiddleware

app = FastAPI()

settings = settings_config()
setup_logging(sql_echo=(settings.environment == "DEV"))

# Đăng ký router
app.include_router(health_router, tags=["Health"])
app.include_router(user_router, prefix="/users", tags=["Users"])
app.include_router(student_router, prefix="/students", tags=["Students"])

# Đăng ký Exception Handler => thứ tự bắt buộc
app.add_exception_handler(BusinessException, business_exception_handler)
app.add_exception_handler(Exception, unhandled_exception_handler)

# Đăng ký middleware => thứ tự quan trọng
app.add_middleware(DBSessionMiddleware)
app.add_middleware(TraceIdMiddleware)  # add sau để bọc ngoài

# CORS middleware (OUTERMOST)
cors = settings.security.cors
if cors.enabled:
    # Guard: khi dùng cookie (allow_credentials=True) thì không được phép allow_origins="*"
    if cors.allow_credentials and ("*" in cors.allow_origins):
        raise RuntimeError(
            "CORS misconfig: allow_credentials=True cannot be used with allow_origins='*'"
        )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=cors.allow_origins,
        allow_credentials=cors.allow_credentials,
        allow_methods=cors.allow_methods,
        allow_headers=cors.allow_headers,
        expose_headers=cors.expose_headers,
        max_age=cors.max_age,
    )
```

---

#### 2.9.8 TokenContextMiddleware

TokenContextMiddleware chỉ parse token nhẹ, ko query DB, ko chặn request (enforce là việc của security dependencies):

```python
# core/middlewares/token_context.py
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

from security.providers import get_jwt_service


class TokenContextMiddleware(BaseHTTPMiddleware):
    """
    Parse token nhẹ:
    - Nếu có token: verify + decode claims -> request.state.token_claims
    - Nếu token lỗi: request.state.token_error = "expired" | "invalid"
    - Không raise 401/403 tại middleware
    - Không query DB
    """

    async def dispatch(self, request: Request, call_next):
        request.state.token_claims = None
        request.state.token_error = None

        token = _extract_token(request)
        if token:
            jwt_service = get_jwt_service()
            claims, err = jwt_service.decode_access_token(token)
            request.state.token_claims = claims
            request.state.token_error = err  # None | "expired" | "invalid"

        return await call_next(request)


def _extract_token(request: Request) -> str | None:
    # Authorization: Bearer <token>
    auth = request.headers.get("Authorization")
    if auth:
        parts = auth.split(" ", 1)
        if len(parts) == 2 and parts[0].lower() == "bearer":
            token = parts[1].strip()
            return token or None

    # Cookie fallback
    token = request.cookies.get("access_token")
    return token
```

---

#### 2.9.9 CurrentUser model (Principal)

`CurrentUser` không phải là bản sao `User`, nó là principal (danh tính) tối thiểu đủ để:
* authorize
* audit
* token invalidation check
* chỉ sống trong 1 request

```python
# security/principals.py
from typing import Any
from pydantic import BaseModel, Field, ConfigDict


class CurrentUser(BaseModel):
    model_config = ConfigDict(frozen=True) # CurrentUser nên là immutable

    user_id: int
    roles: list[str] = Field(default_factory=list)
    permissions: set[str] = Field(default_factory=set)

    token_version: int = 1
    tenant_id: str | None = None

    # factory method (tạo ra một CurrentUser):
    # - nhận: raw claims data
    # - nhiệm vụ: map field, set default, normalize
    # - trả: domain object (CurrentUser)
    @classmethod # Tại thời điểm gọi chưa
    def from_claims(cls, claims: dict[str, Any]) -> CurrentUser:
        # cls là param đặc biệt khi dùng chung với @classmethod
        # cls là tham chiếu tới class đang gọi method (ở đây là CurrentUser)

        sub = claims.get("sub")
        roles = claims.get("roles") or []
        perms = claims.get("permissions") or []
        tv = claims.get("tv") or claims.get("token_version") or 1

        # cls(...): gọi __init__ để khởi tạo đối tượng CurrentUser
        return cls(
            user_id=int(sub), # sub thường là string -> cần convert int
            roles=list(roles),
            permissions=set(perms),
            token_version=int(tv),
            tenant_id=claims.get("tid"),
        )
```

Public schema `UserOut` phải khác `User` ORM:

```python
# schemas/response/user_out_schema.py
from pydantic import BaseModel, EmailStr


class UserOut(BaseModel):
    id: int
    email: EmailStr
    is_active: bool
```

---

#### 2.9.10 Auth exceptions

```python
# core/exceptions/auth_exceptions.py
from http import HTTPStatus
from typing import Literal

from core.exceptions.base import BusinessException

TokenType = Literal["access", "refresh", "unknown"]


def _error_code(base: str, token_type: TokenType) -> str:
    """
    base: 'TOKEN_MISSING' | 'TOKEN_INVALID' | 'TOKEN_EXPIRED'
    => 'AUTH_ACCESS_TOKEN_MISSING' ...
    """
    if token_type == "access":
        prefix = "AUTH_ACCESS"
    elif token_type == "refresh":
        prefix = "AUTH_REFRESH"
    else:
        prefix = "AUTH"
    return f"{prefix}_{base}"


class AuthTokenMissingException(BusinessException):
    def __init__(self, token_type: TokenType = "unknown"):
        super().__init__(
            message="Authentication token is missing",
            error_code=_error_code("TOKEN_MISSING", token_type),
            status_code=HTTPStatus.UNAUTHORIZED,
            extra={"token_type": token_type},
        )


class InvalidTokenException(BusinessException):
    def __init__(self, token_type: TokenType = "unknown", *, reason: str | None = None):
        extra = {"token_type": token_type}
        if reason:
            extra["reason"] = reason

        super().__init__(
            message="Authentication token is invalid",
            error_code=_error_code("TOKEN_INVALID", token_type),
            status_code=HTTPStatus.UNAUTHORIZED,
            extra=extra,
        )


class TokenExpiredException(BusinessException):
    def __init__(self, token_type: TokenType = "unknown"):
        super().__init__(
            message="Authentication token has expired",
            error_code=_error_code("TOKEN_EXPIRED", token_type),
            status_code=HTTPStatus.UNAUTHORIZED,
            extra={"token_type": token_type},
        )


class UserNotFoundOrDisabledException(BusinessException):
    def __init__(self, user_id: int | str | None):
        super().__init__(
            message="User is not found or disabled",
            error_code="AUTH_USER_INVALID",
            status_code=HTTPStatus.UNAUTHORIZED,
            extra={"user_id": user_id},
        )


class ForbiddenException(BusinessException):
    def __init__(self, required: list[str] | None = None):
        super().__init__(
            message="You do not have permission to perform this action",
            error_code="AUTH_PERMISSION_DENIED",
            status_code=HTTPStatus.FORBIDDEN,
            extra={"required_permissions": required or []},
        )
```

---

#### 2.9.11 Security Dependencies

Base dependency:
* Chứa `require_current_user`: nơi xử lý token missing/expired/invalid, ko verify DB và tạo `CurrentUser` nhẹ
  * Được tiêm vào `require_current_user_verified` để sử dụng
  * Ngoài ra cũng có thể dùng cho các endpoint chỉ cần biết “đã đăng nhập” (không cần verify roles/perms từ DB), ví dụ như `/me` 

```python
# security/dependencies.py
from typing import Any
from fastapi import Request

from core.exceptions.auth_exceptions import TokenExpiredException, AuthTokenMissingException, InvalidTokenException
from security.principals import CurrentUser


def get_token_claims(request: Request) -> dict[str, Any] | None:
    """
    Lấy claims từ TokenContextMiddleware
    Middleware đã decode sẵn vào request.state.token_claims
    """
    return getattr(request.state, "token_claims", None)


def get_token_error(request: Request) -> str | None:
    """
    token_error: None | "expired" | "invalid" (được set từ middleware). :contentReference[oaicite:8]{index=8}
    """
    return getattr(request.state, "token_error", None)


def require_current_user(
        request: Request,
) -> CurrentUser:
    """
    Dependency bắt buộc khi đăng nhập
    - Không có token -> 401 (missing)
    - Token expired/invalid -> 401
    - Có claims -> build CurrentUser

    Dùng cho endpoint ít nhạy cảm / nội bộ / access token TTL ngắn
    """
    err = get_token_error(request)
    if err == "expired":
        raise TokenExpiredException(token_type="access")
    if err == "invalid":
        raise InvalidTokenException(token_type="access")

    claims = get_token_claims(request)
    if not claims:
        raise AuthTokenMissingException(token_type="access")

    return CurrentUser.from_claims(claims)
```

Guard dependencies xử lý:
* verified principal
* role guard
* permission guard

```python
# security/guards.py
import logging
from typing import Callable

from fastapi import Depends, Request
from sqlalchemy.orm import Session

from core.exceptions.auth_exceptions import InvalidTokenException, UserNotFoundOrDisabledException, ForbiddenException
from security.dependencies import require_current_user
from security.principals import CurrentUser
from repositories.auth_repository import AuthRepository
from dependencies.db import get_db

logger = logging.getLogger(__name__)


def get_auth_repository() -> AuthRepository:
    return AuthRepository()


def require_current_user_verified(
        request: Request,
        db: Session = Depends(get_db),
        user: CurrentUser = Depends(require_current_user),
        auth_repo: AuthRepository = Depends(get_auth_repository),
) -> CurrentUser:
    """
    Verified principal (enterprise):
    - Input: CurrentUser lấy từ claims (require_current_user)
    - DB snapshot: (roles, permissions, token_version)
    - Verify token_version: claim_tv phải == db_tv
    - Return CurrentUser "fresh" (roles/permissions lấy theo DB)
    """
    # Parse user_id từ principal (sub)
    try:
        user_id = int(user.user_id)
    except (TypeError, ValueError):
        logger.warning(
            "auth.invalid_subject",
            extra={
                "sub": getattr(user, "user_id", None),
                "path": request.url.path,
                "method": request.method,
            },
        )
        # Access token đã decode được nhưng claim sub sai format -> invalid access token
        raise InvalidTokenException("access", reason="invalid_subject")

    # DB snapshot (roles/perms/token_version)
    roles, permissions, db_token_version = auth_repo.get_authz_snapshot(db, user_id)

    # user not found/disabled (repo return token_version=0 để báo invalid)
    if not db_token_version:
        logger.warning(
            "auth.user_not_found_or_disabled",
            extra={
                "user_id": user_id,
                "path": request.url.path,
                "method": request.method,
            },
        )
        raise UserNotFoundOrDisabledException(user_id)

    # token_version check (revoke-all)
    claim_tv = int(getattr(user, "token_version", 1))
    if claim_tv != int(db_token_version):
        # token bị revoke: coi như token invalid
        logger.info(  # đây không phải system error, thường log INFO là đủ (token bị revoke là event hợp lệ)
            "auth.token_revoked",
            extra={
                "user_id": user_id,
                "claim_tv": claim_tv,
                "db_tv": int(db_token_version),
                "path": request.url.path,
                "method": request.method,
            },
        )
        raise InvalidTokenException("access", reason="token_revoked")

    # Return principal fresh theo DB (roles/perms có thể đã thay đổi)
    return CurrentUser(
        user_id=user_id,
        roles=list(roles),
        permissions=set(permissions),
        token_version=int(db_token_version),
        tenant_id=getattr(user, "tenant_id", None),
    )


def require_permissions(*required: str) -> Callable[[CurrentUser], CurrentUser]:
    """
    Factory dependency: require_permissions("student:read", "student:write")
    - Nếu thiếu bất kỳ permission nào -> 403
    """
    required_set = set(required)

    def _dep(user: CurrentUser = Depends(require_current_user_verified)) -> CurrentUser:
        # Các permission được yêu cầu nhưng user không có
        # dùng toán tử '-' với set
        missing = sorted(required_set - user.permissions)

        if missing:
            raise ForbiddenException(required=missing)
        return user

    return _dep


def require_roles(*required: str) -> Callable[[CurrentUser], CurrentUser]:
    """
    Factory dependency: require_roles("admin", "manager")
    - Nếu user không có bất kỳ role nào trong required -> 403
    """
    required_set = set(required)

    def _dep(user: CurrentUser = Depends(require_current_user_verified)) -> CurrentUser:
        user_roles = set(user.roles)

        # user phải có ÍT NHẤT 1 role trong required
        if user_roles.isdisjoint(required_set):
            raise ForbiddenException(required=[f"role:{r}" for r in sorted(required_set)])

        return user

    return _dep
```

Lưu ý: 
* Khi sử dụng `require_current_user_verified` để verify quyền trực tiếp từ DB sẽ làm tăng số lần query DB => gây nghẽn cổ chai khi lượng người dùng lớn
* Dùng cache (Redis / in-memory) cho authz snapshot để giảm tải DB khi lượng người dùng lớn

---

#### 2.9.11 AuthService

Là nơi xử lý toàn bộ luồng:
* Login (verify password => phát hành access token + refresh token session + set cookie)
* Refresh (validate/rotate refresh session => phát hành access token mới + set cookie mới)
* Logout (revoke refresh session + clear cookie)
* (tuỳ chọn) Logout all (revoke all sessions + bump (chủ động tăng) token_version)

```python
# services/auth_service.py
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone

from fastapi import Request, Response
from sqlalchemy.orm import Session

from configs.settings.security import SecuritySettings
from core.exceptions.auth_exceptions import (
    AuthTokenMissingException,
    InvalidTokenException,
    UserNotFoundOrDisabledException,
)
from repositories.auth_repository import AuthRepository
from repositories.refresh_session_repository import RefreshSessionRepository
from security.cookie_policy import RefreshCookiePolicy
from security.jwt_service import JwtService
from security.password import verify_password
from security.refresh_token import generate_refresh_token, hash_refresh_token


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


@dataclass(frozen=True)
class TokenPairOut:
    """
    Service DTO (Service -> Router)
    - access_token trả trong body
    - refresh_token set trong cookie (HttpOnly) => KHÔNG đưa vào body
    """
    access_token: str
    token_type: str = "Bearer"
    expires_in: int | None = None  # seconds


class AuthService:
    """
    Execute:
    - login: verify credentials -> issue access + refresh cookie + store refresh session
    - refresh: validate+rotate refresh session -> issue new access + new refresh cookie
    - logout: revoke refresh session -> clear refresh cookie
    - logout_all: revoke all sessions for user -> clear refresh cookie
    """

    def __init__(
            self,
            *,
            auth_repo: AuthRepository,
            refresh_repo: RefreshSessionRepository,
            cookie_policy: RefreshCookiePolicy,
            security_settings: SecuritySettings,
            jwt_service: JwtService,
    ):
        self.auth_repo = auth_repo
        self.refresh_repo = refresh_repo
        self.cookie_policy = cookie_policy
        self.security_settings = security_settings
        self.jwt_service = jwt_service

        if self.security_settings.jwt is None:
            raise RuntimeError("SecuritySettings.jwt is not configured")

        self._access_ttl_minutes = int(self.security_settings.jwt.access_token_ttl_minutes)
        self._refresh_ttl_minutes = int(self.security_settings.refresh_session.ttl_minutes)
        self._refresh_absolute_ttl_minutes = int(self.security_settings.refresh_session.absolute_ttl_minutes)

    def login(
            self,
            db: Session,
            *,
            request: Request,
            response: Response,
            email: str,
            password: str,
    ) -> TokenPairOut:
        """
        Execute:
        - Load user credentials by email
        - Verify password
        - Load authz snapshot (roles, permissions, token_version)
        - Issue access token (JWT)
        - Issue refresh token (opaque) + store hashed session + set cookie
        """
        user = self.auth_repo.get_user_credentials_by_email(db, email)

        if not user:
            raise InvalidTokenException(token_type="access", reason="invalid_credentials")

        if hasattr(user, "is_active") and not getattr(user, "is_active"):
            raise UserNotFoundOrDisabledException(getattr(user, "id", None))

        if not verify_password(password, getattr(user, "hashed_password", "")):
            raise InvalidTokenException(token_type="access", reason="invalid_credentials")

        user_id = int(getattr(user, "id"))

        _, _, token_version = self.auth_repo.get_authz_snapshot(db, user_id)
        if not token_version:
            raise UserNotFoundOrDisabledException(user_id)

        # Phát hành access token
        access_token = self.jwt_service.create_access_token(
            subject=str(user_id),
            token_version=int(token_version),
        )

        # Phát hành refresh token (opaque) + lưu hash ở DB
        refresh_plain = generate_refresh_token()
        refresh_hash = hash_refresh_token(refresh_plain)

        now = _utcnow()
        refresh_expires_at = now + timedelta(minutes=self._refresh_ttl_minutes)
        refresh_absolute_expires_at = now + timedelta(minutes=self._refresh_absolute_ttl_minutes)

        self.refresh_repo.create_session(
            db,
            user_id=user_id,
            token_hash=refresh_hash,
            expires_at=refresh_expires_at,
            absolute_expires_at=refresh_absolute_expires_at,
            user_agent=request.headers.get("User-Agent"),
            ip_address=request.client.host if request.client else None,
        )

        # Set refresh cookie
        self.cookie_policy.set(response, refresh_plain)

        return TokenPairOut(
            access_token=access_token,
            token_type="Bearer",
            expires_in=self._access_ttl_minutes * 60,
        )

    def refresh(
            self,
            db: Session,
            *,
            request: Request,
            response: Response,
    ) -> TokenPairOut:
        """
        Execute:
        - Read refresh token from cookie
        - Hash -> rotate refresh session
        - Load authz snapshot (roles, permissions, token_version)
        - Issue new access token
        - Set new refresh cookie (rotated)
        """
        refresh_plain = request.cookies.get(self.cookie_policy.name)
        if not refresh_plain:
            raise AuthTokenMissingException(token_type="refresh")

        old_hash = hash_refresh_token(refresh_plain)

        # Rotate refresh session
        new_plain = generate_refresh_token()
        new_hash = hash_refresh_token(new_plain)

        now = _utcnow()
        new_expires_at = now + timedelta(minutes=self._refresh_ttl_minutes)

        session = self.refresh_repo.rotate_session(
            db,
            old_token_hash=old_hash,
            new_token_hash=new_hash,
            new_expires_at=new_expires_at,
            now=now,
        )
        if not session:
            # revoked/expired/unknown
            raise InvalidTokenException(token_type="refresh", reason="session_not_active")

        user_id = int(getattr(session, "user_id"))

        # Load latest authz snapshot (roles/permissions can change)
        _, _, token_version = self.auth_repo.get_authz_snapshot(db, user_id)
        if not token_version:
            raise UserNotFoundOrDisabledException(user_id)

        # Phát hành new access token (latest token_version)
        access_token = self.jwt_service.create_access_token(
            subject=str(user_id),
            token_version=int(token_version),
        )

        # Set rotated refresh cookie
        self.cookie_policy.set(response, new_plain)

        return TokenPairOut(
            access_token=access_token,
            token_type="Bearer",
            expires_in=self._access_ttl_minutes * 60,
        )

    def logout(
            self,
            db: Session,
            *,
            request: Request,
            response: Response,
    ) -> None:
        """
        Logout current device/session:
        - If refresh cookie exists -> revoke that refresh session
        - Clear cookie always
        """
        refresh_plain = request.cookies.get(self.cookie_policy.name)
        if refresh_plain:
            token_hash = hash_refresh_token(refresh_plain)
            # revoke_by_token_hash theo ORM style (bool)
            self.refresh_repo.revoke_by_token_hash(db, token_hash=token_hash)

        self.cookie_policy.clear(response)

    def logout_all(
            self,
            db: Session,
            *,
            user_id: int,
            response: Response,
    ) -> int:
        """
        Logout all devices:
        - Revoke all refresh sessions for user
        - Clear cookie
        - Return number of revoked sessions
        """
        count = self.refresh_repo.revoke_all_for_user(db, user_id=user_id)
        self.cookie_policy.clear(response)
        return int(count)
```

---

#### 2.9.12 Auth Controller

Tạo helper chung cho success response và failed response để:
* Nhất quán API Contract: mọi endpoint trả cùng format
* Ngăn lặp code: ko phải set `trace_id` thủ công ở từng router
* Bảo đảm `trace_id` luôn đúng theo “source of truth” là `trace_id_ctx` (đã được `TraceIdMiddleware` set)
* Dễ mở rộng thêm: message mặc định, mapping `error_code`, `extra`, ...

```python
# core/responses.py
from typing import TypeVar
from core.trace import trace_id_ctx
from schemas.response.base import SuccessResponse

T = TypeVar("T")


def success_response(
    data: T | None = None,
    *,
    message: str | None = None,
) -> SuccessResponse[T]:
    """
    Helper chuẩn hoá response body cho happy-path:
    - Luôn inject trace_id từ trace_id_ctx (source of truth)
    - Không phụ thuộc Request
    - Dùng cho mọi happy-path HTTP response
    """
    return SuccessResponse(
        success=True,
        data=data,
        message=message,
        trace_id=trace_id_ctx.get() or None,
    )
```

Tạo template responses chuẩn tài liệu OpenAPI để dùng chung (tránh lặp code):

```python
# core/openapi_responses.py
from schemas.response.base import ErrorResponse


BAD_REQUEST_400 = {
    "model": ErrorResponse,
    "description": "Invalid parameters (business rule violation)",
}
UNAUTHORIZED_401 = {
    "model": ErrorResponse,
    "description": "Unauthorized (missing/invalid/expired token, or invalid credentials)",
}
FORBIDDEN_403 = {
    "model": ErrorResponse,
    "description": "Forbidden (permission denied)",
}
NOT_FOUND_404 = {
    "model": ErrorResponse,
    "description": "Resource not found",
}
CONFLICT_409 = {
    "model": ErrorResponse,
    "description": "Resource conflict (already exists or unique constraint violation)",
}
INTERNAL_500 = {
    "model": ErrorResponse,
    "description": "Internal server error",
}

AUTH_COMMON_RESPONSES = {
    401: UNAUTHORIZED_401,
    500: INTERNAL_500,
}

AUTHZ_COMMON_RESPONSES = {
    401: UNAUTHORIZED_401,
    403: FORBIDDEN_403,
    500: INTERNAL_500,
}
```

Các router cần thiết cho luồng xác thực người dùng:

```python
# controllers/auth_controller.py
from fastapi import APIRouter, Depends, Request, Response, status
from sqlalchemy.orm import Session

from core.openapi_responses import UNAUTHORIZED_401, INTERNAL_500, AUTH_COMMON_RESPONSES
from core.responses import success_response
from dependencies.db import get_db
from schemas.auth.login_out_schema import LoginResponse
from schemas.auth.login_schema import LoginRequest
from schemas.auth.logout_out_schema import LogoutAllResult
from schemas.response.base import SuccessResponse
from services.auth_service import AuthService, TokenPairOut
from security.providers import get_auth_service
from security.principals import CurrentUser
from security.guards import require_current_user_verified

auth_router = APIRouter()


def _to_response(out: TokenPairOut) -> SuccessResponse[LoginResponse]:
    if out.expires_in is None:
        raise RuntimeError("TokenPairOut.expires_in must not be None")
    return success_response(
        LoginResponse(
            access_token=out.access_token,
            token_type=out.token_type,
            expires_in=out.expires_in,
        )
    )


@auth_router.post(
    "/login",
    response_model=SuccessResponse[LoginResponse],
    responses=AUTH_COMMON_RESPONSES,
)
def login(
        payload: LoginRequest,
        request: Request,
        response: Response,
        svc: AuthService = Depends(get_auth_service),
        db: Session = Depends(get_db)
) -> SuccessResponse[LoginResponse]:
    """
    Login:
    - verify credentials
    - issue access token in body
    - set refresh token cookie (HttpOnly)
    """
    out = svc.login(
        db=db,
        request=request,
        response=response,
        email=str(payload.email),
        password=payload.password,
    )
    return _to_response(out)


@auth_router.post(
    "/refresh",
    response_model=SuccessResponse[LoginResponse],
    responses=AUTH_COMMON_RESPONSES,
)
def refresh(
        request: Request,
        response: Response,
        svc: AuthService = Depends(get_auth_service),
        db: Session = Depends(get_db),
) -> SuccessResponse[LoginResponse]:
    """
    Refresh:
    - read refresh cookie
    - rotate refresh session
    - issue new access token
    - set new refresh cookie
    """
    out = svc.refresh(
        db=db,
        request=request,
        response=response,
    )
    return _to_response(out)


@auth_router.post(
    "/logout",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={500: INTERNAL_500},
)
def logout(
        request: Request,
        response: Response,
        svc: AuthService = Depends(get_auth_service),
        db: Session = Depends(get_db),
) -> Response:
    """
    Logout current device:
    - revoke refresh session (if exists)
    - clear refresh cookie always
    """
    svc.logout(
        db=db,
        request=request,
        response=response,
    )
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@auth_router.post(
    "/logout-all",
    response_model=SuccessResponse[LogoutAllResult],
    responses=AUTH_COMMON_RESPONSES,
)
def logout_all(
        response: Response,
        user: CurrentUser = Depends(require_current_user_verified),
        svc: AuthService = Depends(get_auth_service),
        db: Session = Depends(get_db),
) -> SuccessResponse[LogoutAllResult]:
    """
    Logout all devices:
    - require verified current user (token_version valid)
    - revoke all refresh sessions for this user
    - clear refresh cookie
    """
    user_id = int(user.user_id)
    revoked = svc.logout_all(
        db=db,
        user_id=user_id,
        response=response,
    )
    return success_response(LogoutAllResult(revoked_sessions=revoked))
```

---

#### 2.9.13 Refactor Student Controller

Tạo Empty schema dùng cho các route trả empty payload

```python
# schemas/common.py
from pydantic import BaseModel

class EmptyData(BaseModel):
    pass
```

Refactor Student Controller để apply Auth/Authz với các quy tắc chuẩn sau:
* Role: quyết định ai được phép làm loại hành động này
* Permission: quyết định hành động cụ thể
* Endpoint nhạy cảm => dùng Role + Permission (double-gate authorization)
* Endpoint thường => chỉ cần Permission


```python
from fastapi import APIRouter, Depends, Request, Response, status
from sqlalchemy.orm import Session

from core.openapi_responses import UNAUTHORIZED_401, INTERNAL_500, AUTH_COMMON_RESPONSES, NOT_FOUND_404, \
    BAD_REQUEST_400, AUTHZ_COMMON_RESPONSES, CONFLICT_409, FORBIDDEN_403
from core.responses import success_response
from dependencies.db import get_db
from schemas.common import EmptyData
from schemas.request.student_schema import StudentCreate, StudentUpdate
from schemas.response.base import SuccessResponse
from schemas.response.student_out_schema import StudentOut
from security.dependencies import require_current_user
from security.guards import require_roles, require_permissions
from security.principals import CurrentUser
from services.student_service import StudentService

student_router = APIRouter()
service = StudentService()


@student_router.get(
    "",
    response_model=SuccessResponse[list[StudentOut]],
    responses=AUTH_COMMON_RESPONSES,
)
def list_students(
        offset: int = 0,
        limit: int = 100,
        db: Session = Depends(get_db),
        _: CurrentUser = Depends(require_current_user),
) -> SuccessResponse[list[StudentOut]]:
    students = service.list_students(db, offset=offset, limit=limit)
    data = [StudentOut.model_validate(student) for student in students]
    return success_response(data=data)


@student_router.get(
    "/{student_id:int}",
    response_model=SuccessResponse[StudentOut],
    responses={
        401: UNAUTHORIZED_401,
        404: NOT_FOUND_404,
        500: INTERNAL_500,
    },
)
def get_student(
        student_id: int,
        db: Session = Depends(get_db),
        _: CurrentUser = Depends(require_current_user),
) -> SuccessResponse[StudentOut]:
    student = service.get_student(db, student_id)
    return success_response(StudentOut.model_validate(student))


@student_router.get(
    "/search",
    response_model=SuccessResponse[list[StudentOut]],
    responses={
        400: BAD_REQUEST_400,
        401: UNAUTHORIZED_401,
        500: INTERNAL_500,
    }
)
def search_students(
        keyword: str | None = None,
        min_age: int | None = None,
        max_age: int | None = None,
        offset: int = 0,
        limit: int = 100,
        db: Session = Depends(get_db),
        _: CurrentUser = Depends(require_current_user),
) -> SuccessResponse[list[StudentOut]]:
    students = service.search_students(
        db,
        keyword=keyword,
        min_age=min_age,
        max_age=max_age,
        offset=offset,
        limit=limit,
    )
    data = [StudentOut.model_validate(s) for s in students]
    return success_response(data)


@student_router.post(
    "",
    response_model=SuccessResponse[StudentOut],
    status_code=status.HTTP_201_CREATED,
    responses={
        400: BAD_REQUEST_400,
        401: UNAUTHORIZED_401,
        403: FORBIDDEN_403,
        409: CONFLICT_409,
        500: INTERNAL_500,
    },
)
def create_student(
        data: StudentCreate,
        request: Request,
        response: Response,
        db: Session = Depends(get_db),
        _: CurrentUser = Depends(require_permissions("student:write")),
) -> SuccessResponse[StudentOut]:
    student = service.create_student(db, data)

    # Set Location header
    location = request.url_for("get_student", student_id=student.id)
    response.headers["location"] = str(location)

    return success_response(
        StudentOut.model_validate(student),
        message="Student created",
    )


@student_router.patch(
    "/{student_id}",
    response_model=SuccessResponse[StudentOut],
    responses={
        400: BAD_REQUEST_400,
        401: UNAUTHORIZED_401,
        403: FORBIDDEN_403,
        404: NOT_FOUND_404,
        500: INTERNAL_500,
    }
)
def update_student(
        student_id: int,
        data: StudentUpdate,
        db: Session = Depends(get_db),
        _: CurrentUser = Depends(require_permissions("student:write")),
) -> SuccessResponse[StudentOut]:
    student = service.update_student(db, student_id, data)
    return success_response(
        StudentOut.model_validate(student),
        message="Student updated",
    )


# Double-gate authorization
@student_router.delete(
    "/{student_id}",
    response_model=SuccessResponse[EmptyData],
    responses=AUTHZ_COMMON_RESPONSES,
)
def delete_student(
        student_id: int,
        db: Session = Depends(get_db),
        _: CurrentUser = Depends(require_roles("ADMIN", "HR_MANAGER")),
        __: CurrentUser = Depends(require_permissions("student:delete")),
) -> SuccessResponse[EmptyData]:
    service.delete_student(db, student_id)
    return success_response(EmptyData(), message="Student deleted")
```

---

#### 2.9.14 Cấu hình Swagger/OpenAPI security scheme

Tạo “bearer scheme” dùng cho docs:

```python
# security/schemes.py
from fastapi.security import HTTPBearer

# auto_error=False để không can thiệp flow hiện tại (guards vẫn là nơi quyết định 401/403)
bearer_scheme = HTTPBearer(auto_error=False)
```

Gắn scheme vào OpenAPI cho các route cần login:
* Gắn cho toàn `student_router`

```python
from fastapi import APIRouter, Security
from fastapi.security import HTTPAuthorizationCredentials
from security.schemes import bearer_scheme

student_router = APIRouter(
    dependencies=[Security(bearer_scheme)]
)
```

* Gắn theo từng endpoint (khi muốn để một số endpoint public)

```python
@student_router.get(
    "",
    dependencies=[Security(bearer_scheme)],
    ...
)
def list_students(...):
    ...
```

Bật `"persistAuthorization"` để Swagger nhớ token:

```python
# main.py
app = FastAPI(
    swagger_ui_parameters={"persistAuthorization": True}
)
```

---

#### 2.9.15 Seeding User Data

1. Trước khi seed dữ liệu thì cần chạy Alembic để tạo hoặc cập nhật migration:
* Nếu DB đã có sẵn bảng `students` và `tasks` từ bài trước => cần khai báo để Alembic quản lý
    ```bash
        alembic stamp base
    ```
* Chạy Alembic để tự động gen file migration cho các model mới tạo
    ```bash
        alembic revision --autogenerate -m "init auth and student models"
    ```
* Chạy `alembic upgrade head` để cập nhật schema mới nhất nhất cho DB

2. Cần import các model trong `models/__init__.py` để:
* dùng Alembic autogenerate
* dùng script seed

```python
from models.base import Base

# Association tables (Table)
from models.associations import user_roles, role_permissions

# Core models
from models.user import User
from models.role import Role
from models.permission import Permission
from models.refresh_session import RefreshSession

# Domain models
from models.student import Student
from models.task import Task

# Mixins (optional, không bắt buộc)
from models.time_mixin import TimeMixin

__all__ = [
    "Base",
    "User",
    "Role",
    "Permission",
    "RefreshSession",
    "Student",
    "Task",
]
```

3. Tạo script để seed dữ liệu mẫu cho user gồm:
* Permissions
* Roles
* Role–Permission mapping
* Users
* User–Role mapping

```python
# scripts/seed_user_data.py
from dataclasses import dataclass
from typing import Iterable

from sqlalchemy import select
from sqlalchemy.orm import Session

from configs.database import SessionLocal
from security.password import hash_password

from models import Permission, Role, User


@dataclass(frozen=True)
class SeedRole:
    name: str
    permission_codes: tuple[str, ...]


@dataclass(frozen=True)
class SeedUser:
    email: str
    password: str
    role_names: tuple[str, ...]
    is_active: bool = True
    token_version: int = 1


PERM_STUDENT_READ = "student:read"
PERM_STUDENT_WRITE = "student:write"
PERM_STUDENT_DELETE = "student:delete"

PERM_TASK_READ = "task:read"
PERM_TASK_WRITE = "task:write"
PERM_TASK_DELETE = "task:delete"

DEFAULT_PERMISSIONS: tuple[str, ...] = (
    # Students
    PERM_STUDENT_READ,
    PERM_STUDENT_WRITE,
    PERM_STUDENT_DELETE,
    # Tasks
    PERM_TASK_READ,
    PERM_TASK_WRITE,
    PERM_TASK_DELETE,
)

DEFAULT_ROLES: tuple[SeedRole, ...] = (
    SeedRole(
        name="ADMIN",
        permission_codes=DEFAULT_PERMISSIONS,
    ),
    SeedRole(
        name="TEACHER",
        permission_codes=(
            PERM_STUDENT_READ,
            PERM_STUDENT_WRITE,
            PERM_TASK_READ,
            PERM_TASK_WRITE,
        ),
    ),
    SeedRole(
        name="STUDENT",
        permission_codes=(
            PERM_STUDENT_READ,
            PERM_TASK_READ,
        ),
    ),
)

DEFAULT_USERS: tuple[SeedUser, ...] = (
    SeedUser(
        email="admin@example.com",
        password="Admin@123456",
        role_names=("ADMIN",),
    ),
    SeedUser(
        email="teacher@example.com",
        password="Teacher@123456",
        role_names=("TEACHER",),
    ),
    SeedUser(
        email="student@example.com",
        password="Student@123456",
        role_names=("STUDENT",),
    ),
)


# Upsert helpers (idempotent)
def upsert_permissions(db: Session, codes: Iterable[str]) -> dict[str, Permission]:
    existing = db.execute(select(Permission).where(Permission.code.in_(list(codes)))).scalars().all()
    by_code = {p.code: p for p in existing}

    for code in codes:
        if code in by_code:
            continue
        p = Permission(code=code)
        db.add(p)
        by_code[code] = p

    db.flush()
    return by_code


def upsert_roles(
        db: Session,
        roles: Iterable[SeedRole],
        permissions_by_code: dict[str, Permission],
) -> dict[str, Role]:
    role_names = [r.name for r in roles]
    existing = db.execute(select(Role).where(Role.name.in_(role_names))).scalars().all()
    by_name = {r.name: r for r in existing}

    for seed in roles:
        role = by_name.get(seed.name)
        if role is None:
            role = Role(name=seed.name)
            db.add(role)
            by_name[seed.name] = role

        # Gán permissions theo code (many-to-many)
        desired_perms = [permissions_by_code[c] for c in seed.permission_codes if c in permissions_by_code]
        # Tránh duplicate trong list relationship
        role.permissions = list({p.code: p for p in desired_perms}.values())

    db.flush()
    return by_name


def upsert_users(
        db: Session,
        users: Iterable[SeedUser],
        roles_by_name: dict[str, Role],
) -> dict[str, User]:
    emails = [u.email for u in users]
    existing = db.execute(select(User).where(User.email.in_(emails))).scalars().all()
    by_email = {u.email: u for u in existing}

    for seed in users:
        user = by_email.get(seed.email)
        if user is None:
            user = User(
                email=seed.email,
                hashed_password=hash_password(seed.password),
                is_active=seed.is_active,
                token_version=seed.token_version,
            )
            db.add(user)
            by_email[seed.email] = user
        else:
            # Đồng bộ trạng thái cơ bản
            user.is_active = seed.is_active
            user.token_version = seed.token_version

        # Gán roles theo name (many-to-many)
        desired_roles = [roles_by_name[n] for n in seed.role_names if n in roles_by_name]
        user.roles = list({r.name: r for r in desired_roles}.values())

    db.flush()
    return by_email


# Main runner
def seed() -> None:
    db = SessionLocal()
    try:
        permissions_by_code = upsert_permissions(db, DEFAULT_PERMISSIONS)
        upsert_roles(db, DEFAULT_ROLES, permissions_by_code)
        roles_by_name = db.execute(select(Role)).scalars().all()
        roles_by_name_map = {r.name: r for r in roles_by_name}

        upsert_users(db, DEFAULT_USERS, roles_by_name_map)

        db.commit()

        print("Seed users/roles/permissions: OK")
        print("Created/ensured users:")
        for u in DEFAULT_USERS:
            print(f" - {u.email} / {u.password} (roles={u.role_names})")
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed()
```

---

### 2.10 Tổng hợp toàn bộ luồng Auth/Authz

#### 2.10.1 Kiến trúc tổng thể (Hybrid Middleware + Depends)

> Middleware làm việc “cross-cutting” cho mọi request:
> * tạo `trace_id`
> * parse token nhẹ (decode claims, không query DB)
> * gắn vào `request.state` để các tầng sau dùng lại
> 
> Depends/Guards quyết định “chặn hay không chặn” theo từng route:
> * `require_current_user()` => chặn 401 nếu missing/invalid/expired
> * `require_current_user_verified()` => verify theo DB snapshot (roles/perms/token_version)
> * `require_permissions(...)`, `require_roles(...)` => chặn 403 khi thiếu quyền
> 
> Service chỉ xử lý nghiệp vụ, lỗi auth/authz cũng là `BusinessException` để đi qua handler chung

#### 2.10.2 Luồng xử lý chuẩn cho mọi request

```
Client
  |
  |  HTTP Request
  v
[CORS Middleware]  (preflight OPTIONS có thể dừng ở đây)
  |
  v
[DBSessionMiddleware]   -> gắn db session vào request context
  |
  v
[TraceIdMiddleware]     -> request.state.trace_id (+ X-Trace-Id)
  |
  v
[TokenContextMiddleware]  (NHẸ)
  - đọc Authorization Bearer (hoặc cookie access_token fallback)
  - verify chữ ký + decode claims
  - request.state.token_claims = claims | None
  - request.state.token_error = None | "expired" | "invalid"
  |
  v
[Router/FastAPI]
  |
  +--> Depends: require_current_user()
  |      - token_error == expired -> raise TokenExpiredException (401)
  |      - token_error == invalid -> raise InvalidTokenException (401)
  |      - claims missing -> raise AuthTokenMissingException (401)
  |      - else -> CurrentUser.from_claims()
  |
  +--> Depends: require_current_user_verified() (OPTIONAL theo route)
  |      - parse user_id
  |      - auth_repo.get_authz_snapshot(db, user_id)
  |      - check user active / token_version
  |      - return principal “fresh” (roles/perms từ DB)
  |
  +--> Depends: require_permissions / require_roles (OPTIONAL theo route)
  |      - thiếu quyền -> raise ForbiddenException (403)
  |
  v
[Service Layer]
  - xử lý nghiệp vụ
  - raise BusinessException nếu vi phạm rule
  |
  v
[Exception Handlers]
  - BusinessException -> ErrorResponse chuẩn (4xx) + trace_id
  - Unhandled Exception -> 500 + ErrorResponse chung chung
  |
  v
Client nhận JSON response chuẩn (+ trace_id)
```

Mấu chốt quan trọng đối với kiến trúc Hybrid Middleware + Depends:
* Middleware không quyết định 401/403 (trừ vài trường hợp đặc biệt nếu muốn chặn global)
* 401/403 nằm ở Depends/Guards, nên route nào cần gì thì khai báo đúng cái đó

#### 2.10.3 Use case Auth flows: Login / Refresh / Logout

1) Login: phát hành access token + tạo refresh session + set cookie

Endpoint: `POST /auth/login`:

```markdown
Client -> /auth/login (email, password)
  -> AuthService.login
      - verify credentials
      - issue access_token (JWT) -> trả trong body
      - generate refresh_token (opaque)
      - hash refresh_token -> lưu refresh_sessions
      - set refresh cookie (HttpOnly)
Client nhận:
  - body: access_token
  - cookie: refresh_token (HttpOnly)
```

Các kết quả lỗi hay gặp:
* sai credentials => 401 (InvalidTokenException reason invalid_credentials)
* user disabled => 401 (UserNotFoundOrDisabledException)

2. Refresh: rotate refresh token + cấp access token mới

Endpoint: `POST /auth/refresh`:

```markdown
Client -> /auth/refresh (cookie refresh_token)
  -> AuthService.refresh
      - đọc refresh cookie
      - hash -> rotate_session(old_hash -> new_hash)
      - issue new access_token
      - set cookie refresh_token mới
```

Các nhánh lỗi quan trọng:
* thiếu cookie refresh => 401 (AuthTokenMissingException refresh)
* session hết hạn / revoked / unknown => 401 (InvalidTokenException refresh, reason session_not_active)
* absolute_expires_at hết hạn => coi như session không active => 401 (đăng nhập lại)

3. Logout: revoke refresh session hiện tại + clear cookie

Endpoint: `POST /auth/logout` (204)
* Nếu có refresh cookie → revoke session đó
* Luôn clear cookie

4. Logout all: revoke toàn bộ session + clear cookie

Endpoint: `POST /auth/logout-all`
* yêu cầu user đã login + verified
* revoke tất cả refresh_sessions của user
* clear cookie
* trả số lượng session bị revoke
