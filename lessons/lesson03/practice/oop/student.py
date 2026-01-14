# ===== hàm khởi tạo __init__ =====

class Student:
    def __init__(self, name, age, score):
        self.name = name # thuộc tính (attribute) của object
        self.age = age
        self.score = score

    # Phương thức
    def is_passed(self):
        return self.score >= 5.0

    def introduce(self):
        print(f"Hi, mình là {self.name}, {self.age} tuổi")

