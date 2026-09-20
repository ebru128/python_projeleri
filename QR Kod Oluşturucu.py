import qrcode

# 1. QR Kod nesnesini yapılandırın
qr = qrcode.QRCode(
    version=1,  # 1 ile 40 arası (Veri boyutuna göre otomatik büyür, 1 en küçük boyut)
    error_correction=qrcode.constants.ERROR_CORRECT_H,  # %30'a kadar olan çizilme/hasarları tolore eder
    box_size=10,  # Karelerin boyutu (piksel)
    border=4,     # Kenar boşluğu kalınlığı (minimum 4 önerilir)
)

# 2. Veriyi yükleyin
veri = "https://github.com"
qr.add_data(veri)
qr.make(fit=True)

# 3. Görseli oluşturun (Ön renk ve Arka plan rengi belirleyin)
resim = qr.make_image(
    fill_color="darkblue",  # QR çizgi/kare rengi
    back_color="white"      # Arka plan rengi
)

# 4. Dosyayı kaydedin
resim.save("ozel_qr.png")

print("Özelleştirilmiş QR kod oluşturuldu.")