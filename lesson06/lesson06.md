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
from schemas.response.error_response import ErrorResponse


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

## 2) 