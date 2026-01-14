# Bài 1: Kiểm tra ngày hợp lệ, tìm ngày kế tiếp và ngày trước đó

day = int(input("Nhập ngày: "))
month = int(input("Nhập tháng: "))
year = int(input("Nhập năm: "))

# Kiểm tra năm nhuận
is_leap = False
if (year % 4 == 0 and year % 100 != 0) or (year % 400 == 0):
    is_leap = True

# Xác định số ngày trong tháng
if month < 1 or month > 12:
    print("Ngày tháng năm không hợp lệ!")
else:
    if month == 2:
        if is_leap:
            max_day = 29
        else:
            max_day = 28
    elif month == 4 or month == 6 or month == 9 or month == 11:
        max_day = 30
    else:
        max_day = 31

    # Kiểm tra ngày hợp lệ
    if day < 1 or day > max_day:
        print("Ngày tháng năm không hợp lệ!")
    else:
        print(f"Ngày hợp lệ: {day}/{month}/{year}")

        # Tính ngày kế tiếp
        next_day = day + 1
        next_month = month
        next_year = year

        if next_day > max_day: # qua tháng mới
            next_day = 1
            next_month += 1

            if next_month > 12: # qua năm mới
                next_month = 1
                next_year += 1

        # Tính ngày trước đó
        prev_day = day - 1
        prev_month = month
        prev_year = year

        if prev_day < 1: # lùi về tháng trước
            prev_month -= 1

            if prev_month < 1: # lùi về năm trước
                prev_month = 12
                prev_year -= 1

            # Xác định số ngày của tháng trước (làm lại như trên)
            if prev_month == 2:
                if (prev_year % 4 == 0 and prev_year % 100 != 0) or (prev_year % 400 == 0):
                    prev_day = 29
                else:
                    prev_day = 28
            elif prev_month == 4 or prev_month == 6 or prev_month == 9 or prev_month == 11:
                prev_day = 30
            else:
                prev_day = 31

        print(f"Ngày kế tiếp: {next_day}/{next_month}/{next_year}")
        print(f"Ngày trước đó: {prev_day}/{prev_month}/{prev_year}")
