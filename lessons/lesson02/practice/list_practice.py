# ===== BTTH1 =====
scores = [7.5, 8.0, 6.5, 9.0, 8.5]

# Tự duyệt list
total = 0
max_score = scores[0]
min_score = scores[0]

for s in scores:
    total += s
    if s > max_score:
        max_score = s
    if s < min_score:
        min_score = s

avg_score = total / len(scores)

print("Điểm trung bình:", avg_score)
print("Điểm cao nhất:", max_score)
print("Điểm thấp nhất:", min_score)


# Dùng hàm built-in
avg_score = sum(scores) / len(scores)
max_score = max(scores)
min_score = min(scores)

print("Điểm trung bình:", avg_score)
print("Điểm cao nhất:", max_score)
print("Điểm thấp nhất:", min_score)


# ===== BTTH2 =====
numbers = [5, -2, 8, -1, 0, 3, -10]

# Dùng vòng lặp (không sửa list khi đang duyệt)
result = []
for x in numbers:
    if x >= 0:
        result.append(x)

print(result)

# Duyệt copy
for x in numbers[:]:
    if x < 0:
        numbers.remove(x)

print(numbers)

# Dùng list comprehension
filtered = [x for x in numbers if x >= 0]
print(filtered)


# ===== BTTH3 =====
nested = [[1,2,3],[4,5],[6]]

# 2 vòng lặp
flat = []
for sub in nested:
    for x in sub:
        flat.append(x)

print(flat)

# Nested list comprehension
flat = [x for sub in nested for x in sub]
print(flat)

