# Todo API (DB version)

## Yêu cầu:
> 1. Chuyển Todo API từ in-memory sang PostgreSQL (persist data)
> 2. Áp dụng kiến trúc chuẩn: Router => Service => Repository => DB
> 3. Dùng Alembic Migration để quản lý schema DB
> 4. Dùng Pydantic đúng chuẩn: Create / Update / Out
> 5. Chuẩn hoá response + trace_id + logging màu

---

### 1) Chuẩn bị Database

#### 1.1 Docker compose (bắt buộc)

* Tạo `docker-compose.yml` chạy Postgres
* DB name: `techzen_academy` (hoặc `todo_db` đều được, miễn thống nhất trong `.env`)

#### 1.2 `.env`

* Khai báo `DATABASE_URL`, `TZ`, `DB_POOL_SIZE`, `DB_MAX_OVERFLOW`
* Lưu ý password có ký tự đặc biệt thì encode đúng

=> Yêu cầu: chạy được Postgres + connect OK

---

### 2) Tạo model SQLAlchemy cho Todo

#### 2.1 Model `Todo`

* Tạo `docker-compose.yml` chạy Postgres
* DB name: `techzen_academy` (hoặc `todo_db` đều được, miễn thống nhất trong `.env`)

#### 1.2 `.env`

Tạo file `models/todo.py` theo chuẩn SQLAlchemy (thể dùng `Column` hoặc `Mapped/mapped_column`, miễn consistent)

Các trường cần thiết:
* `id`: int, PK
* `title`: string(200), unique, not null
* `description`: text hoặc string, nullable
* `priority`: int, not null
* `done`: bool, not null, default false
* `created_at`, `updated_at` (dùng `TimeMixin`)

=> Yêu cầu: model có constraint unique(title) và có timestamp

---

### 3) Alembic migration

#### 3.1 Init alembic

* `alembic init alembic`

#### 3.2 Cấu hình `alembic/env.py`

* `target_metadata = Base.metadata`
* import models để autogenerate thấy table
* `compare_type=True`

#### 3.2 Cấu hình `alembic/env.py`

* `alembic revision --autogenerate -m "create todos table"`
* `alembic upgrade head`

=> Yêu cầu: 
* Có bảng `alembic_version`
* Có bảng `todos` trong DB

---

### 4) Schema Pydantic cho Todo (request/response)

Giữ đúng yêu cầu bài tập về nhà Buổi 4 nhưng tách folder:
* `schemas/request/todo_schema.py`: `TodoCreate`, `TodoUpdate`
* `schemas/response/todo_out_schema.py`: `TodoOut`

Yêu cầu validate (giống BTVN Buổi 4):
* `title`: min_length=3
* `priority`: 1..5
* `done`: default false
* `TodoUpdate`: tất cả optional

=> Yêu cầu: Router khai báo `response_model` đúng loại schema

---

### 5) Repository layer

Tạo `repositories/todo_repository.py` kế thừa `BaseRepository[Todo]`

Bắt buộc có:
1. `get_by_title(db, title: str) -> Todo | None` (case-insensitive)
2. `search(db, *, done: bool|None, keyword: str|None, offset: int, limit: int) -> list[Todo]`

Gợi ý search:
* `keyword` tìm theo `title` (ILIKE %keyword%)
* `done` lọc theo trạng thái
* phân trang bằng `offset`/`limit`

=> Yêu cầu: repo không raise HTTPException, không commit/rollback

---

### 6) Service layer (rules nghiệp vụ)

Tạo `services/todo_service.py`, bắt buộc rule:

1. `title` không trùng (case-insensitive) => nếu trùng: `409`
2. Validate nghiệp vụ (ngoài validate schema), ví dụ:
* không cho `priority` ngoài 1..5 (nếu muốn double-check)

Các hàm bắt buộc:
* `create_todo(db, data: TodoCreate) -> Todo`
* `get_todo(db, todo_id: int) -> Todo` (không có => `404`)
* `list_todos(db, done, keyword, offset, limit) -> list[Todo]`
* `update_todo_put(db, todo_id, data: TodoCreate) -> Todo`
* `update_todo_patch(db, todo_id, data: TodoUpdate) -> Todo`
* `delete_todo(db, todo_id) -> None`
 
=> Yêu cầu: service dày, router mỏng

---

### 7) Router endpoints (giữ giống BTVN Buổi 4 nhưng chạy DB)

Tạo router `/todos` với các API:

1. `POST /todos` => `201`
2. `GET /todos` => có query: `done`, `keyword`, `offset`, `limit`
3. `GET /todos/{todo_id}` => `404` nếu không tồn tại
4. `PUT /todos/{todo_id}` (replace toàn bộ)
5. `PATCH /todos/{todo_id}` (update một phần, dùng `exclude_unset=True`)
6. `DELETE /todos/{todo_id}` => `204`

Bắt buộc:
* Khai báo `responses={...}` cho `400`/`404`/`409` (tối thiểu các lỗi có raise)
* Route tĩnh như `/search` (nếu tách endpoint search riêng) phải đặt trước route `/{todo_id:int}` để tránh bị FastAPI hiểu nhầm path
 
=> Yêu cầu: test được bằng Swagger `/docs`

---

### Seeding dữ liệu (bắt buộc)

Tạo `scripts/seed_todo_data.py`:

* Insert 5 todos mẫu nếu DB đang rỗng
* Chạy bằng `python -m scripts.seed_todo_data`
 
=> Yêu cầu: sau seed, `GET /todos` trả ra danh sách

---


### 7) Phần nâng cao (ko bắt buộc)

1. Response wrapper:
   * `SuccessResponse[T]` có `trace_id`, `message`
   * `POST /todos` set header `location: /todos/{id}`
2. TraceIdMiddleware + logging màu:
   * `X-Trace-Id` luôn được trả về response header
   * Log format có `[trace_id=...]`
3. Health check DB:
   * `GET /health/db` chạy `SELECT 1`
