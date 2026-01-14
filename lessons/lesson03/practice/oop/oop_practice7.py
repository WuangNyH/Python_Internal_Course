# ===== BTTH7 =====
class Product:
    def __init__(self, name: str, price: float, quantity: int):
        self.name = name
        self.price = price
        self.quantity = quantity

    def get_total(self) -> float:
        return self.price * self.quantity

    def is_out_of_stock(self) -> bool:
        return self.quantity == 0

    def __str__(self) -> str:
        total = self.get_total()
        return f"{self.name} – {self.price} usd – SL: {self.quantity} – Tổng: {total:.1f} usd"
