# Bài tập 1: Kiểm tra và tìm ngày kế tiếp, ngày trước đó

## Đề bài:
> * Nhập vào thông tin 1 ngày (ngày – tháng – năm)
> * Kiểm tra ngày có hợp lệ hay không? 
> * Nếu hợp lệ hãy tìm ra ngày kế tiếp (ngày – tháng – năm) & ngày trước đó (ngày – tháng – năm)

### Hướng dẫn các bước thực hiện

* Bước 1: Nhập vào ngày, tháng, năm từ bàn phím
* Bước 2: Kiểm tra xem ngày, tháng, năm nhập vào có hợp lệ hay không. Cần xác định số ngày tối đa của mỗi tháng (lưu ý tháng 2 trong năm nhuận), và xem xét liệu ngày nhập vào có vượt quá số ngày tối đa đó hay không
* Bước 3: Nếu ngày, tháng, năm hợp lệ, tìm ngày kế tiếp và ngày trước đó
  * Để tìm ngày kế tiếp, có thể tăng ngày lên 1
    * Nếu ngày vượt quá số ngày tối đa của tháng, đặt lại ngày về 1 và tăng tháng lên 1
    * Nếu tháng vượt quá 12, đặt lại tháng về 1 và tăng năm lên 1
  * Để tìm ngày trước đó, có thể giảm ngày đi 1
    * Nếu ngày nhỏ hơn 1, đặt ngày về ngày cuối của tháng trước và giảm tháng đi 1
    * Nếu tháng nhỏ hơn 1, đặt tháng về 12 và giảm năm đi 1
* Bước 4: In ngày kế tiếp và ngày trước đó ra màn hình console

---

# Bài tập 2: Tính tổng S = 1 + 1/3! + 1/5! + ... + 1/(2n−1)!

> **Đề bài:**
> Viết chương trình tính `S = 1 + 1/3! + 1/5! + ... + 1/(2n−1)!`, với n được nhập từ bàn phím

---

# Bài tập 3: Thao tác chuỗi

> **Đề bài:**
> Viết chương trình để chuẩn hoá câu:
>* Bỏ khoảng trắng thừa (giữa các từ chỉ còn 1 khoảng trắng)
>* Viết hoa chữ cái đầu câu
>* Đảm bảo câu kết thúc bằng chính xác một dấu chấm “.”
>  * Nếu thừa nhiều dấu chấm liên tiếp thì rút gọn còn “.”
> 
> Ví dụ: "Hello worlD, this Is python.. " => "Hello world, this is python."
