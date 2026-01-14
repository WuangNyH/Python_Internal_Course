# Buổi 5: FastAPI với Database (PostgreSQL)

## Phần 1) Kết nối Database

Ở buổi 4 đã:

* Tạo API
* Validate dữ liệu bằng Pydantic
* Lưu dữ liệu trong in-memory list (bài tập)

Hạn chế của in-memory:

* Mất dữ liệu khi server restart
* Không chia sẻ dữ liệu giữa nhiều instance
* Không phù hợp cho production

=> Database (PostgreSQL) giúp:

* Lưu trữ dữ liệu bền vững (persistent)
* Hỗ trợ truy vấn phức tạp
* Đảm bảo toàn vẹn dữ liệu (constraint, transaction)
* Scale hệ thống backend thực tế

### 1.1 Tổng quan kiến trúc FastAPI + SQLAlchemy + PostgreSQL

Kiến trúc chuẩn:

```
Client (Web / Mobile / Postman)
        ↓
FastAPI (Controller / Router)
        ↓
Service layer (Business logic)
        ↓
SQLAlchemy ORM
        ↓
PostgreSQL Database
```

Trong đó:

* FastAPI: xử lý HTTP, validation, routing
* SQLAlchemy: ORM (Object Relational Mapping)
* PostgreSQL: hệ quản trị CSDL quan hệ

---

### 1.2 Cài đặt DB

#### 1.2.1 Cài PostgreSQL (local)

Cách 1: Cài trực tiếp
* Download từ: https://www.postgresql.org
* Cài đặt và tạo database

Cách 2: Dùng Docker (dev thường dùng)

```bash
# docker-compose.yml

services:
  postgres:
    image: postgres:17
    container_name: pg-fastapi
    environment:
      POSTGRES_DB: techzen_academy
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: 123456@root
      TZ: Asia/Ho_Chi_Minh
    ports:
      - '5432:5432'
    volumes:
      - pgdata:/var/lib/postgresql/data
    healthcheck:
      test: [ "CMD-SHELL", "pg_isready -U postgres -d techzen_academy" ]
      interval: 5s
      timeout: 3s
      retries: 10
      start_period: 5s
    networks:
      - backend_net

volumes:
  pgdata:

networks:
  backend_net:
    name: techzen_backend_net
    driver: bridge
```

Thông tin DB:

* host: `localhost`
* port: `5432`
* user: `postgres`
* password: `123456@root`
* db: `techzen_academy`
* network: `techzen_backend_net`

### 1.2.2 Cài đặt thư viện kết nối DB

Cài SQLAlchemy trong môi trường `.venv`:

```bash
    pip install "sqlalchemy>=2.0,<3.0" psycopg2-binary
```

Trong đó:
* `sqlalchemy>=2.0,<3.0`: ORM chính
  * Giới hạn ko nâng version lên 3.0 (BREAKING CHANGE) => có thể lỗi tương thích
* `psycopg2-binary`: driver kết nối PostgreSQL

Sau khi cài xong => cập nhật lại file `requirements.txt`:

```bash
    pip freeze > requirements.txt
```

---

### 1.3 Cấu hình Database trong FastAPI

#### 1.3.1 Cấu trúc file database.py

```
app/
 ├─ main.py
 ├─ database.py
```

#### 1.3.2 Khai báo DATABASE_URL

Tạo file `.env`:

```dotenv
DATABASE_URL=postgresql+psycopg2://postgres:123456%40root@localhost:5432/techzen_academy
TZ=Asia/Ho_Chi_Minh
DB_POOL_SIZE=10
DB_MAX_OVERFLOW=20
```

Format chung:

```
postgresql+<driver>://<username>:<password>@<host>:<port>/<database_name>
```

**Lưu ý**: Password chứa `@` => thay bằng `%40`

#### 1.3.3 Setting config

Tạo file `configs/env.py`:

```python
# configs/env.py
from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    database_url: str = Field(..., validation_alias="DATABASE_URL")

    tz: str = Field(default="UTC", validation_alias="TZ")
    
    pool_size: int = Field(default=10, validation_alias="DB_POOL_SIZE")
    max_overflow: int = Field(default=20, validation_alias="DB_MAX_OVERFLOW")


@lru_cache
def settings_config() -> Settings:
    # noinspection PyArgumentList
    return Settings()
```

Trong đó:
* `BaseSettings` của `pydantic_settings` dùng để:
  * Tự động đọc biến môi trường (file `.env`, OS env)
  * Tự động kiểm tra kiểu dữ liệu
* `SettingsConfigDict` của `pydantic_settings` để cấu hình cho `Settings`:
  * `env_file = ".env"`: đọc biến môi trường từ file `.env`
  * `env_file_encoding = "utf-8"`: chỉ định encoding cho file `.env`
* `Field(..., validation_alias="DATABASE_URL")`:
  * `...` trong Pydantic: trường này bắt buộc phải có
  * `validation_alias="DATABASE_URL`: map tên biến UPPER_SNAKE_CASE từ `.env` sang biến Python snake_case
* `@lru_cache`: cache của Python => chỉ khởi tạo Settings() duy nhất 1 lần
  * Tên đầy đủ: Least Recently Used Cache

#### 1.3.3 Cấu hình SQLAlchemy Engine

Tạo file `database.py`:

```python
# configs/database.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

from configs.env import settings_config

settings = settings_config()

engine = create_engine(
    settings.database_url,
    echo=True,
    pool_pre_ping=True,
    pool_size=settings.pool_size,
    max_overflow=settings.max_overflow,
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)

Base = declarative_base()
```

Giải thích chi tiết:
* `create_engine`: quản lý kết nối DB với ứng dụng FastAPI
  * Kết nối đến DB qua `settings.database_url` 
  * `echo=True`: in log SQL ra console (chỉ bật ở DEV)
  * `pool_pre_ping=True`: tránh “kết nối chết” => param quan trọng
    * Trước khi dùng một connection trong pool, SQLAlchemy sẽ:
      * gửi 1 ping nhẹ để kiểm tra connection còn sống không
      * nếu connection đã bị DB đóng hoặc timeout => SQLAlchemy tự tạo connection mới
  * Connection Pool: SQLAlchemy sẽ tạo sẵn một nhóm kết nối => tái sử dụng lại cho các request khác
    * `pool_size=10`: giữ sẵn tối đa 10 connection
    * `max_overflow=20`: Số lượng kết nối tạm thời được phép tạo thêm khi pool đầy
    * Lưu ý KHÔNG nên để pool quá lớn:
      * DB quá tải
      * tốn RAM
      * DB từ chối kết nối
* `sessionmaker`: quản lý phiên làm việc DB
  * Session = 1 phiên làm việc với DB
    * Mỗi request FastAPI sẽ dùng 1 session riêng
    * Tránh chia sẻ session giữa các request


Tạo file `models/base.py`:

```python
from sqlalchemy.orm import DeclarativeBase

class Base(DeclarativeBase):
    # Base hiện tại chưa cần thêm logic
    # nhưng bắt buộc phải tồn tại như một lớp con
    # để SQLAlchemy sử dụng
    pass
```

* `Base = declarative_base()`: class cha cho tất cả ORM Models dùng để:
  * Tạo bảng
  * Mapping Python class <=> DB table
 
Chỉ nâng cấp lên Async DB khi:
* Dự án lớn cần xử lý đồng thời hàng ngàn I/O request
* Ứng dụng có sử dụng `WebSocket` / `Streaming` => bắt buộc Async DB

#### 1.3.4 Kiểm tra kết nối DB

1. Test nhanh DB có tồn tại

    ```bash
        docker exec -it pg-fastapi bash
        psql -U postgres
        \list
    ```

2. Test ứng dụng FastAPI kết nối DB bằng endpoint `/health/db`:

Thêm endpoint `/health/db`

```python
from fastapi import APIRouter
from sqlalchemy import text
from configs.database import SessionLocal

health_router = APIRouter()


@health_router.get("/health/db")
def health_db():
    db = SessionLocal()
    try:
        db.execute(text("SELECT 1"))
        return {"status": "ok"}
    finally:
        db.close()
```

Đăng ký router trong `main.py`

```python
app.include_router(health_router, tags=["Health"])
```

Lưu ý: Cần tắt PostgreSQL service trên hệ điều hành vì nó chiếm port 5432 => ko kết nối được DB `techzen_academy` trong pg-fastapi

---

### 1.4 Best Practices

* Không hard-code password trong production
* Dùng `.env` + `pydantic-settings`
* Mỗi request dùng 1 DB session
* Không gọi SQL trực tiếp trong controller
* DB config nằm riêng trong `database.py`

> Lưu ý
> * `SessionLocal` chỉ là factory để khởi tạo session
> * Việc inject DB session theo request sẽ được thực hiện bằng `Depends(get_db)` => chi tiết ở phần sau

---

## 2) SQLAlchemy Models (tầng persistence)

### 2.1 Persistence layer

Trong kiến trúc backend, **persistence layer** là tầng chịu trách nhiệm:
* Lưu dữ liệu xuống DB
* Đọc dữ liệu từ DB
* Đảm bảo dữ liệu phù hợp cấu trúc bảng và ràng buộc (constraints)

Trong FastAPI + SQLAlchemy:
* Persistence layer được mô tả thông qua **SQLAlchemy models**
* Mỗi model thường tương ứng với **1 bảng** trong PostgreSQL

---

### 2.2 ORM

**ORM (Object–Relational Mapping)**: ánh xạ `Object (Python class) <=> Relational table (DB table)`

Lợi ích khi dùng ORM:
* Code thao tác DB theo hướng đối tượng (ít viết SQL thủ công)
* Tăng tốc phát triển CRUD
* Dễ refactor và mở rộng
* Giảm lỗi do nối chuỗi SQL

> Lưu ý: ORM không thay thế hoàn toàn SQL. Dự án lớn vẫn cần query tối ưu (SQL thuần hoặc SQLAlchemy Core)

---

### 2.3 Model vs Schema

| Thành phần           | Dùng cho                         | Thư viện   | Tầng         | Ví dụ                         |
|----------------------|----------------------------------|------------|--------------|-------------------------------|
| **SQLAlchemy Model** | Lưu/đọc DB (table)               | SQLAlchemy | Persistence  | `Student`, `Task`             |
| **Pydantic Schema**  | Validate request/format response | Pydantic   | API Contract | `StudentCreate`, `StudentOut` |

Nguyên tắc:

* **Model** = cấu trúc dữ liệu trong DB (có PK, constraint, index, relationship)
* **Schema** = cấu trúc dữ liệu API (có field required/optional theo use-case)

---

### 2.4 Các thành phần bắt buộc của một SQLAlchemy model

#### 2.4.1 `Base`

Mọi model phải kế thừa từ `Base` (đã khai báo trong `database.py`):

```python
from app.database import Base
```

#### 2.4.2 `__tablename__`

Tên bảng trong DB:

```python
__tablename__ = "students"
```

Quy ước:
* Dùng **snake_case**
* Dùng **số nhiều** cho bảng (`students`, `tasks`)

#### 2.4.3 `Column` + kiểu dữ liệu

Mỗi cột DB là một `Column(...)`:

```python
from sqlalchemy import Column, Integer, String

id = Column(Integer, primary_key=True, index=True)
name = Column(String(100), nullable=False)
```

---

### 2.5 Các kiểu dữ liệu phổ biến trong PostgreSQL qua SQLAlchemy

| PostgreSQL | SQLAlchemy                  | Gợi ý dùng             |
|------------|-----------------------------|------------------------|
| INTEGER    | `Integer`                   | id, age                |
| BIGINT     | `BigInteger`                | số lớn                 |
| VARCHAR    | `String(length)`            | name, email            |
| TEXT       | `Text`                      | mô tả dài              |
| BOOLEAN    | `Boolean`                   | active, deleted        |
| DATE       | `Date`                      | ngày                   |
| TIMESTAMP  | `DateTime`                  | created_at, updated_at |
| NUMERIC    | `Numeric(precision, scale)` | tiền, số thập phân     |

> Thực tế dự án: `String` nên đặt length rõ ràng để tránh dữ liệu “trôi”

---

### 2.6 Primary Key, Index, Unique, Nullable

#### 2.6.1 Primary Key

```python
id = Column(Integer, primary_key=True, index=True)
```

* `primary_key=True`: PK
* `index=True`: tạo index để query nhanh theo id

#### 2.6.2 Nullable

```python
name = Column(String(100), nullable=False)
```

* `nullable=False`: NOT NULL

#### 2.6.3 Unique

```python
email = Column(String(255), unique=True, nullable=False)
```

* `unique=True`: không cho trùng giá trị

---

### 2.7 Model Student

Tạo file `models/student.py` (theo chuẩn SQLAlchemy 2.0 typing):

class Mapped:
pass

```python
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from models.base import Base


class Student(Base):
    __tablename__ = "students"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    
    full_name: Mapped[str] = mapped_column(String(100), nullable=False)
    age: Mapped[int] = mapped_column(nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    phone_number: Mapped[str | None] = mapped_column(String(20))

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
```

Chú thích:
* Sử dụng `Mapped[]` và `mapped_column()` theo chuẩn SQLAlchemy 2.0 typing thay cho `Column`
* `func.now()`: lấy thời gian từ DB server (đảm bảo đồng nhất)
* `onupdate=func.now()`: tự cập nhật khi record đổi (phù hợp logging audit)

---

### 2.8 Model Task

Tạo file `models/task.py` (chuẩn SQLAlchemy thông thường):

```python
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.sql import func

from models.base import Base


class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)

    title = Column(String(200), nullable=False)
    is_done = Column(Boolean, nullable=False, default=False)

    # Quan hệ (FK) - sẽ học relationship ở phần sau, nhưng có thể chuẩn bị trước
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
```

---

### 2.9 Import models để tạo bảng

Trong `models/__init__.py`:

```python
from .student import Student
from .task import Task
```

Mục đích:
* Khi import `models` => toàn bộ model được load
* Dễ gọi `Base.metadata.create_all(...)` hoặc dùng Alembic

---

### 2.10 Tạo bảng nhanh (dev-only) bằng `create_all`

> Thực tế sẽ dùng Alembic migration

Tạo `init_db.py`:

```python
from contextlib import asynccontextmanager

from configs.database import engine
from models.base import Base
import models # đảm bảo models được import để Base.metadata có tables

@asynccontextmanager
async def db_lifespan():
    Base.metadata.create_all(bind=engine)
    yield
    print("App shutting down...")
    engine.dispose()
```

Chú thích:
* `Base.metadata.create_all(...)`: tạo bảng nếu chưa tồn tại
* `yield`: tạo ngữ cảnh để biến `@asynccontextmanager` thành 1 context manager (giống with statement)
  * Trước `yield` => chạy khi app khởi động
  * Sau `yield` => chạy khi app shutdown

Gắn `db_lifespan` vào `app = FastAPI()` trong `main.py`:

```python
app = FastAPI(lifespan=db_lifespan)
```

Kiểm tra bảng đã được tạo chưa bằng `psql`/`pgAdmin4`

---

### 2.11 TimeMixin: tái sử dụng các column thời gian

Vấn đề: 
* 2 model `Student` và `Task` đều đang có cột `created_at`, `updated_at`
* Nếu tăng lên chục model => lặp code

Định nghĩa TimeMixin:

```python
# models/mixins.py
from sqlalchemy import Column, DateTime
from sqlalchemy.sql import func


class TimeMixin:
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
```

Lưu ý:
* Không kế thừa `Base`
* Chỉ chứa field dùng chung
* Có thể gắn vào nhiều model

Sử dụng TimeMixin trong model:

```python
class Student(TimeMixin, Base):
    __tablename__ = "students"

    id = Column(Integer, primary_key=True, index=True)

    full_name = Column(String(100), nullable=False)
    age = Column(Integer, nullable=False)

    email = Column(String(255), unique=True, nullable=False)
```

```python
class Task(TimeMixin, Base):
    __tablename__ = "tasks"
    ...
```

Lưu ý thứ tự kế thừa:
* Mixin trước, Base sau => SQLAlchemy đọc đúng metadata
* Sai thứ tự kế thừa có thể gây lỗi mapping khó debug

---

## 3) Mapping giữa Model & Schema

### 3.1 Sự cần thiết của Mapping giữa Model & Schema

Trong thực tế:
* **Model (SQLAlchemy)** đại diện cho dữ liệu trong DB
* **Schema (Pydantic)** đại diện cho dữ liệu đi qua API

Hai tầng này **KHÔNG nên dùng chung một class**, vì:
* Không phải field nào trong DB cũng được phép expose ra API
* Request và Response có cấu trúc khác nhau
* Tránh lộ dữ liệu nhạy cảm (password, internal flag, ...)
* Dễ thay đổi API mà không ảnh hưởng DB

=> Vì vậy cần **mapping rõ ràng** giữa `Model <=> Schema`

---

### 3.2 Các loại Schema thường gặp trong CRUD

Ví dụ với entity `Student`:

| Schema          | Mục đích                        | Khi dùng       |
|-----------------|---------------------------------|----------------|
| `StudentCreate` | Dữ liệu client gửi khi tạo mới  | POST           |
| `StudentUpdate` | Dữ liệu client gửi khi cập nhật | PUT / PATCH    |
| `StudentOut`    | Dữ liệu trả về cho client       | GET / Response |

Nguyên tắc Schema:
* **Create**: không có `id`, `created_at`, `updated_at`
* **Update**: các field thường là `optional`
* **Out**: chỉ chứa field được phép public

---

### 3.3 Khai báo Pydantic Schema cho Student

Tạo file `schemas/request/student_schema.py`:

```python
from datetime import datetime
from pydantic import BaseModel, EmailStr


class StudentCreate(BaseModel):
    full_name: str
    age: int
    email: EmailStr


class StudentUpdate(BaseModel):
    full_name: str | None = None
    age: int | None = None


class StudentOut(BaseModel):
    id: int
    full_name: str
    age: int
    email: EmailStr
    created_at: datetime
    updated_at: datetime

    class Config:
        # Cho phép map trực tiếp từ SQLAlchemy ORM object
        from_attributes = True
```

Tạo file `schemas/response/student_out_schema.py`:

```python
from datetime import datetime
from pydantic import BaseModel, EmailStr


class StudentOut(BaseModel):
    id: int
    full_name: str
    age: int
    email: EmailStr
    phone_number: str | None = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
```

Chú thích:
* `from_attributes = True`: cho phép Pydantic đọc dữ liệu trực tiếp từ ORM object
  * Đây là **key quan trọng nhất** để mapping Model => Schema
  * Dùng cho schema OUTPUT, nơi thực hiện:
    * trả ORM object
    * serialize ra JSON

---

### 3.4 Mapping Model => Schema (ORM => Response)

Sau khi query từ DB để lấy object `Student`:

```python
# query lấy student đầu tiên 
student = db.query(Student).first()
```

Chuyển sang schema response bằng `model_validate` của Pydantic:

```python
student_out = StudentOut.model_validate(student)
```

FastAPI cũng hỗ trợ tự động mapping khi khai báo `response_model`:

```python
@router.get("/{student_id}", response_model=StudentOut)
def get_student(student_id: int, db: Session = Depends(get_db)):
    student = db.query(Student).get(student_id) # thực tế controller KHÔNG trực tiếp query 
    return student
```

FastAPI sẽ:
* Nhận ORM object
* Dùng `from_attributes=True`
* Convert sang JSON đúng schema `StudentOut`

---

### 3.5 Mapping Schema => Model (Request => ORM)

Khi tạo mới Student:

```python
def create_student(db: Session, data: StudentCreate) -> Student:
    student = Student(
        full_name=data.full_name,
        age=data.age,
        email=data.email,
    )
    db.add(student)
    db.commit()
    db.refresh(student)
    return student
```

Nguyên tắc:
* Schema **chỉ dùng để đọc dữ liệu request**
* Model **chỉ dùng để làm việc với DB**
* Không nhét logic DB vào schema

---

### 3.6 Update mapping (Schema Update => Model)

Ví dụ update Student:

```python
def update_student(db: Session, student: Student, data: StudentUpdate) -> Student:
    if data.full_name is not None:
        student.full_name = data.full_name
    if data.age is not None:
        student.age = data.age

    db.commit()
    db.refresh(student)
    return student
```

Hoặc cách ngắn gọn hơn bằng `model_dump`:

```python
update_data = data.model_dump(exclude_unset=True)
for field, value in update_data.items():
    setattr(student, field, value)
```

Chú thích:
* `exclude_unset=True`: chỉ lấy những field client đã gửi
  * Client gửi `{ "full_name": "New Name" }` và nếu ko dùng `exclude_unset`: 
    * `age` sẽ là `None`
    * Có thể ghi đè dữ liệu cũ
* Duyệt qua từng cặp `field = value` để gán tự động vào ORM object bằng `setattr` 

---

### 3.7 Best Practices khi thiết kế Mapping

* Model ≠ Schema
* Mỗi use-case có schema riêng
* Response luôn dùng `response_model` của router
* Mapping rõ ràng giúp code:
  * Dễ test
  * Dễ maintain
  * An toàn dữ liệu

---

## 4) Alembic Migration (Quản lý schema Database)

### 4.1 Lý do KHÔNG dùng `Base.metadata.create_all()` trong PRODUCTION

Hạn chế nghiêm trọng của `Base.metadata.create_all()`:

* Không quản lý được lịch sử thay đổi schema
* Không biết DB đang ở version nào
* Không rollback được khi deploy lỗi
* Mỗi dev tự tạo bảng => lệch schema

Trong thực tế, **schema DB phải được version hóa** giống như source code

---

### 4.2 Alembic

**Alembic** là công cụ migration chính thức của SQLAlchemy, dùng để:
* Theo dõi thay đổi schema DB theo thời gian
* Tự tạo file migration (DDL)
* Upgrade / downgrade DB theo version

Tư duy cốt lõi:

```text
Model thay đổi => generate migration => commit migration => chạy migration
```

---

### 4.3 Cài đặt Alembic

Trong môi trường `.venv`:

```bash
    pip install alembic
```

Cập nhật `requirements.txt`:

```bash
    pip freeze > requirements.txt
```

---

### 4.4 Khởi tạo Alembic

Tại thư mục root của project:

```bash
    alembic init alembic
```

Cấu trúc được tạo:

```
alembic/
 ├─ versions/ # các file migration
 ├─ env.py # cấu hình kết nối DB & metadata
 ├─ script.py.mako
alembic.ini
```

---

### 4.5 Cấu hình Alembic cho FastAPI project

#### 4.5.1 Kết nối Alembic với SQLAlchemy Models

Mở `alembic/env.py`:

```python
from logging.config import fileConfig

from sqlalchemy import engine_from_config, pool
from alembic import context

from models.base import Base
from configs.env import settings_config

# IMPORTANT: import all models so Base.metadata is populated
import models  # noqa: F401

# Alembic Config object
config = context.config

# Setup Python logging
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Metadata for 'autogenerate'
target_metadata = Base.metadata

# Load settings
settings = settings_config()


def get_url() -> str:
    return settings.database_url


def run_migrations_offline() -> None:
    context.configure(
        url=get_url(),  # lấy từ .env
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    connectable = engine_from_config(
        {
            **config.get_section(config.config_ini_section, {}),
            "sqlalchemy.url": get_url(),  # override URL
        },
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
```

Lưu ý:
* `import models`: đảm bảo toàn bộ model đã được load
  * `Base.metadata` mới có table
  * Khi chạy `alembic revision --autogenerate` mới tạo đúng migration
    * Nếu ko `import models` sẽ là migration rỗng, ko có table
* `target_metadata`: Alembic dùng metadata này để detect thay đổi schema
* `compare_type=True`: Alembic sẽ phát hiện được thay đổi khi so sánh kiểu dữ liệu:
  * Khi có thay đổi:
    * `String(100)` => `String(255)`
    * `nullable=False` => `nullable=True`
    * `DateTime(timezone=False)` => `DateTime(timezone=True)`
  * Khi chạy Alembic sẽ autogenerate lệnh `ALTER COLUMN ... TYPE`

---

#### 4.5.2 Cấu hình file `alembic.ini`

Lưu ý không hard-code URL ở đây, mà đã lấy từ `settings` bên `alembic/env.py`

Chỉ cần điều chỉnh `script_location`:

```ini
[alembic]
script_location = alembic
```

---

### 4.6 Tạo migration đầu tiên

Lưu ý: Vì đã dùng Alembic => cần xóa `init_db.py` với `Base.metadata.create_all()`
* Nếu không `create_all()` chạy trước => khiến bảng đã tồn tại => Alembic không kiểm soát 

Tạo migration với 2 model `Student`, `Task` đã có:

```bash
    alembic revision --autogenerate -m "create student and task tables"
```

Kết quả:
* Tạo file trong `alembic/versions/`
* Chứa các lệnh `op.create_table(...)`

---

### 4.7 Chạy migration

Upgrade DB lên version mới nhất:

```bash
    alembic upgrade head
```

Kiểm tra trong DB:
* Có bảng `alembic_version` với version mới được auto-gen
* Có bảng `students`, `tasks`

---

### 4.8 Rollback migration

Khi muốn quay về version trước:

```bash
    alembic downgrade -1
```

Hoặc về version cụ thể:

```bash
    alembic downgrade <revision_id>
```

---

### 4.9 Thay đổi schema & tạo migration mới

Thêm cột `phone_number` vào `Student`, flow cần tuân theo:

1. Sửa model:

```python
phone_number: Mapped[str | None] = mapped_column(String(20))
```

2. Auto-gen migration:

```bash
    alembic revision --autogenerate -m "add phone_number to student"
```

3. Chạy migration:

```bash
    alembic upgrade head
```

---

### 4.10 Seeding dữ liệu mẫu

Tạo Script seeding riêng `scripts/seed_student_data.py`:

```python
from configs.database import SessionLocal
from models.student import Student

def seed_students():
    db = SessionLocal()
    try:
        if db.query(Student).count() == 0:
            db.add_all([
                Student(full_name="Demo A", age=20, email="a@test.com"),
                Student(full_name="Demo B", age=22, email="b@test.com"),
            ])
            db.commit()
    finally:
        db.close()

if __name__ == "__main__":
    seed_students()
```

Chạy bằng `-m` (module) để import và load đúng file `.venv`:

```bash
    python -m scripts.seed_student_data
```

---

### 4.11 Best Practices khi dùng Alembic

* Không sửa trực tiếp DB bằng tay
* Không xóa file migration đã commit
* Mỗi thay đổi schema = 1 migration
* Commit migration cùng code
* Review file migration trước khi chạy
* Production chỉ dùng `upgrade`, hạn chế `downgrade`

---

## 5) Thao tác với DB (Repository => Service => Router)

### 5.1 Tổng quan luồng xử lý CRUD chuẩn

Luồng xử lý cho một request CRUD:

```
HTTP Request
   ↓
DB Middleware
  - create Session
  - attach to request.state
   ↓
Router (API layer)
   ↓ Depends(get_db)
DB Session (per-request)
   ↓
Service layer (business logic)
   ↓
Repository (DB access)
   ↓
SQLAlchemy ORM
   ↓
PostgreSQL
```

Nguyên tắc cốt lõi:
* Router **không query DB trực tiếp**
* Service **không cần phải biết HTTP**
* Repository **không biết request / response**

---

### 5.2 Middleware tạo DB session

Mục đích của DBSessionMiddleware:

> Tạo và quản lý DB Session cho mỗi HTTP request, đảm bảo:
> * mỗi request có 1 session riêng
> * commit / rollback tự động
> * không bị leak connection

```python
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from sqlalchemy.orm import Session

from configs.database import SessionLocal


class DBSessionMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        db: Session = SessionLocal()
        request.state.db = db

        try:
            response = await call_next(request)
            db.commit()
            return response
        except Exception:
            db.rollback()
            raise
        finally:
            db.close()
```

Giải thích chi tiết:
* `BaseHTTPMiddleware`: DBSessionMiddleware kế thừa class này để:
  * Middleware chạy trước và sau mỗi request
  * Áp dụng cho toàn bộ API
* `db: Session = SessionLocal()`: tạo 1 phiên làm việc với DB
* `request.state`: mỗi request có session độc lập, không dùng chung
  * nơi lưu dữ liệu riêng cho request
  * controller/service có thể truy cập lại bằng `request.state.db`
* `await call_next(request)`: chuyển request đến bước kế tiếp (middleware tiếp theo => controller)
* `db.commit()`: nếu không có lỗi => lưu toàn bộ thay đổi vào DB
* `db.rollback()`: nếu gặp lỗi => huỷ toàn bộ thay đổi trong transaction

---

### 5.3 Đăng ký middleware trong main.py

```python
from fastapi import FastAPI
from core.middlewares.db_session import DBSessionMiddleware

app = FastAPI()
app.add_middleware(DBSessionMiddleware)  # type: ignore[arg-type]
```

Chú thích:
* `# type: ignore[arg-type]`: bỏ qua cảnh báo kiểu tham số đối với `add_middleware`

---

### 5.4 Dependency Injection DB session (`get_db`)

Tạo file `dependencies/db.py` để tiêm phụ thuộc:

```python
from fastapi import Request
from sqlalchemy.orm import Session


def get_db(request: Request) -> Session:
    return request.state.db
```

Sử dụng trong router:

```python
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from dependencies.db import get_db
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
def create_user(user: UserCreate, db: Session = Depends(get_db)) -> UserOut:
    ...
```

---

### 5.5 Repository layer: truy cập DB

#### 5.5.1 Trách nhiệm của Repository

Repository là tầng truy cập dữ liệu:
* Chỉ làm việc với SQLAlchemy ORM / SQL
* Không cần biết HTTP request/response
* Không xử lý rule nghiệp vụ
* Không commit/rollback/close session (vì middleware đã quản lý transaction)

> Nguyên tắc: “Repository chỉ query/ghi dữ liệu, không cần quản transaction”

#### 5.5.2 BaseRepository

Tạo BaseRepository chứa CRUD cơ bản để dùng chung cho tất cả repo khác:

```python
# repositories/base_repository.py

from typing import Any, Generic, Type, TypeVar
from sqlalchemy import select
from sqlalchemy.orm import Session

from models.base import Base

ModelType = TypeVar("ModelType", bound=Base)


class BaseRepository(Generic[ModelType]):
    def __init__(self, model: Type[ModelType]):
        self.model = model

    # -------- READ --------
    def get_by_id(self, db: Session, entity_id: Any) -> ModelType | None:
        stmt = select(self.model).where(self.model.id == entity_id)  # type: ignore[attr-defined]
        return db.execute(stmt).scalars().first()

    def list(self, db: Session, *, offset: int = 0, limit: int = 100) -> list[ModelType]:
        stmt = select(self.model).offset(offset).limit(limit)
        return list(db.execute(stmt).scalars().all())

    # -------- WRITE --------
    def create(self, db: Session, obj: ModelType) -> ModelType:
        db.add(obj)
        db.flush()
        db.refresh(obj)
        return obj

    def update(self, db: Session, obj: ModelType, data: dict[str, Any]) -> ModelType:
        for field, value in data.items():
            setattr(obj, field, value)

        db.flush()
        db.refresh(obj)
        return obj

    def delete(self, db: Session, obj: ModelType) -> None:
        db.delete(obj)
        db.flush()
```

Giải thích chi tiết:
* `TypeVar("ModelType", bound=Base)`: khai báo một kiểu generic đại diện cho một ORM model bất kỳ,
nhưng bắt buộc phải kế thừa từ Base (SQLAlchemy DeclarativeBase)
  * `TypeVar`: tạo biến đại diện cho kiểu dữ liệu (giống như `class BaseRepository<T> extends Base { }` trong Java)
  * `bound=Base`: giới hạn kiểu `ModelType` phải là subclass của `Base` => repo chỉ làm việc với ORM models
    * Ví dụ: `class Student(Base): ...`
    * Nhờ `bound=Base` chúng ta có thể dùng `self.model` với ý nghĩa:
      * là ORM class
      * có mapping SQLAlchemy
      * có thể dùng trong `select(self.model)`
* `db: Session`: ko nên cho `BaseRepository` giữ session trong constructor
  * Tránh repo sống lâu giữ session quá vòng đời request
  * Nên truyền `db: Session` vào từng method => repo ko tạo session, chỉ sử dụng => pattern stateless repo
* `select(self.model)`: tạo câu lệnh SQLAlchemy `SELECT * FROM <table>`
  * `self.model`: là ORM class (ví dụ: `Student`)
* `db.execute(stmt)`: gửi câu SQL xuống DB => DB thực thi query
  * Kết quả trả về một `Result` chứa `Row` dạng `(Row(Student(...)),)`
* `scalars()`: bóc tách lớp `Row` để lấy ra ORM object `Student(...)`
* `first()`: lấy bản ghi đầu tiên
  * Nếu ko có bản ghi nào => trả None
  * Ko `raise exception`
* `# type: ignore[attr-defined]`: tránh cảnh báo typing trên IDE vì
  * IDE không chắc model nào cũng có `id`
  * Nhưng theo convention, mọi entity đều phải có `id` 
* Dấu `*` đứng độc lập trong chữ ký hàm: đánh dấu rằng tất cả tham số phía sau phải truyền bằng keyword
  * Nơi gọi cần phải `repo.list(db, offset=0, limit=10)` => giúp code rõ ràng
* `db.add(obj)`: đưa object vào session
* `db.flush()`: đẩy các thay đổi đang pending trong Session xuống DB
  * Ko nhận SQL như `db.execute()`
* `db.refresh(obj)`: lấy dữ liệu mới nhất từ DB

#### 5.5.1 StudentRepository

`StudentRepository` là repository cụ thể cho entity `Student`:
* Tái sử dụng CRUD cơ bản từ BaseRepository
* Viết thêm các query đặc thù của `Student` (ví dụ: get_by_email, search theo tên, kiểm tra trùng email, join, ...)
* Không chứa business rule, không commit/rollback/close session


```python
# repositories/student_repository.py

from sqlalchemy import select
from sqlalchemy.orm import Session

from models.student import Student
from repositories.base_repository import BaseRepository


class StudentRepository(BaseRepository[Student]):

    def __init__(self):
        super().__init__(Student)

    def get_by_email(self, db: Session, email: str) -> Student | None:
        stmt = select(Student).where(Student.email == email)
        return db.execute(stmt).scalars().first()

    def search(
            self,
            db: Session,
            *,
            keyword: str | None = None,
            min_age: int | None = None,
            max_age: int | None = None,
            offset: int = 0,
            limit: int = 100,
    ) -> list[Student]:
        stmt = select(Student)

        if keyword:
            stmt = stmt.where(Student.full_name.ilike(f"%{keyword}%"))

        if min_age is not None:
            stmt = stmt.where(Student.age >= min_age)

        if max_age is not None:
            stmt = stmt.where(Student.age <= max_age)

        stmt = stmt.offset(offset).limit(limit)
        return list(db.execute(stmt).scalars().all())
```

Giải thích chi tiết:
* `class StudentRepository(BaseRepository[Student])`:
  * `StudentRepository` kế thừa `BaseRepository` để dùng lại các hàm CRUD chuẩn:
    * `get_by_id(db, id)`
    * `list(db, offset, limit)`
    * `create(db, obj)`
    * `delete(db, obj)`
  * `[Student]` giúp IDE hiểu:
    * mọi kết quả trả về sẽ là `Student` thay vì ModelType kiểu chung
* `super().__init__(Student)`: Khi khởi tạo `StudentRepository`, ta truyền model `Student` cho `BaseRepository` để:
  * `self.model` trở thành `Student`
  * `select(self.model)` tương đương `select(Student)`
* `ilike("%keyword%")`: tìm kiếm không phân biệt hoa thường (Postgres)

> Best practice:
> * Repository chỉ làm việc với ORM model
> * Không commit/rollback => để tầng middleware xử lý 
> * Không xử lý validate theo rule nghiệp vụ => để tầng Service xử lý (ví dụ: “email bắt buộc unique”, ...)
> * Không `raise HTTPException`

---

### 5.4 Service layer: xử lý nghiệp vụ

#### 5.4.1 Quy tắc thiết kế Service chuẩn

1. Service không commit/rollback
   * Transaction đã do middleware quản lý
2. Service không cần biết FastAPI
   * Không dùng `Request`, không dùng `Depends`
3. Service chỉ nhận `db: Session` + data
4. Service xử lý lỗi nghiệp vụ bằng exception
   * Sử dụng custom exception

#### 5.4.2 StudentService

```python
# services/student_service.py

from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from models.student import Student
from repositories.student_repository import StudentRepository
from schemas.request.student_schema import StudentCreate, StudentUpdate


class StudentService:

    def __init__(self):
        self.repo = StudentRepository()

    # -------- READ --------
    def get_student(self, db: Session, student_id: int) -> Student:
        student = self.repo.get_by_id(db, student_id)
        if not student:
            # Tạm thời sử dụng HTTPException (buổi sau nâng cấp lên custom exception)
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Student not found",
            )
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
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="min_age must be <= max_age",
            )

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
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Email already exists",
            )

        # Rule nghiệp vụ: tuổi hợp lệ
        if data.age < 18:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Age must be >= 18",
            )

        student = Student(**data.model_dump())
        return self.repo.create(db, student)

    # PATCH
    def update_student(self, db: Session, student_id: int, data: StudentUpdate) -> Student:
        student = self.get_student(db, student_id)

        # Rule nghiệp vụ: không cho update age dưới 18
        if data.age is not None and data.age < 18:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Age must be >= 18",
            )

        # exclude_unset=True: chỉ lấy field client gửi
        updated_data = data.model_dump(exclude_unset=True)

        return self.repo.update(db, student, updated_data)

    def delete_student(self, db: Session, student_id: int) -> None:
        student = self.get_student(db, student_id)
        self.repo.delete(db, student)
```

Giải thích chi tiết:
* `Student(**data.model_dump())`: Chuyển dữ liệu từ Pydantic Schema sang ORM Model
  * `data`: Lấy dữ liệu đã validate từ pydantic schema
  * `model_dump()`: Convert pydantic schema sang dict (với pydantic v1: dùng `.dict()`)
  * `Student(...)`: Dùng dict đó để khởi tạo ORM model chưa lưu DB
  * `**`: Giải nén dict thành các keyword arguments (ví dụ `Student(full_name="Nguyen Van A", age=20, email="a@test.com")`)

> Best practice:
> * Service là nơi xử lý rule nghiệp vụ
> * Không quản transaction (đã có middleware lo)
> * Được phép raise `HTTPException` hoặc custom exception
> * Mapping Schema => Model nên thực hiện tại đây

#### 5.4.3 Phân biệt lỗi nghiệp vụ vs lỗi hệ thống

1. Lỗi nghiệp vụ (Service xử lý):

* Email đã tồn tại
* min_age > max_age
* Age < 18

=> Trả 400/409

2. Lỗi hệ thống (Middleware/DB)
* DB mất kết nối
* lỗi SQL, constraint lỗi

=> middleware rollback, FastAPI trả 500 (exception handler riêng)

---

### 5.5 Router layer: API endpoints

#### 5.5.1 Luồng xử lý trong Router

```
POST /students
   ↓
Router nhận StudentCreate (validate)
   ↓
Router lấy db session: db = Depends(get_db)
   ↓
Router gọi service.create_student(db, data)
   ↓
Service gọi repo lưu DB
   ↓
Router map Student ORM → StudentOut
   ↓
Trả response 201
```

#### 5.5.2 Response wrapper (Pydantic schema)

Response wrapper phải kế thừa `BaseModel` của Pydantic để FastAPI tự động:
* Serialize sang JSON
* Set `Content-Type`
* Apply `response_model`
* Validate output

=> đây là “happy path” chuẩn FastAPI

```python
# schemas/response/base.py

from typing import Generic, TypeVar
from pydantic import BaseModel

T = TypeVar("T")


class SuccessResponse(BaseModel, Generic[T]):
    success: bool = True
    data: T
    message: str | None = None
    trace_id: str | None = None # được tạo ở TraceIdMiddleware
```

Cách làm SAI: trả `JSONResponse`
* Router mất `response_model
* Swagger không biết schema thật
* Data bị serialize 2 lần
* Pydantic bị bypass
* Service / Controller bị gắn chặt HTTP response

```python
def response_success(data):
    return JSONResponse(
        status_code=200,
        content={
            "success": True,
            "data": data
        }
    )
```

=> anti-pattern trong FastAPI

#### 5.5.3 TraceIdMiddleware

Tạo biến context theo từng request / coroutine:
* `ContextVar` cho phép tạo biến virtual toàn cục, nhưng mỗi request (async task) sẽ có giá trị riêng (ko giống biến global)
* `ContextVar` hoạt động thực tế như sau: giả sử có 2 request đồng thời:
  * Request A có `trace_id_ctx="abc-123"`
  * Request B có `trace_id_ctx="xyz-456"`
  * Dù chạy async, nhưng vẫn ko bị đè lên nhau

```python
# core/trace.py
from contextvars import ContextVar

trace_id_ctx: ContextVar[str | None] = ContextVar("trace_id", default=None)
```

Tạo `TraceIdMiddleware`:

```python
import uuid
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from core.trace import trace_id_ctx

TRACE_HEADER = "X-Trace-Id"


class TraceIdMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next) -> Response:
        # Luôn generate trace_id mới cho mỗi request
        trace_id = str(uuid.uuid4())

        # Gắn vào request.state để controller/service dùng
        request.state.trace_id = trace_id

        # Gắn vào contextvar để logging tự động lấy được
        token = trace_id_ctx.set(trace_id)
        try:
            response = await call_next(request)
        finally:
            # Reset context để tránh leak sang request khác
            trace_id_ctx.reset(token)

        # Trả trace_id cho client qua header
        response.headers[TRACE_HEADER] = trace_id
        return response
```

#### 5.5.4 Cấu hình Logging

```python
# core/app_logging.py
import logging
from colorlog import ColoredFormatter
from core.trace import trace_id_ctx


class TraceIdFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        record.trace_id = trace_id_ctx.get() or "n/a"
        return True

# Gọi 1 lần khi app start để
# tạo formatter có %(trace_id)s
# và gắn TraceIdFilter vào root logger
def setup_logging(sql_echo: bool = False) -> None:
    root = logging.getLogger()
    root.setLevel(logging.INFO)

    trace_filter = TraceIdFilter()

    # Nếu root đã có handler (thường do uvicorn cấu hình), gắn filter vào các handler đó
    if root.handlers:
        for h in root.handlers:
            h.addFilter(trace_filter)
    else:
        # Nếu chưa có handler nào, tự tạo handler console theo format tự cấu hình
        handler = logging.StreamHandler()
        formatter = ColoredFormatter(
            fmt="%(log_color)s %(asctime)s %(levelname)s [trace_id=%(trace_id)s] %(name)s: %(message)s",
            log_colors={
                "DEBUG": "white",
                "INFO": "green",
                "WARNING": "yellow",
                "ERROR": "red",
                "CRITICAL": "bold_red",
            }
        )
        handler.setFormatter(formatter)
        handler.addFilter(trace_filter)
        root.addHandler(handler)

    # DEV ONLY: bật SQLAlchemy engine log qua hệ logging hiện tại
    sa_logger = logging.getLogger("sqlalchemy.engine")
    sa_logger.setLevel(logging.INFO if sql_echo else logging.WARNING)
    sa_logger.propagate = True
```

Tắt `echo=True` làm SQLAlchemy bật logging/echo ở mức INFO để tránh dup log DB:

```python
engine = create_engine(
    settings.database_url,
    echo=False, # tắt echo để tránh duplicate log DB
    pool_pre_ping=True,
    pool_size=settings.pool_size,
    max_overflow=settings.max_overflow,
)
```

Đăng ký `TraceIdMiddleware` và gọi `setup_logging()` trong `main.py`:

```python
from fastapi import FastAPI

from configs.env import settings_config
from controllers.health_controller import health_router
from controllers.student_controller import student_router
from controllers.user_controller import user_router
from core.app_logging import setup_logging
from core.middlewares.db_session import DBSessionMiddleware
from core.middlewares.trace_id import TraceIdMiddleware

app = FastAPI()

settings = settings_config()
setup_logging(sql_echo=(settings.environment == "DEV"))

# Đăng ký router
app.include_router(health_router, tags=["Health"])
app.include_router(user_router, prefix="/users", tags=["Users"])
app.include_router(student_router, prefix="/students", tags=["Students"])

app.add_middleware(DBSessionMiddleware)
app.add_middleware(TraceIdMiddleware)  # add sau để bọc ngoài
```

**Lưu ý**:
* KHÔNG bật SQL log ở PROD vì:
  * lộ cấu trúc DB, query, đôi khi lộ dữ liệu
  * log rất lớn, tốn chi phí

#### 5.5.5 Student controller

Quy tắc ngầm định của FastAPI:
* FastAPI tự hiểu Query Param khi:
  * Tham số không nằm trong path (`/search` không có `{}`)
  * Không phải `Depends(...)`
  * Không phải Pydantic model (kế thừa `BaseModel`)
* FastAPI tự hiểu Request Body khi:
  * Là Pydantic BaseModel
  * Không có `Depends`
  * Không nằm trong path

Lưu ý thứ tự khai báo route và kiểu tham số:
* Luôn khai báo route tĩnh trước route động (route có `{}`)
* Nên khai báo ràng buộc kiểu cho path param
  * `@student_router.get("/{student_id:int}")`
  * `"/{student_id:int}"`: ko có space, nếu có space trả lỗi `405`


```python
# controllers/student_controller.py

from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.orm import Session

from dependencies.db import get_db
from schemas.request.student_schema import StudentCreate, StudentUpdate
from schemas.response.base import SuccessResponse
from schemas.response.error_response import ErrorResponse
from schemas.response.student_out_schema import StudentOut
from services.student_service import StudentService

student_router = APIRouter()
service = StudentService()


@student_router.get("", response_model=SuccessResponse[list[StudentOut]])
def list_students(
        offset: int = 0,
        limit: int = 100,
        db: Session = Depends(get_db),
) -> SuccessResponse[list[StudentOut]]:
    students = service.list_students(db, offset=offset, limit=limit)
    data = [StudentOut.model_validate(student) for student in students]
    return SuccessResponse(data=data)


@student_router.get(
    "/{student_id:int}",
    response_model=SuccessResponse[StudentOut],
    responses={404: {"model": ErrorResponse, "description": "Student not found"}},
)
def get_student(
        student_id: int,
        db: Session = Depends(get_db),
) -> SuccessResponse[StudentOut]:
    student = service.get_student(db, student_id)
    return SuccessResponse(data=StudentOut.model_validate(student))


@student_router.get(
    "/search",
    response_model=SuccessResponse[list[StudentOut]],
    responses={
        400: {
            "model": ErrorResponse,
            "description": "Invalid search parameters (business rule violation)"
        }
    }
)
def search_students(
        keyword: str | None = None,
        min_age: int | None = None,
        max_age: int | None = None,
        offset: int = 0,
        limit: int = 100,
        db: Session = Depends(get_db),
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
    return SuccessResponse(data=data)


@student_router.post(
    "",
    response_model=SuccessResponse[StudentOut],
    status_code=status.HTTP_201_CREATED,
    responses={
        400: {"model": ErrorResponse, "description": "Business validation error"},
        409: {"model": ErrorResponse, "description": "Email already exists"}
    },
)
def create_student(
        data: StudentCreate,
        response: Response,
        db: Session = Depends(get_db),
) -> SuccessResponse[StudentOut]:
    student = service.create_student(db, data)

    # Set Location header
    response.headers["location"] = f"/students/{student.id}"

    return SuccessResponse(data=StudentOut.model_validate(student))


@student_router.patch(
    "/{student_id}",
    response_model=SuccessResponse[StudentOut],
    responses={
        400: {"model": ErrorResponse, "description": "Business validation error"},
        404: {"model": ErrorResponse, "description": "Not found"},
    }
)
def update_student(
        student_id: int,
        data: StudentUpdate,
        db: Session = Depends(get_db),
) -> SuccessResponse[StudentOut]:
    student = service.update_student(db, student_id, data)
    return SuccessResponse(data=StudentOut.model_validate(student))


@student_router.delete(
    "/{student_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={404: {"model": ErrorResponse, "description": "Not found"}},
)
def delete_student(
        student_id: int,
        db: Session = Depends(get_db),
) -> None:
    service.delete_student(db, student_id)
    return None
```

Giải thích thêm:
* Theo patter chuẩn REST, đối với `POST /students` nên trả kèm field `location` trong header
  * `response.headers["Location"]`: set url cho `location`

---

### 5.6 Đăng ký router trong `main.py`

```python
from fastapi import FastAPI

from controllers.student_controller import student_router

app = FastAPI()
app.include_router(student_router, prefix="/students", tags=["Students"])
```

---

### 5.7 Lưu ý kiến trúc CRUD chuẩn

* Router không query DB
* Repository ko cần biết HTTP
* Service ko cần biết Request/Response format
* Mỗi request dùng 1 DB session
* Schema dùng cho API, Model dùng cho DB
