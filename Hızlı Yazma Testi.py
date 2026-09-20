import random
import time
import tkinter as tk
from tkinter import ttk

# Test kelimeleri
KELIMELER = [
    "python", "uygulama", "geliştirmek", "kolay", "hızlı", "doğru",
    "yazılım", "teknoloji", "başarı", "pratik", "çalışmak", "ekran",
    "klavye", "program", "bilgisayar", "deneme", "öğrenmek", "tasarım",
    "kodlamak", "dikkat", "sabır", "başlangıç", "hedef", "zaman"
]
TEST_SURESI = 60

class HizliYazmaUygulamasi:
    def __init__(self, root):
        self.root = root
        self.root.title("Hızlı Yazma Testi")
        self.root.geometry("760x540")
        self.root.resizable(False, False)
        self.renkler = {
            "arka": "#eef3f8",
            "lacivert": "#102a43",
            "kart": "#ffffff",
            "metin": "#243b53",
            "soluk": "#627d98",
            "mavi": "#1976d2",
            "yesil": "#20a05a",
            "cizgi": "#d9e2ec",
        }
        self.root.config(bg=self.renkler["arka"])

        self.hedef_kelime = ""
        self.gosterilen_kelimeler = []
        self.baslangic_zamani = None
        self.test_aktif = False
        self.toplam_kelime = 0

        # Üst başlık alanı
        header = tk.Frame(root, bg=self.renkler["lacivert"], height=125)
        header.pack(fill="x")
        header.pack_propagate(False)
        self.baslik_label = tk.Label(
            header, text="⚡ HIZLI YAZMA TESTİ",
            font=("Segoe UI", 24, "bold"), bg=self.renkler["lacivert"], fg="white"
        )
        self.baslik_label.pack(pady=(24, 4))
        tk.Label(
            header, text="Parmaklarını hızlandır, doğruluğunu geliştir.",
            font=("Segoe UI", 10), bg=self.renkler["lacivert"], fg="#b9d8f2"
        ).pack()

        kart = tk.Frame(root, bg=self.renkler["kart"], highlightthickness=1,
                        highlightbackground=self.renkler["cizgi"])
        kart.pack(fill="both", expand=True, padx=42, pady=28)

        icerik = tk.Frame(kart, bg=self.renkler["kart"])
        icerik.pack(fill="both", expand=True, padx=30, pady=24)

        tk.Label(
            icerik, text="60 SANİYELİK KELİME TESTİ",
            font=("Segoe UI", 11, "bold"), bg=self.renkler["kart"],
            fg=self.renkler["metin"]
        ).pack(anchor="w", pady=(0, 9))

        tk.Label(
            icerik, text="Kelimeyi doğru yazınca yenisi gelir. 1 dakikada kaç kelime yazabileceksin?",
            font=("Segoe UI", 9), bg=self.renkler["kart"],
            fg=self.renkler["soluk"]
        ).pack(anchor="w", pady=(0, 8))

        # Hedef kelime alanı
        self.cumle_text = tk.Text(
            icerik, font=("Consolas", 18, "bold"), width=50, height=2,
            wrap="word", bg="#f5f9fd", fg=self.renkler["metin"],
            bd=0, relief="flat", highlightthickness=1,
            highlightbackground=self.renkler["cizgi"], padx=14, pady=12
        )
        self.cumle_text.pack(fill="x", pady=(0, 18))
        
        # Text etiketi renk tanımlamaları
        self.cumle_text.tag_config("dogru", foreground="#168447")
        self.cumle_text.tag_config("yanlis", foreground="#c0392b", background="#fadbd8")
        self.cumle_text.tag_config("kalan", foreground="#9aaabd")
        self.cumle_text.tag_config("aktif", foreground="#1976d2", underline=True)

        # Kullanıcı Giriş Alanı
        self.entry = tk.Entry(
            icerik, font=("Consolas", 16), state="disabled", relief="flat",
            bg="white", fg=self.renkler["metin"], insertbackground=self.renkler["mavi"],
            highlightthickness=1, highlightbackground=self.renkler["cizgi"],
            highlightcolor=self.renkler["mavi"]
        )
        self.entry.pack(fill="x", ipady=10, pady=(0, 18))
        self.entry.bind("<KeyRelease>", self.klavye_kontrol)

        # Süre ve istatistik alanı
        self.bilgi_label = tk.Label(
            icerik, text="Kalan süre: 60s  |  Hız: 0 WPM  |  Doğruluk: %100",
            font=("Segoe UI", 11, "bold"), bg=self.renkler["kart"], fg=self.renkler["mavi"]
        )
        self.bilgi_label.pack(pady=(0, 15))

        # Başlat / yeniden başlat düğmesi
        self.buton = tk.Button(
            icerik, text="Testi Başlat  →", font=("Segoe UI", 11, "bold"),
            bg=self.renkler["yesil"], fg="white", activebackground="#168447",
            activeforeground="white", command=self.testi_baslat, relief="flat",
            cursor="hand2", padx=22, pady=10
        )
        self.buton.pack()
        self.root.bind("<Return>", lambda event: self.testi_baslat() if not self.test_aktif else None)

    def testi_baslat(self):
        self.toplam_kelime = 0
        self.gosterilen_kelimeler = [random.choice(KELIMELER) for _ in range(6)]
        self.hedef_kelime = self.gosterilen_kelimeler[0]
        self.kelimeleri_goster()

        # Giriş alanını temizle ve aktif et.
        self.entry.config(state="normal")
        self.entry.delete(0, tk.END)
        self.entry.focus()

        self.baslangic_zamani = None
        self.test_aktif = True
        self.buton.config(text="Yeniden Başlat", bg="#e67e22")
        self.bilgi_label.config(text="Yazmaya başladığında 60 saniye başlar...")

    def kelimeleri_goster(self):
        """Sıradaki kelimeleri yatay bir şerit halinde gösterir."""
        self.cumle_text.config(state="normal")
        self.cumle_text.delete("1.0", tk.END)
        for index, kelime in enumerate(self.gosterilen_kelimeler):
            baslangic = self.cumle_text.index(tk.END)
            self.cumle_text.insert(tk.END, kelime)
            bitis = self.cumle_text.index(tk.END)
            self.cumle_text.tag_add("aktif" if index == 0 else "kalan", baslangic, bitis)
            if index < len(self.gosterilen_kelimeler) - 1:
                self.cumle_text.insert(tk.END, "   ")
        self.cumle_text.config(state="disabled")

    def sonraki_cumleyi_hazirla(self):
        self.toplam_kelime += 1
        self.gosterilen_kelimeler.pop(0)
        self.gosterilen_kelimeler.append(random.choice(KELIMELER))
        self.hedef_kelime = self.gosterilen_kelimeler[0]
        self.kelimeleri_goster()
        self.entry.delete(0, tk.END)
        self.entry.focus_set()

    def klavye_kontrol(self, event):
        if not self.test_aktif:
            return

        # İlk tuşa basıldığında süreyi başlat
        if self.baslangic_zamani is None:
            self.baslangic_zamani = time.time()
            self.sureyi_guncelle()

        yazilan_metin = self.entry.get()
        
        self.cumleyi_renklendir(yazilan_metin)

        # Kelime tamamlanınca sayacı artır ve yeni kelimeye geç.
        if yazilan_metin == self.hedef_kelime:
            self.sonraki_cumleyi_hazirla()

    def cumleyi_renklendir(self, yazilan_metin):
        """Hedef kelimenin doğru kısmını yeşil, yanlış kısmını kırmızı gösterir."""
        self.cumle_text.config(state="normal")
        self.cumle_text.tag_remove("dogru", "1.0", tk.END)
        self.cumle_text.tag_remove("yanlis", "1.0", tk.END)
        self.cumle_text.tag_remove("kalan", "1.0", tk.END)
        self.cumle_text.tag_remove("aktif", "1.0", tk.END)

        karakter_baslangici = 0
        for index, kelime in enumerate(self.gosterilen_kelimeler):
            kelime_sonu = karakter_baslangici + len(kelime)
            yazilan_kelime = yazilan_metin if index == 0 else ""
            kelime_doldu = len(yazilan_kelime) == len(kelime)
            kelime_dogru = kelime_doldu and yazilan_kelime == kelime

            if not yazilan_kelime:
                etiket = "kalan"
            elif kelime_dogru:
                etiket = "dogru"
            elif any(
                yazilan_kelime[i] != kelime[i]
                for i in range(min(len(yazilan_kelime), len(kelime)))
            ):
                etiket = "yanlis"
            else:
                etiket = "dogru"

            baslangic_index = f"1.0 + {karakter_baslangici} char"
            bitis_index = f"1.0 + {kelime_sonu} char"
            yazilan_uzunluk = len(yazilan_kelime)
            if etiket == "kalan":
                self.cumle_text.tag_add(etiket, baslangic_index, bitis_index)
            elif etiket == "yanlis" or kelime_doldu:
                self.cumle_text.tag_add(etiket, baslangic_index, bitis_index)
            else:
                self.cumle_text.tag_add(
                    "dogru", baslangic_index,
                    f"1.0 + {karakter_baslangici + yazilan_uzunluk} char"
                )
                self.cumle_text.tag_add(
                    "kalan", f"1.0 + {karakter_baslangici + yazilan_uzunluk} char", bitis_index
                )

            karakter_baslangici = kelime_sonu + 3

        self.cumle_text.config(state="disabled")

    def sureyi_guncelle(self):
        if self.test_aktif and self.baslangic_zamani:
            gecen_sure = time.time() - self.baslangic_zamani
            kalan_sure = max(0, TEST_SURESI - gecen_sure)
            yazilan_metin = self.entry.get()

            if gecen_sure >= TEST_SURESI:
                self.testi_bitir()
                return
            
            # WPM ve Doğruluk hesabı
            kelime_sayisi = self.toplam_kelime + len(yazilan_metin.split())
            wpm = (kelime_sayisi / gecen_sure) * 60 if gecen_sure > 0 else 0
            
            dogru_sayisi = sum(1 for i, c in enumerate(yazilan_metin) if i < len(self.hedef_kelime) and c == self.hedef_kelime[i])
            dogruluk = (dogru_sayisi / len(yazilan_metin)) * 100 if len(yazilan_metin) > 0 else 100

            self.bilgi_label.config(
                text=f"Kalan süre: {kalan_sure:.1f}s | Hız: {int(wpm)} WPM | Doğruluk: %{int(dogruluk)}"
            )
            # Her 100ms'de bir süreyi canlı güncelle
            self.root.after(100, self.sureyi_guncelle)

    def testi_bitir(self):
        self.test_aktif = False
        toplam_kelime = self.toplam_kelime
        
        self.entry.config(state="disabled")
        self.bilgi_label.config(
            text=f"🎉 Süre doldu! 1 dakikada {toplam_kelime} kelime yazdın.",
            fg="#2ecc71"
        )

if __name__ == "__main__":
    root = tk.Tk()
    app = HizliYazmaUygulamasi(root)
    root.mainloop()