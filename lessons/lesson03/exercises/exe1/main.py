from file_utils import read_file_content, count_word_frequency


def print_top_words(freq: dict[str, int], top_n: int = 10) -> None:
    items = sorted(freq.items(), key=lambda item: item[1], reverse=True)

    print(f"Top {top_n} từ xuất hiện nhiều nhất:")
    for word, count in items[:top_n]:
        print(f"- {word}: {count}")


def main():
    filename = input("Nhập tên file cần phân tích: ").strip()

    try:
        content = read_file_content(filename)
    except FileNotFoundError:
        print(f"File '{filename}' không tồn tại.")
        return
    except OSError as e:
        print(f"Không thể đọc file: {e}")
        return

    # Đếm tần suất
    freq = count_word_frequency(content)

    total_words = sum(freq.values())
    print(f"Tổng số từ: {total_words}")

    if total_words == 0:
        print("File không có nội dung hoặc không có từ nào.")
        return

    print_top_words(freq, top_n=10)


if __name__ == "__main__":
    main()
