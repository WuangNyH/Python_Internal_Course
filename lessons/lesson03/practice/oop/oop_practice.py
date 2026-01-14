# ===== BTTH7 =====
from lessons.lesson03.practice.oop.oop_practice9 import Community
from lessons.lesson03.practice.oop.person import Person

# Tạo danh sách sản phẩm
# products = [
#     Product("Sữa tươi", 25.5, 10),
#     Product("Bánh mì", 12.0, 0),
#     Product("Cà phê", 18.5, 5),
# ]
#
# # In danh sách
# for p in products:
#     print(p)
#
# # Tính tổng giá trị toàn bộ kho
# def calc_inventory_value(products: list[Product]) -> float:
#     if not products:
#         return 0.0
#     total = 0.0
#     for p in products:
#         total += p.get_total()
#     return total
#
# inventory_value = calc_inventory_value(products)
# print("Tổng giá trị kho:", inventory_value, "usd")
#
#
# # Tìm sản phẩm có total value cao nhất
# def find_top_product(products: list[Product]) -> Product | None:
#     if not products:
#         return None
#
#     top = products[0]
#     for p in products[1:]:
#         if p.get_total() > top.get_total():
#             top = p
#     return top
#
# best_product = find_top_product(products)
# if best_product is None:
#     print("Không có sản phẩm nào trong kho")
# else:
#     print("Sản phẩm giá trị cao nhất:")
#     print(best_product)



# ===== BTTH8 =====
# e = Employee("An", 1000)
# print(e)
# print("Total income:", e.total_income())
#
# e.salary = 2000
# e.bonus_rate = 0.2
# print(e)
# print("Total income:", e.total_income())

# validate
# try:
#     e.salary = -10
# except ValueError as err:
#     print("Lỗi set salary:", err)
#
# try:
#     e.bonus_rate = 1.5
# except ValueError as err:
#     print("Lỗi set bonus_rate:", err)



# ===== BTTH9 =====
p1 = Person("An", 20, 1000)
p2 = Person("Binh", 30, 2500)
p3 = Person("Chi", 20, 1800)

comm = Community(p1, p2, p3)
print(comm)
print()

print("Tìm name='An':")
print(comm.find(name="An"))
print()

print("Tìm age=20:")
print(comm.find(age=20))
print()

print("Tìm income=2500:")
print(comm.find(income=2500))
print()

print("Tìm name='An', age=20:")
print(comm.find(name="An", age=20))
