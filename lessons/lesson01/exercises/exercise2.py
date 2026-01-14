# Bài tập 2: Tính tổng S = 1 + 1/3! + 1/5! + ... + 1/(2n−1)!

# Nhập n (đảm bảo n > 0)
while True:
    n = int(input("Nhập n (>0): "))
    if n > 0:
        break
    print("n phải > 0. Nhập lại!")

sum_s = 0.0

# vòng lặp i chạy từ 1 -> n
for i in range(1, n + 1):
    k = 2 * i - 1  # số cần tính giai thừa: 1, 3, 5, ..., (2n−1)

    fact = 1  # tính giai thừa k!
    for j in range(1, k + 1):
        fact *= j

    sum_s += 1.0 / fact

print("Giá trị S =", sum_s)
