# In-memory CRUD API theo MVC + Service layer

## Yêu cầu:
> 1. Tạo được API CRUD hoàn chỉnh (Create/Read/Update/Delete)
> 2. Tổ chức code theo MVC + Service layer
> 3. Dùng Pydantic đúng chuẩn: tách `Create/Update/Out`
> 4. Áp dụng đúng status code + lỗi `422/400/404/409`

### Domain: Todo API

Pydantic Models (`models/todo.py`)
* Có validate bằng `Field`

Tạo 3 schema:
1. `TodoCreate`
    * `title: str` (bắt buộc, min_length=3)
    * `description: str | None = None`
    * `priority: int` (1–5)
    * `done: bool = False`
2. `TodoUpdate`
    * Tất cả field đều optional (`None`), dùng cho `PATCH`
3. `TodoOut`
    * `id: int`
    * `title: str`
    * `description: str | None`
    * `priority: int`
    * `done: bool`


### Service: In-memory Storage

1. In-memory store (lưu trong RAM) 

* Trong `todo_service.py` tạo:
  * `_todos: list[dict] = []`
  * `_id_counter = 1`

2. Nghiệp vụ trong service layer

* `title` không được trùng (case-insensitive)
  * Nếu trùng => raise `HTTPException(status_code=409, detail="Todo title already exists")`

### Controller: CRUD Endpoints

Tạo router `/todos` với các endpoint sau:

1. Create
    * `POST /todos`
    * Request: `TodoCreate`
    * Response: `TodoOut`
    * Status: `201 Created`
2. Get all + Query params
    * `GET /todos`
    * Query params:
      * `done: bool | None = None` (lọc theo trạng thái)
      * `keyword: str | None = None` (lọc theo title chứa keyword, không phân biệt hoa thường)
      * `limit: int = 10` (1..50)
    * Response: `list[TodoOut]`
3. Get by id
    * `GET /todos/{todo_id}`
    * Nếu không tồn tại => `404 Not Found`
4. Update toàn bộ
    * `PUT /todos/{todo_id}`
    * Request: `TodoCreate` (vì PUT = replace toàn bộ)
    * Response: `TodoOut`
    * Nếu không tồn tại => `404`
5. Update một phần
    * `PATCH /todos/{todo_id}`
    * Request: `TodoUpdate` (vì PUT = replace toàn bộ)
    * Response: `TodoOut`
    * Nếu không tồn tại => `404`
6. Delete
    * `DELETE /todos/{todo_id}`
    * Status: `204 No Content` (không trả body)
    * Nếu không tồn tại => `404`

Lưu ý: Controller mỏng, Service dày:
* Controller chỉ được làm:
  * nhận request model
  * gọi service
  * trả response
  * raise 404 nếu service trả `None` (hoặc service tự raise)
* Không được nhét logic lọc/search/CRUD vào controller