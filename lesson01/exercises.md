# Bài tập 1: Chuyển số thành chữ tiếng Anh

> **Yêu cầu:**
> Viết chương trình nhập vào một số tự nhiên từ **1 đến 10**, sau đó in ra **tên tiếng Anh** tương ứng của số đó

### Hướng dẫn các bước thực hiện

#### Cách 1: Sử dụng if-else

* Bước 1: Nhập số từ bàn phím
* Bước 2: Dùng cấu trúc if-else để so sánh số vừa nhập với các số từ 1 đến 10
  * Mỗi số tương ứng với một tên tiếng Anh cụ thể
* Bước 3: In ra màn hình tên tiếng Anh của số đã nhập

#### Cách 2: Sử dụng switch-case

* Bước 1: Nhập số từ bàn phím
* Bước 2: Dùng cấu trúc switch-case với số đã nhập làm biểu thức điều kiện
    * Mỗi case sẽ ứng với một số từ 1 đến 10 và in ra tên tiếng Anh tương ứng
* Bước 3: In ra màn hình tên tiếng Anh của số đã nhập

---

# Bài tập 2: Đảo giá trị của hai biến

> **Yêu cầu:**
> Nhập vào 2 số nguyên và lưu vào hai biến `a` và `b`. Sau đó, hãy đảo giá trị của hai biến này rồi in kết quả ra màn hình console

Thực hiện bài tập bằng **2 cách**:

1. **Cách 1:** Sử dụng biến tạm
2. **Cách 2:** Không dùng biến tạm

### Hướng dẫn các bước thực hiện

#### Cách 1: Sử dụng biến tạm

* Bước 1: Nhập hai số nguyên từ bàn phím và gán cho biến a và b
* Bước 2: Tạo một biến tạm (temp) và gán giá trị của a cho temp
* Bước 3: Gán giá trị của b cho a
* Bước 4: Gán giá trị của temp (tức giá trị ban đầu của a) cho b
* Bước 5: In ra màn hình giá trị mới của a và b

#### Cách 2: Không sử dụng biến tạm

* Bước 1: Nhập hai số nguyên từ bàn phím và gán cho biến a và b
* Bước 2: Sử dụng cách cộng giá trị của a và b, rồi gán tổng đó cho a
* Bước 3: Lấy giá trị mới của a trừ đi b để ra giá trị ban đầu của a, sau đó gán cho b
* Bước 4: Lấy giá trị mới của a trừ đi giá trị mới của b (tức giá trị ban đầu của b) và gán cho a
* Bước 5: In ra màn hình giá trị mới của a và b sau khi đổi chỗ

---

# Bài tập 3: Giải phương trình bậc nhất

> **Yêu cầu:**
> Giải phương trình bậc nhất có dạng: ax + b = 0

### Hướng dẫn các bước thực hiện

* Bước 1: Nhập vào hai hệ số a và b của phương trình từ bàn phím
* Bước 2: Kiểm tra xem hệ số a có bằng 0 hay không
    * Nếu a = 0, tiếp tục kiểm tra hệ số b:
        * Nếu b = 0: phương trình có vô số nghiệm
        * Nếu b ≠ 0: phương trình vô nghiệm
    * Nếu a ≠ 0: chuyển sang bước tiếp theo
* Bước 3: Khi a ≠ 0, tính nghiệm của phương trình theo công thức: x = -b/a
* Bước 4: In ra màn hình console nghiệm của phương trình hoặc thông báo phương trình vô nghiệm/vô số nghiệm tùy vào trường hợp

---

# Bài tập 4: Giải phương trình bậc hai

> **Yêu cầu:**
> Giải phương trình bậc hai có dạng: ax2 + bx + c = 0

### Hướng dẫn các bước thực hiện

* Bước 1: Nhập vào ba hệ số a, b, c của phương trình từ bàn phím
* Bước 2: Kiểm tra hệ số a
    * Nếu a = 0, phương trình trở thành phương trình bậc một. Khi đó áp dụng cách giải phương trình bậc một
    * Nếu a ≠ 0, tiếp tục bước 3
* Bước 3: Khi a ≠ 0, tính giá trị delta (Δ) theo công thức: Δ=b2−4ac
* Bước 4: Dựa vào giá trị của delta để kết luận nghiệm của phương trình:
  * Nếu Δ < 0, phương trình vô nghiệm
  * Nếu Δ = 0, phương trình có một nghiệm kép: x = -b/2a
  * Nếu Δ > 0, phương trình có hai nghiệm phân biệt x1, x2 (tra công thức nghiệm phương trình bậc 2)
* Bước 5: In ra màn hình console nghiệm của phương trình hoặc thông báo vô nghiệm, tùy theo từng trường hợp

---

# Bài tập 5: Tính lương nhân viên theo thâm niên công tác

> **Yêu cầu:**
> Viết chương trình tính lương của nhân viên dựa trên thâm niên công tác (TNCT) theo quy định sau:
> * Công thức tính lương: `Lương = hệ số × lương căn bản`
> * Trong đó lương căn bản = 650000

**Quy định hệ số theo TNCT (tính theo tháng)**:
* Nếu TNCT < 12 tháng ⇒ hệ số = 1.92
* Nếu 12 ≤ TNCT < 36 tháng ⇒ hệ số = 2.34
* Nếu 36 ≤ TNCT < 60 tháng ⇒ hệ số = 3
* Nếu TNCT ≥ 60 tháng ⇒ hệ số = 4.5

### Hướng dẫn các bước thực hiện

* Bước 1: Nhập vào thâm niên công tác (TNCT) của nhân viên từ bàn phím (tính theo tháng)
* Bước 2: Đặt lương căn bản bằng 650000
* Bước 3: Dựa vào TNCT, xác định hệ số lương:
  * Nếu TNCT < 12 tháng → hệ số = 1.92
  * Nếu 12 ≤ TNCT < 36 tháng → hệ số = 2.34
  * Nếu 36 ≤ TNCT < 60 tháng → hệ số = 3
  * Nếu TNCT ≥ 60 tháng → hệ số = 4.5
* Bước 4: Tính lương nhân viên theo công thức: `Lương = hệ số × lương căn bản`
* Bước 5: In ra màn hình console mức lương của nhân viên

--- 

# Bài tập 6: Xác định số ngày trong một tháng

> **Yêu cầu:**
> Nhập vào tháng và năm. Hãy cho biết tháng đó trong năm đó có bao nhiêu ngày

### Hướng dẫn các bước thực hiện

* Bước 1: Nhập vào tháng và năm từ bàn phím
* Bước 2: Dựa vào tháng, xác định số ngày:
  * Nếu tháng là 4, 6, 9 hoặc 11, số ngày = 30
  * Nếu tháng là 2, cần kiểm tra xem năm đó có phải là năm nhuận hay không:
    * Nếu là năm nhuận, số ngày = 29
    * Nếu không phải năm nhuận, số ngày = 28
  * Các tháng còn lại sẽ có 31 ngày
* Bước 3: In ra màn hình console số ngày tương ứng của tháng đã nhập

> **Lưu ý**: Để kiểm tra một năm có phải là năm nhuận hay không, áp dụng quy tắc:
> * Năm nhuận là năm chia hết cho 4 nhưng không chia hết cho 100,
  hoặc năm chia hết cho 400

---

# Bài tập 7: Đổi chữ hoa thành chữ thường và ngược lại

> **Yêu cầu:**
> Nhập vào một ký tự và đảm bảo rằng ký tự đó là chữ cái
> * Nếu không phải chữ cái, hãy thông báo nhập sai
> * Nếu là chữ cái, kiểm tra xem đó là chữ thường hay chữ hoa:
>   * Nếu là chữ thường, chuyển thành chữ hoa
>   * Nếu là chữ hoa, chuyển thành chữ thường

**Gợi ý**:
* Mã ASCII của chữ cái thường và chữ cái hoa khác nhau 32 đơn vị
* Ví dụ: `a` có mã 97, `A` có mã 65

### Hướng dẫn các bước thực hiện

* Bước 1: Nhập vào một ký tự từ bàn phím
* Bước 2: Kiểm tra xem ký tự được nhập có phải là chữ cái hay không
  * Nếu không phải chữ cái, in ra thông báo: "Bạn đã nhập sai"
* Bước 3: Nếu là chữ cái, xác định ký tự đó là chữ hoa hay chữ thường:
  * Nếu là chữ thường (mã ASCII từ 97 đến 122), chuyển sang chữ hoa bằng cách trừ 32 (vì chữ thường và chữ hoa cách nhau 32 đơn vị trên bảng mã ASCII)
  * Nếu là chữ hoa (mã ASCII từ 65 đến 90), chuyển sang chữ thường bằng cách cộng 32
* Bước 4: In ra màn hình console ký tự sau khi đã chuyển đổi

---

# Bài tập 8: Kiểm tra số chính phương

## Đề bài:
> Kiểm tra 1 số nguyên dương x có phải là số chính phương hay không?
> * Định nghĩa số chính phương: Là số mà kết quả khai căn bậc 2 của nó là 1 số nguyên. vd: 0, 1, 4, 9, 16, 25, 36 ...

### Hướng dẫn các bước thực hiện

* Bước 1: Nhập một số nguyên dương x từ bàn phím
* Bước 2: Tính căn bậc hai của x bằng Math.sqrt(x) và lưu kết quả vào biến squareRoot
* Bước 3: Kiểm tra nếu squareRoot là số nguyên (có phần thập phân bằng 0, tức squareRoot % 1 == 0), thì x là số chính phương. Ngược lại, x không phải là số chính phương
* Bước 4: In ra thông báo tương ứng với kết quả kiểm tra ở Bước 3

---

# Bài tập 9: Kiểm tra và tìm ngày kế tiếp, ngày trước đó

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