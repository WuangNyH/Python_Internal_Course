def say_hello(name: str) -> None:
    print(f"Hello, {name}!")


# Gọi hàm
say_hello("Taro")


# ===== Tham số và giá trị trả về =====
def add(a: int, b: int) -> int:
    return a + b


result = add(1, 2)
print(result)


# ===== Tham số mặc định =====
def power(base: int, exp: int = 2) -> int:
    return base ** exp

print(power(3)) # Mặc định exp=2
print(power(3, 3))


# ===== Tham số có thể nhận None =====
def greet(name: str | None = None) -> None:
    if name is None:
        print("Hello, stranger!")
    else:
        print(f"Hello, {name}!")

greet() # Hello, stranger!
greet("Taro") # Hello, Taro!

# Tham số optional
def repeat_message(msg: str, times: int | None = None) -> None:
    # Nếu không truyền times => mặc định là 1
    if times is None:
        times = 1

    for _ in range(times):
        print(msg)

repeat_message("Hi") # không truyền times => ta đã gán lại thành 1
repeat_message("Hi", 3) # times = 3
repeat_message("Hi", None) # Người gọi cố tình truyền None => ta cũng đã xử lý
