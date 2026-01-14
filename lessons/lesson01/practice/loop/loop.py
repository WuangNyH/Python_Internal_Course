# ===== for với range =====
for i in range(5): # 0, 1, 2, 3, 4
    print(i, end=" ") # end mặc định "\n"

print() # xuống dòng sau khi in

for i in range(1, 6): # 1, 2, 3, 4, 5
    print(i, end=" ")

print()


# ===== for-each duyệt list và string =====
names = ["Doraemon", "Nobita", "Shizuka"]
for name in names:
    print(name, end=" ")
print()

string = "hello"
for character in string:
    print(character)


# ===== break & continue =====
# break
for i in range(1, 11):
    if i == 5:
        break
    print(i, end=" ")
print()

# continue
for i in range(1, 11):
    if i % 2 == 0:
        continue
    print(i, end=" ")
print()


# ===== while =====
n = 5
while n > 0:
    print(n, end="\t")
    n -= 1
print()

# while True
while True:
    pwd = input("Nhập mật khẩu: ")
    if pwd == "123@techzen":
        print("Ping pong!")
        break
    print("Sai rồi! Chịu khó nhập lại đi em iu")


# ===== Nested Loop =====
for i in range(3): # i = 0,1,2
    for j in range(2): # j = 0,1
        print(f"Vòng {i}: {j}")


"""
In hình sau:
* * * * * *
* * * * * *
* * * * * *
* * * * * *
* * * * * *
"""
row, col = 5, 6
for i in range(row):
    for j in range(col):
        print("*", end=" ")
    print()

