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

* `UnauthorizedException` (401): thiếu/invalid token
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
    expires_at: Mapped[datetime] = mapped_column(
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

    # ---- Metadata (optional but enterprise-friendly) ----
    user_agent: Mapped[str | None] = mapped_column(String(255), nullable=True)
    ip_address: Mapped[str | None] = mapped_column(String(45), nullable=True)

    # ---- Relationship ----
    user = relationship("User", lazy="joined")

    __table_args__ = (
        UniqueConstraint("token_hash", name="uq_refresh_sessions_token_hash"),
        Index("ix_refresh_sessions_user_active", "user_id", "revoked_at"),
    )
```

---

#### 2.9.2 Password Hashing

Cài thư viện `bcrypt`:

```bash
    pip install passlib[bcrypt]
```

Tạo Password utility:

```python
# security/password.py
from passlib.context import CryptContext

_pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


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

#### 2.9.3 Schemas cho login

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
    token_type: str = "bearer"
    expires_in: int  # seconds
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
            user_agent: str | None = None,
            ip_address: str | None = None,
            now: datetime | None = None,
    ) -> RefreshSession:
        now = now or _utcnow()

        session = RefreshSession(
            user_id=user_id,
            token_hash=token_hash,
            expires_at=expires_at,
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
            )
        )

        if for_update:
            stmt = stmt.with_for_update()

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
        current.expires_at = new_expires_at
        current.rotated_at = now
        current.updated_at = now

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
        id_stmt = select(RefreshSession.id).where(RefreshSession.expires_at <= before)
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

from configs.env import settings_config

_settings = settings_config()

JWT_ALGORITHM = _settings.jwt_algorithm
JWT_SECRET_KEY = _settings.jwt_secret_key
JWT_ISSUER = _settings.jwt_issuer
JWT_AUDIENCE = _settings.jwt_audience


def create_access_token(
    *,
    subject: str,
    permissions: list[str],
    roles: list[str] | None = None,
    expires_minutes: int = 15,
    extra_claims: dict[str, Any] | None = None,
) -> str:
    now = datetime.now(timezone.utc)
    payload: dict[str, Any] = {
        "sub": subject,
        "iss": JWT_ISSUER,
        "aud": JWT_AUDIENCE,
        "iat": int(now.timestamp()),
        "exp": int((now + timedelta(minutes=expires_minutes)).timestamp()),
        "permissions": permissions,
        "roles": roles or [],
    }
    if extra_claims:
        payload.update(extra_claims)

    return jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)


def decode_access_token(token: str) -> tuple[dict[str, Any] | None, str | None]:
    try:
        claims = jwt.decode(
            token,
            JWT_SECRET_KEY,
            algorithms=[JWT_ALGORITHM],
            audience=JWT_AUDIENCE,
            issuer=JWT_ISSUER,
            options={"require_aud": True, "require_iss": True},
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
from typing import Literal

from fastapi import Response

SameSite = Literal["lax", "strict", "none"]


class RefreshCookiePolicy:
    def __init__(
            self,
            *,
            name: str = "refresh_token",
            path: str = "/api/v1/auth/refresh",
            secure: bool = True,
            samesite: SameSite = "strict",
            max_age_seconds: int = 60 * 60 * 24 * 14,
    ):
        self.name = name
        self.path = path
        self.secure = secure
        self.samesite: SameSite = samesite
        self.max_age_seconds = max_age_seconds

    def set(self, response: Response, token: str) -> None:
        response.set_cookie(
            key=self.name,
            value=token,
            httponly=True,
            secure=self.secure,
            samesite=self.samesite,
            max_age=self.max_age_seconds,
            path=self.path,
        )

    def clear(self, response: Response) -> None:
        response.delete_cookie(key=self.name, path=self.path)
```

---

#### 2.9.7 TokenContextMiddleware

TokenContextMiddleware chỉ parse token nhẹ, ko query DB, ko chặn request (enforce là việc của security dependencies):

```python
# core/middlewares/token_context.py
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

from security.jwt_service import decode_access_token


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
            claims, err = decode_access_token(token)
            request.state.token_claims = claims
            request.state.token_error = err  # None | "expired" | "invalid"

        return await call_next(request)


def _extract_token(request: Request) -> str | None:
    # Authorization: Bearer <token>
    auth = request.headers.get("Authorization")
    if auth and auth.startswith("Bearer "):
        return auth.removeprefix("Bearer ").strip()

    # Cookie fallback
    token = request.cookies.get("access_token")
    return token
```

---

#### 2.9.8 CurrentUser model (Principal)

`CurrentUser` không phải là bản sao `User`, nó là principal (danh tính) tối thiểu đủ để:
* authorize
* audit
* token invalidation check

```python
# security/principals.py
from __future__ import annotations

from typing import Any
from pydantic import BaseModel, Field, ConfigDict


class CurrentUser(BaseModel):
    model_config = ConfigDict(frozen=True)

    user_id: int
    roles: list[str] = Field(default_factory=list)
    permissions: set[str] = Field(default_factory=set)

    token_version: int = 1
    tenant_id: str | None = None

    @classmethod
    def from_claims(cls, claims: dict[str, Any]) -> "CurrentUser":
        # sub thường là string -> convert
        sub = claims.get("sub")
        roles = claims.get("roles") or []
        perms = claims.get("permissions") or []
        tv = claims.get("tv") or claims.get("token_version") or 1

        return cls(
            user_id=int(sub),
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

#### 2.9.9 Depends: get_current_user + optional_user

```python
# security/dependencies.py

```

