# Bài 2: Thống kê sản phẩm & hóa đơn

# Dữ liệu ban đầu
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

# a. Tạo một dict `product_map` từ `products` để tra cứu nhanh theo `product_id`
product_map = {}

for product_id, name, price in products:
    product_map[product_id] = {
        "name": name,
        "price": price,
    }

print(product_map)


# b. Với mỗi hóa đơn trong `orders`, hãy tính tổng tiền của hóa đơn đó, lưu vào key mới `"total"` trong từng dict hóa đơn
for order in orders:
    total = 0
    for product_id in order["items"]:
        price = product_map[product_id]["price"]
        total += price
    order["total"] = total

print(orders)


# c. In ra danh sách hóa đơn theo format
for order in orders:
    order_id = order["order_id"]
    item_count = len(order["items"])
    total = order["total"]
    print(f"{order_id}: {item_count} san pham, Tong tien = {total}")


# d. Tạo một set `all_products_sold` chứa tất cả `product_id` đã từng được bán trong mọi hóa đơn, sau đó in ra
all_products_sold = set()

for order in orders:
    all_products_sold.update(order["items"])

print("So luong san pham khac nhau da ban:", len(all_products_sold))

