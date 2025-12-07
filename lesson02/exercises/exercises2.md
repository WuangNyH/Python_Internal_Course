# Bài tập 1: Quản lý học viên & khóa học

## Đề bài:
* Cho sẵn dữ liệu ban đầu:

```python
# Danh sách học viên (list các tuple)
students = [
    ("SV01", "Nguyen Van A", 20),
    ("SV02", "Tran Thi B", 21),
    ("SV03", "Le Van C", 19),
]

# Dict lưu điểm từng môn cho từng sinh viên
scores = {
    "SV01": {"math": 8.0, "python": 7.5},
    "SV02": {"math": 6.5, "python": 8.5},
    "SV03": {"math": 9.0, "python": 9.5},
}

# Set các môn học hiện có
courses = {"math", "python"}
```

* Yêu cầu:
  * a. Dùng vòng lặp + unpacking tuple để in ra danh sách học viên theo format
    ```text
        SV01 - Nguyen Van A (20)
        SV02 - Tran Thi B (21)
        ...
    ```
  * b. Tạo một list mới `python_scores` chỉ chứa tuple `(student_id, name, python_score)`
  * c. Tìm học viên có điểm Python cao nhất từ `python_scores` và in ra: `Top Python: <name> - <score>`
  * d. Thêm môn mới `"database"` vào `courses` (dùng set) và gán tạm điểm `database = 0` cho tất cả sinh viên trong `scores`

---

# Bài tập 2: Thống kê sản phẩm & hóa đơn

## Đề bài:
* Cho sẵn dữ liệu ban đầu:

```python
# Mỗi sản phẩm là 1 tuple (product_id, name, price)
products = [
    (1, "Ban Phim", 250_000),
    (2, "Chuot", 150_000),
    (3, "Man Hinh", 3_000_000),
    (4, "Tai Nghe", 500_000),
]

# Danh sách đơn hàng (list dict)
orders = [
    {"order_id": "HD01", "items": [1, 2, 4]},
    {"order_id": "HD02", "items": [2, 3]},
    {"order_id": "HD03", "items": [1, 4]},
]
```

* Yêu cầu:
  * a. Tạo một dict `product_map` từ `products` để tra cứu nhanh theo `product_id` với dạng:
    ```text
        {
            1: {"name": "Ban Phim", "price": 250_000},
            2: {"name": "Chuot", "price": 150_000},
            ...
        }
    ```
  * b. Với mỗi hóa đơn trong `orders`, hãy tính tổng tiền của hóa đơn đó, lưu vào key mới `"total"` trong từng dict hóa đơn
    * Hints:
      * items là list các product_id
      * tra giá ở product_map (dict)
      * cộng dồn
  * c. In ra danh sách hóa đơn theo format:
    ```text
        HD01: 3 san pham, Tong tien = ...
        HD02: ...
    ```
  * d. Tạo một set `all_products_sold` chứa tất cả `product_id` đã từng được bán trong mọi hóa đơn, sau đó in ra:
    ```text
      So luong san pham khac nhau da ban: <len(all_products_sold)>
    ```

---

# Bài tập 3: Hệ thống tag bài viết & người dùng

## Đề bài:
* Cho sẵn dữ liệu ban đầu:

```python
# Danh sách user: list tuple (user_id, name)
users = [
    ("U01", "Alice"),
    ("U02", "Bob"),
    ("U03", "Charlie"),
]

# Dict bài viết: key là post_id, value là dict thông tin
posts = {
    "P01": {
        "title": "Hoc Python co ban",
        "author_id": "U01",
        "tags": {"python", "beginner"},
    },
    "P02": {
        "title": "Lam viec voi List va Dict",
        "author_id": "U01",
        "tags": {"python", "data-structure"},
    },
    "P03": {
        "title": "Gioi thieu HTML CSS",
        "author_id": "U02",
        "tags": {"web", "frontend"},
    },
}
```

* Yêu cầu:
  * a. Tạo một dict `user_map` từ `users`, map `user_id` sang `name`
    ```text
        Ví dụ:
        {
            "U01": "Alice",
            "U02": "Bob",
            "U03": "Charlie",
        }
    ```
  * b. Dùng vòng lặp duyệt `posts.items()` để in ra:
    ```text
        [P01] Hoc Python co ban - Alice - Tags: python, beginner
        [P02] ...
    ```
    * Hints:
      * lấy `author_id` từ dict `posts`
      * tra tên ở `user_map`
      * `tags` là set, cần chuyển sang list/sorted trước rồi nối thành chuỗi
    * c. Tạo một set `all_tags` chứa toàn bộ tag xuất hiện trong mọi bài viết
      * Hints: duyệt từng `post`, lấy `post["tags"]` (set), dùng `update()` để dồn vào `all_tags`
    * d. Tạo một dict `tag_counter` để đếm số bài viết chứa mỗi tag
      ```text
        Ví dụ:
        {
              "python": 2,
              "beginner": 1,
              "data-structure": 1,
              "web": 1,
              "frontend": 1,
        }
      ```
      * Hints:
        * Khởi tạo `tag_counter = {}`
        * Duyệt từng post, với mỗi tag trong `post["tags"]`:
          * nếu tag chưa có trong dict => gán = 1
          * nếu đã có => tăng lên 1

