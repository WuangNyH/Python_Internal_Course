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

### 1.2 PostgreSQL

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

---






## 1.4 Cài đặt thư viện kết nối DB

Trong môi trường `.venv`:

```bash
    pip install sqlalchemy psycopg2-binary
```

Giải thích:

* `sqlalchemy`: ORM chính
* `psycopg2-binary`: driver kết nối PostgreSQL

Sau khi cài xong:

```bash
pip freeze > requirements.txt
```

---

## 1.5 Cấu hình Database trong FastAPI

### 1.5.1 Tổ chức file database.py

Tạo file:

```
app/
 ├─ main.py
 ├─ database.py   👈
```

### 1.5.2 Khai báo DATABASE_URL

```python
# app/database.py
DATABASE_URL = "postgresql://postgres:postgres@localhost:5432/fastapi_db"
```

Format chung:

```
postgresql://<username>:<password>@<host>:<port>/<database_name>
```

---

## 1.6 SQLAlchemy Engine

```python
from sqlalchemy import create_engine

engine = create_engine(
    DATABASE_URL,
    echo=True  # log SQL ra console (dev only)
)
```

Giải thích:

* `engine`: quản lý kết nối DB
* `echo=True`: in câu SQL (giúp debug khi học)

---

## 1.7 SessionLocal – quản lý phiên làm việc DB

```python
from sqlalchemy.orm import sessionmaker

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)
```

Ý nghĩa:

* **Session** = 1 phiên làm việc với DB
* Mỗi request FastAPI sẽ dùng **1 session riêng**
* Tránh chia sẻ session giữa các request

---

## 1.8 Base – nền tảng cho ORM Models

```python
from sqlalchemy.orm import declarative_base

Base = declarative_base()
```

Vai trò của `Base`:

* Là class cha cho tất cả SQLAlchemy models
* Dùng để:

  * Tạo bảng
  * Mapping Python class ↔ DB table

---

## 1.9 Tổng hợp file database.py hoàn chỉnh

```python
# app/database.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

DATABASE_URL = "postgresql://postgres:postgres@localhost:5432/fastapi_db"

engine = create_engine(
    DATABASE_URL,
    echo=True
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

Base = declarative_base()
```

---

## 1.10 Kiểm tra kết nối DB (test nhanh)

Tạo file test đơn giản:

```python
from app.database import engine

try:
    with engine.connect() as conn:
        print("✅ Connected to PostgreSQL successfully")
except Exception as e:
    print("❌ Connection failed", e)
```

Nếu thấy log kết nối thành công → DB đã sẵn sàng

---

## 1.11 Best Practices quan trọng

* Không hard-code password trong production
* Dùng `.env` + `python-dotenv` (sẽ học sau)
* Mỗi request dùng 1 DB session
* Không gọi SQL trực tiếp trong controller
* DB config nằm riêng trong `database.py`

---

✅ Kết thúc Phần 1 – Kết nối cơ sở dữ liệu

➡️ Phần tiếp theo: **Models & Schemas** (SQLAlchemy Model vs Pydantic Schema)
