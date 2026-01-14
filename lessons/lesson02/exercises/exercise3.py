# Bài 3: Hệ thống tag bài viết & người dùng

# Dữ liệu ban đầu
# Danh sách user: list tuple (user_id, name)
users = [
    ("U01", "Alice"),
    ("U02", "Bob"),
    ("U03", "Charlie"),
]

# Dict bài viết: key là post_id, value là dict thông tin
posts = {
    "P01": {
        "title": "Hoc Python co ban",
        "author_id": "U01",
        "tags": {"python", "beginner"},
    },
    "P02": {
        "title": "Lam viec voi List va Dict",
        "author_id": "U01",
        "tags": {"python", "data-structure"},
    },
    "P03": {
        "title": "Gioi thieu HTML CSS",
        "author_id": "U02",
        "tags": {"web", "frontend"},
    },
}


# a. Tạo một dict `user_map` từ `users`, map `user_id` sang `name`
user_map = {}

for user_id, name in users:
    user_map[user_id] = name

print(user_map)


# b. Dùng vòng lặp duyệt posts.items() để in ra
for post_id, info in posts.items():
    title = info["title"]
    author_id = info["author_id"]
    tags = info["tags"]

    author_name = user_map.get(author_id, "Unknown")

    sorted_tags = sorted(tags)
    tags_str = ", ".join(sorted_tags)

    print(f"[{post_id}] {title} - {author_name} - Tags: {tags_str}")


# c. Tạo một set `all_tags` chứa toàn bộ tag xuất hiện trong mọi bài viết
all_tags = set()

for info in posts.values():
    all_tags.update(info["tags"])

print(all_tags)


# d. Tạo một dict `tag_counter` để đếm số bài viết chứa mỗi tag
tag_counter = {}

for info in posts.values():
    for tag in info["tags"]:
        if tag in tag_counter:
            tag_counter[tag] += 1
        else:
            tag_counter[tag] = 1

print(tag_counter)
