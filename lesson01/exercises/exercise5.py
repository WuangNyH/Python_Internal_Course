"""
Tính lương nhân viên theo thâm niên công tác
* Nếu TNCT < 12 tháng ⇒ hệ số = 1.92
* Nếu 12 ≤ TNCT < 36 tháng ⇒ hệ số = 2.34
* Nếu 36 ≤ TNCT < 60 tháng ⇒ hệ số = 3
* Nếu TNCT ≥ 60 tháng ⇒ hệ số = 4.5
"""

tnct = int(input("Nhập thâm niên công tác: "))

luong_can_ban = 1000000

if tnct < 12:
    he_so = 1.92
elif tnct < 36:
    he_so = 2.34
elif tnct < 60:
    he_so = 3
else:
    he_so = 4.5

print(f"Hệ số lương: {he_so:.2f}")
print(f"Lương của nhân viên: {luong_can_ban * he_so:,.0f} đồng")
