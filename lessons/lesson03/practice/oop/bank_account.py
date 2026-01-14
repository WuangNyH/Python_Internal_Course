class BankAccount:
    def __init__(self, owner, balance=0):
        self.owner = owner
        self._balance = balance  # "private" theo quy ước

    def deposit(self, amount):
        if amount <= 0:
            print("Số tiền nạp phải > 0")
            return
        self._balance += amount

    def withdraw(self, amount):
        if amount > self._balance:
            print("Không đủ số dư")
            return
        self._balance -= amount

    def get_balance(self):
        return self._balance

