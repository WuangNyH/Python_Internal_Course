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
ModelType = TypeVar("ModelType", bound=Base)
```

Trong đó:
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

from configs.database import Base


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
* Sử dụng `Mapped[]` và `mapped_column()` theo chuẩn SQLAlchemy 2.0 typing
* `func.now()`: lấy thời gian từ DB server (đảm bảo đồng nhất)
* `onupdate=func.now()`: tự cập nhật khi record đổi (phù hợp logging audit)

---

### 2.8 Model Task

Tạo file `models/task.py` (chuẩn SQLAlchemy thông thường):

```python
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.sql import func

from configs.database import Base


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

### 2.9 Import models để tạo bảng (chuẩn bị cho bước tạo bảng)

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

from configs.database import engine, Base
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

from configs.database import Base
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



## 5) CRUD với DB (get_db → Repository → Service → Router)

> Mục tiêu của phần này:
>
> * Hiểu **luồng xử lý đầy đủ của 1 request CRUD** trong FastAPI
> * Biết cách **inject DB session đúng chuẩn** bằng `Depends(get_db)`
> * Áp dụng **Repository pattern** để tách logic DB
> * Áp dụng **Service layer** để xử lý nghiệp vụ
> * Hoàn thiện CRUD API theo kiến trúc clean, dễ mở rộng

---

### 5.1 Tổng quan luồng xử lý CRUD chuẩn

Luồng xử lý cho một request CRUD:

```
HTTP Request
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
* Service **không biết HTTP**
* Repository **không biết request / response**

---

### 5.2 Dependency Injection DB session (`get_db`)

Tạo file `deps/db.py`:

```python
from typing import Generator
from sqlalchemy.orm import Session

from configs.database import SessionLocal


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

Giải thích:

* `SessionLocal()` tạo **session mới cho mỗi request**
* `yield` cho FastAPI quản lý lifecycle
* `finally: close()` đảm bảo không leak connection

---

### 5.3 Repository layer – truy cập DB

Tạo thư mục:

```
app/
 ├─ repositories/
 │   └─ student_repository.py
```

#### 5.3.1 StudentRepository

```python
from sqlalchemy.orm import Session

from models.student import Student


class StudentRepository:
    def get_by_id(self, db: Session, student_id: int) -> Student | None:
        return db.get(Student, student_id)

    def list(self, db: Session) -> list[Student]:
        return db.query(Student).all()

    def create(self, db: Session, student: Student) -> Student:
        db.add(student)
        db.commit()
        db.refresh(student)
        return student

    def delete(self, db: Session, student: Student) -> None:
        db.delete(student)
        db.commit()
```

Ghi chú:

* Repository **chỉ làm việc với ORM model**
* Không xử lý validate nghiệp vụ
* Không raise HTTPException

---

### 5.4 Service layer – xử lý nghiệp vụ

Tạo thư mục:

```
app/
 ├─ services/
 │   └─ student_service.py
```

#### 5.4.1 StudentService

```python
from sqlalchemy.orm import Session
from fastapi import HTTPException

from models.student import Student
from schemas.request.student_schema import StudentCreate, StudentUpdate
from repositories.student_repository import StudentRepository


class StudentService:
    def __init__(self):
        self.repo = StudentRepository()

    def get_by_id(self, db: Session, student_id: int) -> Student:
        student = self.repo.get_by_id(db, student_id)
        if not student:
            raise HTTPException(status_code=404, detail="Student not found")
        return student

    def list(self, db: Session) -> list[Student]:
        return self.repo.list(db)

    def create(self, db: Session, data: StudentCreate) -> Student:
        student = Student(
            full_name=data.full_name,
            age=data.age,
            email=data.email,
        )
        return self.repo.create(db, student)

    def update(self, db: Session, student_id: int, data: StudentUpdate) -> Student:
        student = self.get_by_id(db, student_id)

        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(student, field, value)

        db.commit()
        db.refresh(student)
        return student

    def delete(self, db: Session, student_id: int) -> None:
        student = self.get_by_id(db, student_id)
        self.repo.delete(db, student)
```

Ghi chú:

* Service là nơi **validate nghiệp vụ**
* Được phép raise `HTTPException`
* Mapping Schema → Model diễn ra tại đây

---

### 5.5 Router layer – API endpoints

Tạo file `routers/student_router.py`:

```python
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from deps.db import get_db
from schemas.request.student_schema import StudentCreate, StudentUpdate
from schemas.request.student_schema import StudentOut
from services.student_service import StudentService

router = APIRouter(prefix="/students", tags=["Students"])
service = StudentService()


@router.get("/{student_id}", response_model=StudentOut)
def get_student(student_id: int, db: Session = Depends(get_db)):
    return service.get_by_id(db, student_id)


@router.get("", response_model=list[StudentOut])
def list_students(db: Session = Depends(get_db)):
    return service.list(db)


@router.post("", response_model=StudentOut, status_code=201)
def create_student(data: StudentCreate, db: Session = Depends(get_db)):
    return service.create(db, data)


@router.put("/{student_id}", response_model=StudentOut)
def update_student(
    student_id: int,
    data: StudentUpdate,
    db: Session = Depends(get_db),
):
    return service.update(db, student_id, data)


@router.delete("/{student_id}", status_code=204)
def delete_student(student_id: int, db: Session = Depends(get_db)):
    service.delete(db, student_id)
    return None
```

---

### 5.6 Đăng ký router trong `main.py`

```python
from fastapi import FastAPI

from routers.student_router import router as student_router

app = FastAPI()
app.include_router(student_router)
```

---

### 5.7 Checklist kiến trúc CRUD chuẩn

* Router không query DB
* Repository không biết HTTP
* Service không biết Request/Response format
* Mỗi request dùng 1 DB session
* Schema dùng cho API, Model dùng cho DB

---

### 5.8 Bài tập thực hành

1. Hoàn thiện CRUD cho `Task`
2. Tạo `TaskRepository`, `TaskService`, `TaskRouter`
3. Áp dụng `response_model`
4. Test bằng Swagger UI

---

✅ Kết thúc Phần 5 – CRUD với DB (get_db → Repository → Service → Router)

➡️ Buổi tiếp theo: **Testing (pytest) & Error Handling nâng cao**
