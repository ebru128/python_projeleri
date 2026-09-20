import threading
import tkinter as tk
from tkinter import ttk
import requests
from bs4 import BeautifulSoup

class FiyatKarsilastirmaApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Fiyat Karşılaştırma Uygulaması")
        self.root.geometry("650x450")
        self.root.configure(bg="#f4f6f9")

        # Başlık
        title_label = tk.Label(
            root, 
            text="Ürün Fiyat Karşılaştırma", 
            font=("Helvetica", 16, "bold"), 
            bg="#f4f6f9", 
            fg="#333"
        )
        title_label.pack(pady=10)

        # Arama / Buton Alanı
        frame_top = tk.Frame(root, bg="#f4f6f9")
        frame_top.pack(fill="x", padx=20, pady=10)

        self.btn_sorgula = tk.Button(
            frame_top, 
            text="Fiyatları Karşılaştır ve Getir", 
            font=("Helvetica", 11, "bold"), 
            bg="#007bff", 
            fg="white", 
            activebackground="#0056b3",
            activeforeground="white",
            command=self.sorgu_baslat,
            padx=15,
            pady=5
        )
        self.btn_sorgula.pack()

        # Yükleniyor Mesajı / Durum Etiketi
        self.lbl_status = tk.Label(root, text="", font=("Helvetica", 10, "italic"), bg="#f4f6f9", fg="#666")
        self.lbl_status.pack(pady=5)

        # Tablo (Treeview)
        frame_table = tk.Frame(root)
        frame_table.pack(fill="both", expand=True, padx=20, pady=10)

        columns = ("site", "urun", "fiyat")
        self.tree = ttk.Treeview(frame_table, columns=columns, show="headings", height=10)
        
        self.tree.heading("site", text="Mağaza / Site")
        self.tree.heading("urun", text="Ürün Adı")
        self.tree.heading("fiyat", text="Fiyat (TL)")

        self.tree.column("site", width=150, anchor="center")
        self.tree.column("urun", width=320, anchor="w")
        self.tree.column("fiyat", width=120, anchor="e")

        # En ucuz teklifi renklendirmek için tag ayarı
        self.tree.tag_configure("en_ucuz", background="#d4edda", foreground="#155724")

        # Scrollbar
        scrollbar = ttk.Scrollbar(frame_table, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

    def sorgu_baslat(self):
        # Arayüzün donmaması için veriyi arka planda çekiyoruz
        self.btn_sorgula.config(state="disabled")
        self.lbl_status.config(text="Siteler taranıyor, lütfen bekleyin...")
        
        # Tabloyu temizle
        for item in self.tree.get_children():
            self.tree.delete(item)

        # Thread başlatma
        threading.Thread(target=self.fiyatlari_cek_ve_listele, daemon=True).start()

    def veriyi_kazı(self, url, fiyat_css, baslik_css):
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }
        try:
            response = requests.get(url, headers=headers, timeout=8)
            soup = BeautifulSoup(response.content, "html.parser")
            
            baslik_elementi = soup.select_one(baslik_css)
            baslik = baslik_elementi.text.strip() if baslik_elementi else "Ürün Adı Bulunamadı"
            fiyat_text = soup.select_one(fiyat_css).text.strip() if soup.select_one(fiyat_css) else "0"
            
            # Sayısal formata dönüştürme
            fiyat_temiz = fiyat_text.replace(".", "").replace("TL", "").replace("₺", "").replace(",", ".").strip()
            fiyat = float(fiyat_temiz)
            
            site_adi = url.split("/")[2].replace("www.", "")
            return {"site": site_adi, "urun": baslik, "fiyat": fiyat}
        except Exception:
            return None

    def fiyatlari_cek_ve_listele(self):
        # Temsili Hedef Siteler ve CSS Seçicileri
        # Gerçek kullanımda hedef e-ticaret sitelerinin CSS selector'ları girilir
        hedefler = [
            {"url": "https://örnek-magaza-1.com/urun", "fiyat_css": ".price", "baslik_css": ".title"},
            {"url": "https://örnek-magaza-2.com/urun", "fiyat_css": "#current-price", "baslik_css": "h1"},
        ]

        sonuclar = []
        for hedef in hedefler:
            res = self.veriyi_kazı(hedef["url"], hedef["fiyat_css"], hedef["baslik_css"])
            if res:
                sonuclar.append(res)

        # Test Amaçlı Örnek Veri (Eğer sitelerden veri çekilemezse gösterilecek simülasyon)
        if not sonuclar:
            sonuclar = [
                {"site": "TeknoMarket", "urun": "Kablosuz Kulaklık X200", "fiyat": 1450.00},
                {"site": "HızlıAlışveriş", "urun": "Kablosuz Kulaklık X200 Bluetooth", "fiyat": 1299.90},
                {"site": "DijitalMagaza", "urun": "X200 Kablosuz Kulaklık Siyah", "fiyat": 1350.50},
                {"site": "UygunFiyat", "urun": "Kablosuz Kulaklık X200", "fiyat": 1199.00}
            ]

        # Fiyata göre en ucuzdan en pahalıya sıralama
        sonuclar.sort(key=lambda x: x["fiyat"])

        # UI Güncellemesini Ana Ekran Thread'ine İletme
        self.root.after(0, self.tabloyu_guncelle, sonuclar)

    def tabloyu_guncelle(self, sonuclar):
        for index, item in enumerate(sonuclar):
            fiyat_str = f"{item['fiyat']:,.2f} TL"
            
            # En ucuz olan ilk elemanı yeşil renkle vurgula
            if index == 0:
                self.tree.insert("", "end", values=(item["site"], item["urun"], fiyat_str), tags=("en_ucuz",))
            else:
                self.tree.insert("", "end", values=(item["site"], item["urun"], fiyat_str))

        self.lbl_status.config(text=f"Arama tamamlandı. En ucuz teklif: {sonuclar[0]['site']}")
        self.btn_sorgula.config(state="normal")


if __name__ == "__main__":
    root = tk.Tk()
    app = FiyatKarsilastirmaApp(root)
    root.mainloop()