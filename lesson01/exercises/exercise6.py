# Bài 6: Xác định số ngày trong một tháng

month = int(input("Nhập tháng (1-12): "))
year = int(input("Nhập năm: "))

# Kiểm tra tính hợp lệ của tháng
if month < 1 or month > 12:
    print("Tháng không hợp lệ!")
else:
    # Nếu tháng có 30 ngày
    if month in (4, 6, 9, 11):
        days = 30

    # Nếu tháng là tháng 2 → kiểm tra năm nhuận
    elif month == 2:
        # Kiểm tra năm nhuận
        if (year % 4 == 0 and year % 100 != 0) or (year % 400 == 0):
            days = 29
        else:
            days = 28

    # Các tháng còn lại có 31 ngày
    else:
        days = 31

    print(f"Tháng {month} năm {year} có {days} ngày.")
