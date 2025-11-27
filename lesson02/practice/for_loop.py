"""
for: thường được sử dụng khi biết số lần lặp

Thực hành: In dãy số 1, 2, 3, ... n (n là số nhập từ bàn phím)
"""

n = 5

# Cú pháp for biến_lặp in range(bắt_đầu, kết_thúc, bước_lặp):
for i in range(0, n, 1):
    print(i + 1)

"""
Vòng lặp for chạy như thế nào???

Trong Python, hàm range(start, stop, step):

- start: giá trị bắt đầu (chạy 1 lần duy nhất khi vào vòng lặp)
- stop: điều kiện dừng (chạy cho đến khi i < stop)
- step: bước tăng

Khi còn thỏa điều kiện i < stop:
    - Chạy body của vòng lặp
    - Tăng i lên step đơn vị và kiểm tra lại
"""

# Mô phỏng for
"""
i = 0 | 0 < 5 => True  | print(1)
i = 1 | 1 < 5 => True  | print(2)
i = 2 | 2 < 5 => True  | print(3)
i = 3 | 3 < 5 => True  | print(4)
i = 4 | 4 < 5 => True  | print(5)
i = 5 | 5 < 5 => False => thoát khỏi vòng lặp
"""

# Nếu giá trị khởi tạo là 1 thì sao???
# Java: for (int i = 1; i <= n; i++)
# Python:
for i in range(1, n + 1):
    print(i)

# In ra n lần từ "hello"
for i in range(1, n + 1):
    print("hello")
