# Bài tập 3: Chuẩn hoá câu

def normalize_sentence(text: str) -> str:
    # Bỏ khoảng trắng đầu/cuối toàn đoạn
    text = text.strip()

    # Tách câu theo dấu chấm
    raw_sentences = text.split(".")

    normalized_sentences = []

    for sentence in raw_sentences:
        # Bỏ khoảng trắng thừa ở đầu/cuối câu
        sentence = sentence.strip()
        if sentence == "":
            continue  # bỏ câu rỗng (do "..." hoặc "." liên tiếp)

        # Bỏ khoảng trắng thừa giữa các từ
        # split() sẽ tách theo mọi khoảng trắng & tự gom nhiều khoảng trắng còn 1
        words = sentence.split()
        sentence_clean = " ".join(words)

        # Viết hoa chữ cái đầu câu, các chữ còn lại cho về thường
        sentence_clean = sentence_clean.lower()
        sentence_clean = sentence_clean[0].upper() + sentence_clean[1:]

        normalized_sentences.append(sentence_clean)

    # Ghép lại thành đoạn văn, mỗi câu cách nhau 1 khoảng trắng và có 1 dấu chấm
    if not normalized_sentences:
        return ""

    result = ". ".join(normalized_sentences) + "."
    return result


# Test
para = "Hello worlD, this Is python.. "
normalized = normalize_sentence(para)
print("Normalized:", normalized)
