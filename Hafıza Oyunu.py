import tkinter as tk
from tkinter import messagebox
import random
import winsound  # Windows dahili ses sistemi

class RenkliHafizaOyunu:
    def __init__(self, root):
        self.root = root
        self.root.title("Renkli Hayvanlar - Hafıza Oyunu")
        self.root.geometry("480x630")
        self.root.configure(bg="#2c3e50")
        self.root.resizable(False, False)

        # Hayvanlar ve Her Biri İçin Özel Renkler
        self.hayvan_renkleri = {
            '🐶': '#ffbe76',
            '🐱': '#ff7979',
            '🐭': '#dff9fb',
            '🐹': '#f6e58d',
            '🐰': '#badc58',
            '🦊': '#e056fd',
            '🐻': '#c7acee',
            '🐼': '#7ed6df'
        }

        # 8 Çift (16 Kart)
        self.semboller = list(self.hayvan_renkleri.keys()) * 2
        random.shuffle(self.semboller)

        # Oyun Değişkenleri
        self.butonlar = []
        self.secilenler = []
        self.hamle_sayisi = 0
        self.eslesen_ciftler = 0
        self.kalan_hak = 3      # Maksimum 3 Hata Hakkı
        self.gecan_sure = 0
        self.sure_calisiyor = False
        self.en_iyi_sure = None

        # Başlık
        title_label = tk.Label(
            root, 
            text="🌈 RENKLİ HAYVANLAR 🎨", 
            font=("Segoe UI", 16, "bold"), 
            bg="#2c3e50", 
            fg="#f1c40f", 
            pady=8
        )
        title_label.pack()

        # Skor ve Hak Paneli
        self.skor_label = tk.Label(
            root, 
            text="Hamle: 0 | Eşleşme: 0/8 | Süre: 0s", 
            font=("Segoe UI", 11, "bold"), 
            bg="#34495e", 
            fg="#ecf0f1", 
            padx=12, 
            pady=6
        )
        self.skor_label.pack()

        # Can / Hak Göstergesi
        self.hak_label = tk.Label(
            root,
            text="Kalan Hak: ❤️ ❤️ ❤️",
            font=("Segoe UI", 12, "bold"),
            bg="#2c3e50",
            fg="#e74c3c",
            pady=5
        )
        self.hak_label.pack()

        # Rekor Paneli
        self.rekor_label = tk.Label(
            root,
            text="En İyi Süre: -",
            font=("Segoe UI", 9, "italic"),
            bg="#2c3e50",
            fg="#bdc3c7"
        )
        self.rekor_label.pack()

        # Kart Alanı
        self.grid_frame = tk.Frame(root, bg="#2c3e50")
        self.grid_frame.pack(padx=10, pady=10)

        # 4x4 Izgara
        for i in range(16):
            btn = tk.Button(
                self.grid_frame,
                text="🐾",
                font=("Segoe UI", 22, "bold"),
                width=4,
                height=2,
                bg="#341f97",
                fg="#f1c40f",
                activebackground="#54a0ff",
                relief="flat",
                cursor="hand2",
                command=lambda idx=i: self.kart_tikla(idx)
            )
            row = i // 4
            col = i % 4
            btn.grid(row=row, column=col, padx=6, pady=6)
            self.butonlar.append(btn)

        # Yeniden Başlat Butonu
        reset_btn = tk.Button(
            root, 
            text="🔄 Yeniden Başlat", 
            font=("Segoe UI", 11, "bold"), 
            bg="#10ac84", 
            fg="white", 
            activebackground="#1dd1a1",
            activeforeground="white",
            relief="flat",
            cursor="hand2",
            padx=10,
            pady=5,
            command=self.oyunu_sifirla
        )
        reset_btn.pack(pady=8)

    # Ses Efektleri (Windows Beep)
    def ses_tiklama(self):
        winsound.Beep(800, 80)  # Yüksek Frekans Kısa Ses

    def ses_basarili(self):
        winsound.Beep(1200, 120)

    def ses_hata(self):
        winsound.Beep(300, 200)  # Koyu Ton Yanlış Ses

    def ses_kaybetme(self):
        winsound.Beep(200, 500)

    def sureyi_guncelle(self):
        if self.sure_calisiyor:
            self.gecan_sure += 1
            self.skor_guncelle()
            self.root.after(1000, self.sureyi_guncelle)

    def kart_tikla(self, index):
        if not self.sure_calisiyor and self.eslesen_ciftler < 8 and self.kalan_hak > 0:
            self.sure_calisiyor = True
            self.sureyi_guncelle()

        secilen_btn = self.butonlar[index]

        if secilen_btn['text'] != "🐾" or len(self.secilenler) >= 2 or self.kalan_hak <= 0:
            return

        # Tıklama Sesi
        self.ses_tiklama()

        hayvan = self.semboller[index]
        ozel_renk = self.hayvan_renkleri[hayvan]

        secilen_btn.config(text=hayvan, bg=ozel_renk, fg="#2c3e50")
        self.secilenler.append((index, secilen_btn))

        if len(self.secilenler) == 2:
            self.hamle_sayisi += 1
            self.skor_guncelle()
            self.root.after(600, self.eslesme_kontrol)

    def eslesme_kontrol(self):
        idx1, btn1 = self.secilenler[0]
        idx2, btn2 = self.secilenler[1]

        if self.semboller[idx1] == self.semboller[idx2]:
            # Doğru Eşleşme
            self.ses_basarili()
            btn1.config(bg="#2ed573", fg="white", state="disabled")
            btn2.config(bg="#2ed573", fg="white", state="disabled")
            self.eslesen_ciftler += 1
            self.skor_guncelle()

            if self.eslesen_ciftler == 8:
                self.sure_calisiyor = False
                if self.en_iyi_sure is None or self.gecan_sure < self.en_iyi_sure:
                    self.en_iyi_sure = self.gecan_sure
                    self.rekor_label.config(text=f"En İyi Süre: {self.en_iyi_sure} saniye")
                    rekor_mesaj = "\n🎉 Harika! Yeni Rekor Kırdınız!"
                else:
                    rekor_mesaj = ""

                messagebox.showinfo(
                    "Tebrikler!", 
                    f"Tüm hayvanları eşleştirdiniz! 🦁🎉\n\nSüre: {self.gecan_sure} saniye\nHamle: {self.hamle_sayisi}{rekor_mesaj}"
                )
        else:
            # Yanlış Eşleşme (Hata)
            self.ses_hata()
            self.kalan_hak -= 1
            self.hak_guncelle()

            btn1.config(text="🐾", bg="#341f97", fg="#f1c40f")
            btn2.config(text="🐾", bg="#341f97", fg="#f1c40f")

            # Hak Bittiğinde Kaybetme Kontrolü
            if self.kalan_hak <= 0:
                self.sure_calisiyor = False
                self.ses_kaybetme()
                
                # Tüm Kartları Aç
                for i, btn in enumerate(self.butonlar):
                    h = self.semboller[i]
                    btn.config(text=h, bg="#e74c3c", fg="white", state="disabled")

                messagebox.showerror(
                    "Oyun Bitti!", 
                    "3 Yanlış Hamle Yaptınız ve Kaybettiniz! ❌\n\nYeniden başlamak için 'Yeniden Başlat' butonuna tıklayın."
                )

        self.secilenler.clear()

    def hak_guncelle(self):
        kalpler = "❤️ " * self.kalan_hak + "🖤 " * (3 - self.kalan_hak)
        self.hak_label.config(text=f"Kalan Hak: {kalpler}")

    def skor_guncelle(self):
        self.skor_label.config(
            text=f"Hamle: {self.hamle_sayisi} | Eşleşme: {self.eslesen_ciftler}/8 | Süre: {self.gecan_sure}s"
        )

    def oyunu_sifirla(self):
        self.sure_calisiyor = False
        self.gecan_sure = 0
        self.hamle_sayisi = 0
        self.eslesen_ciftler = 0
        self.kalan_hak = 3
        self.secilenler.clear()
        
        random.shuffle(self.semboller)
        self.skor_guncelle()
        self.hak_guncelle()

        for btn in self.butonlar:
            btn.config(text="🐾", bg="#341f97", fg="#f1c40f", state="normal")

if __name__ == "__main__":
    root = tk.Tk()
    app = RenkliHafizaOyunu(root)
    root.mainloop()