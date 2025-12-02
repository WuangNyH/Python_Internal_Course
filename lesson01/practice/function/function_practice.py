# ===== BTTH7a. Hàm tính tổng từ 1 đến n  =====
def sum_to_n(n: int) -> int:
    s = 0
    for i in range(1, n + 1):
        s += i
    return s

print(sum_to_n(5))


# ===== BTTH7b. Hàm kiểm tra năm nhuận  =====
def is_leap_year(year: int) -> bool:
    return (year % 400 == 0) or (year % 4 == 0 and year % 100 != 0)

print(is_leap_year(2024))
print(is_leap_year(2025))


# ===== BTTH7c. Hàm đếm ký tự  =====
def count_char(string: str, char: str) -> int:
    count = 0
    for c in string:
        if c == char:
            count += 1
    return count

print(f"Số ký tự: {count_char("hello", "l")}")


# ===== BTTH8. Hàm định dạng tên  =====
def format_name(first: str, last: str, middle: str | None = None) -> str:
    if middle is None:
        return f"{first} {last}"
    return f"{first} {middle} {last}"

print(format_name("Nguyen", "An"))
print(format_name("Nguyen", "An", "Van"))
