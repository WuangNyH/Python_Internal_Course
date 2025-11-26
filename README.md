# Python Internal Course — Techzen Training Program

**Python Core · OOP · FastAPI · Project-Based Learning**

Khoá học Python nội bộ dành cho fresher Techzen, tập trung vào thực hành và tư duy lập trình thực chiến để ứng viên có thể tham gia dự án thực tế sau khi hoàn thành khóa học

---

## Mục tiêu khóa học

Sau khóa học, học viên có thể:

- Hiểu và sử dụng thành thạo Python Core
- Áp dụng tư duy Lập trình Hướng Đối Tượng (OOP) trong bài toán thực tế
- Xây dựng API backend với **FastAPI**
- Tự tin tham gia các dự án Python tại Techzen

---

## Nội dung khóa học

| Module                           | Nội dung chính                                                                                                                                          |
|----------------------------------|---------------------------------------------------------------------------------------------------------------------------------------------------------|
| **Module 1 — Python Core**       | biến, kiểu dữ liệu, toán tử, cấu trúc điều kiện, vòng lặp, hàm, list/tuple/dict/set, file I/O, exception                                                |
| **Module 2 — Python OOP**        | class, object, thuộc tính – phương thức, kế thừa, đa hình, trừu tượng, interface, static/class method, magic methods                                    |
| **Module 3 — FastAPI Framework** | dependency injection, routing, DTO/schema Pydantic, CRUD, kết nối database bằng SQLAlchemy, Migration, Authentication                                   |
| **Module 4 — Techzen Project**   | Xây dựng tính năng thực tế để tích hợp vào Techzen product (dùng FastAPI) hoàn chỉnh theo mô hình 3 lớp: `controller → service → repository → database` |

---

## Cấu trúc thư mục dự kiến

```bash
python-internal-course/
│
├── module_01_python_core/
├── module_02_oop/
├── module_03_fastapi/
│   ├── app/
│   │   ├── controllers/
│   │   ├── services/
│   │   ├── repositories/
│   │   ├── models/
│   │   ├── schemas/
│   │   └── database.py
│   ├── requirements.txt
│   └── README.md
│
├── final_project/
│
└── README.md
