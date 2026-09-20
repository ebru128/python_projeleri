#!/usr/bin/env python3
"""Bilgi Yarışması - Tkinter sürümü (Python 3.8+, ek kütüphane gerekmez)

Her soruya tek cevap hakkı vardır. Yanlış cevapta doğru cevap gösterilir.
Test sonunda puan gösterilir. En iyi puanlar en_iyi_puanlar.json dosyasında saklanır.
"""
import json
import random
import tkinter as tk
from pathlib import Path
from tkinter import ttk

SKOR_DOSYASI = Path(__file__).with_name("en_iyi_puanlar.json")

TESTLER = {
    "genel": {
        "baslik": "Genel kültür",
        "not": "Sanat, spor ve dünya bilgisi",
        "sorular": [
            ("Mona Lisa tablosunu kim yapmıştır?", "Leonardo da Vinci", ["Michelangelo", "Vincent van Gogh", "Pablo Picasso"]),
            ("Tokyo hangi ülkenin başkentidir?", "Japonya", ["Çin", "Güney Kore", "Tayland"]),
            ("Satrançta her oyuncunun kaç piyonu vardır?", "8", ["6", "10", "12"]),
            ("Antik Olimpiyat Oyunları hangi ülkede başlamıştır?", "Yunanistan", ["İtalya", "Mısır", "Fransa"]),
            ("Bir futbol takımı sahaya kaç oyuncuyla çıkar?", "11", ["9", "10", "12"]),
        ],
    },
    "bilim": {
        "baslik": "Bilim",
        "not": "Uzay, kimya ve insan vücudu",
        "sorular": [
            ("Hangi gezegen “Kızıl Gezegen” olarak bilinir?", "Mars", ["Venüs", "Merkür", "Satürn"]),
            ("Suyun kimyasal formülü nedir?", "H₂O", ["CO₂", "O₂", "NaCl"]),
            ("Güneş Sistemi’ndeki en büyük gezegen hangisidir?", "Jüpiter", ["Satürn", "Uranüs", "Neptün"]),
            ("İnsan vücudundaki en büyük organ hangisidir?", "Deri", ["Karaciğer", "Akciğer", "Beyin"]),
            ("Dünya atmosferinde en çok bulunan gaz hangisidir?", "Azot", ["Oksijen", "Karbondioksit", "Argon"]),
        ],
    },
    "turkiye": {
        "baslik": "Türkiye",
        "not": "Coğrafya ve tarih",
        "sorular": [
            ("Türkiye Cumhuriyeti hangi yıl ilan edilmiştir?", "1923", ["1919", "1920", "1938"]),
            ("Türkiye’nin en yüksek dağı hangisidir?", "Ağrı Dağı", ["Erciyes Dağı", "Uludağ", "Kaçkar Dağı"]),
            ("Türkiye’nin en büyük gölü hangisidir?", "Van Gölü", ["Tuz Gölü", "Beyşehir Gölü", "Eğirdir Gölü"]),
            ("İstanbul Boğazı hangi iki denizi birbirine bağlar?", "Karadeniz ve Marmara", ["Ege ve Akdeniz", "Marmara ve Ege", "Karadeniz ve Akdeniz"]),
            ("Aşağıdaki ülkelerden hangisi Türkiye’nin komşusu değildir?", "Romanya", ["Bulgaristan", "Gürcistan", "Yunanistan"]),
        ],
    },
}

# Renkler
BG = "#EDF0FF"
SURFACE = "#FFFFFF"
INK = "#1A1D4A"
MUTED = "#5B5F8C"
LINE = "#C9CEF0"
ACCENT = "#3B3BF0"
OK, OK_BG = "#17805A", "#DDF5EA"
BAD, BAD_BG = "#C22F45", "#FCE3E7"
GOLD = "#FFC93C"

FONT = "Segoe UI"
HARFLER = "ABCD"
GENISLIK = 560


def en_iyileri_yukle():
    try:
        return json.loads(SKOR_DOSYASI.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}


def en_iyiyi_kaydet(test_id, puan):
    en_iyiler = en_iyileri_yukle()
    if puan > en_iyiler.get(test_id, -1):
        en_iyiler[test_id] = puan
        try:
            SKOR_DOSYASI.write_text(json.dumps(en_iyiler, ensure_ascii=False), encoding="utf-8")
        except OSError:
            pass  # dosyaya yazılamazsa uygulama yine de çalışır


class SinavUygulamasi(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Bilgi Yarışması")
        self.configure(bg=BG)
        self.geometry("640x700")
        self.minsize(600, 640)

        stil = ttk.Style(self)
        try:
            stil.theme_use("clam")
        except tk.TclError:
            pass
        stil.configure("Ana.TButton", font=(FONT, 12, "bold"), padding=(18, 10),
                       background=ACCENT, foreground="white", borderwidth=0)
        stil.map("Ana.TButton", background=[("active", "#2A2AD0")])
        stil.configure("Hayalet.TButton", font=(FONT, 12, "bold"), padding=(18, 10),
                       background=BG, foreground=INK, bordercolor=LINE)
        stil.map("Hayalet.TButton", background=[("active", SURFACE)])

        self.kap = tk.Frame(self, bg=BG)
        self.kap.pack(fill="both", expand=True, padx=40, pady=28)

        self.test_id = None
        self.sorular = []
        self.i = 0
        self.sonuclar = []
        self.kilitli = False
        self.secenek_etiketleri = []
        self.parcalar = []
        self.sonraki_btn = None

        self.bind("<Key>", self.tus_basildi)
        self.ana_ekran()

    # ---------- yardımcılar ----------
    def temizle(self):
        for w in self.kap.winfo_children():
            w.destroy()
        self.secenek_etiketleri = []
        self.parcalar = []
        self.sonraki_btn = None

    def etiket(self, parent, text, size=12, bold=False, fg=INK, **kw):
        return tk.Label(parent, text=text, bg=kw.pop("bg", BG), fg=fg,
                        font=(FONT, size, "bold" if bold else "normal"), **kw)

    # ---------- ana ekran ----------
    def ana_ekran(self):
        self.temizle()
        self.test_id = None
        en_iyiler = en_iyileri_yukle()

        self.etiket(self.kap, "Bilgi Yarışması", 30, True).pack(anchor="w", pady=(10, 6))
        self.etiket(
            self.kap,
            "Bir test seç. Her soruya tek cevap hakkın var; yanlış yaparsan doğru cevabı "
            "hemen görürsün. Test sonunda puanın açıklanır.",
            11, fg=MUTED, wraplength=GENISLIK, justify="left",
        ).pack(anchor="w", pady=(0, 22))

        for test_id, test in TESTLER.items():
            kart = tk.Frame(self.kap, bg=SURFACE, highlightthickness=2, highlightbackground=LINE, cursor="hand2")
            kart.pack(fill="x", pady=6)
            sol = tk.Frame(kart, bg=SURFACE)
            sol.pack(side="left", padx=16, pady=14)
            tk.Label(sol, text=test["baslik"], bg=SURFACE, fg=INK, font=(FONT, 15, "bold")).pack(anchor="w")
            tk.Label(sol, text=f"{test['not']} · {len(test['sorular'])} soru", bg=SURFACE,
                     fg=MUTED, font=(FONT, 10)).pack(anchor="w")
            en_iyi = en_iyiler.get(test_id)
            sag = tk.Frame(kart, bg=SURFACE)
            sag.pack(side="right", padx=16)
            tk.Label(sag, text="–" if en_iyi is None else f"{en_iyi}/{len(test['sorular'])}",
                     bg=SURFACE, fg=INK, font=(FONT, 16, "bold")).pack(anchor="e")
            tk.Label(sag, text="en iyi puan", bg=SURFACE, fg=MUTED, font=(FONT, 9)).pack(anchor="e")

            def tikla(_e, tid=test_id):
                self.testi_baslat(tid)

            def girdi(_e, k=kart):
                k.configure(highlightbackground=ACCENT)

            def cikti(_e, k=kart):
                k.configure(highlightbackground=LINE)

            for w in [kart, sol, sag] + list(sol.winfo_children()) + list(sag.winfo_children()):
                w.bind("<Button-1>", tikla)
                w.bind("<Enter>", girdi)
                w.bind("<Leave>", cikti)

    # ---------- test ----------
    def testi_baslat(self, test_id):
        test = TESTLER[test_id]
        self.test_id = test_id
        self.sorular = []
        for soru, dogru, yanlislar in random.sample(test["sorular"], k=len(test["sorular"])):
            secenekler = yanlislar + [dogru]
            random.shuffle(secenekler)
            self.sorular.append({"soru": soru, "dogru": dogru, "secenekler": secenekler})
        self.i = 0
        self.sonuclar = []
        self.soru_goster()

    def soru_goster(self):
        self.temizle()
        self.kilitli = False
        s = self.sorular[self.i]
        test = TESTLER[self.test_id]

        ust = tk.Frame(self.kap, bg=BG)
        ust.pack(fill="x")
        self.etiket(ust, f"{test['baslik']} · Soru {self.i + 1}/{len(self.sorular)}", 10, fg=MUTED).pack(side="left")
        cik = self.etiket(ust, "Testten çık", 10, fg=MUTED, cursor="hand2")
        cik.configure(font=(FONT, 10, "underline"))
        cik.pack(side="right")
        cik.bind("<Button-1>", lambda _e: self.ana_ekran())

        cubuk = tk.Frame(self.kap, bg=BG)
        cubuk.pack(fill="x", pady=(10, 26))
        for k in range(len(self.sorular)):
            f = tk.Frame(cubuk, height=8, bg=LINE)
            f.pack(side="left", fill="x", expand=True, padx=(0 if k == 0 else 3, 3))
            self.parcalar.append(f)
        self.cubugu_guncelle()

        self.etiket(self.kap, s["soru"], 20, True, wraplength=GENISLIK, justify="left").pack(anchor="w", pady=(0, 20))

        for idx, secenek in enumerate(s["secenekler"]):
            e = tk.Label(self.kap, text=f"{HARFLER[idx]}    {secenek}", anchor="w", justify="left",
                         bg=SURFACE, fg=INK, font=(FONT, 13), padx=16, pady=12,
                         wraplength=GENISLIK - 40, highlightthickness=2, highlightbackground=LINE,
                         cursor="hand2")
            e.pack(fill="x", pady=5)
            e.bind("<Button-1>", lambda _e, n=idx: self.cevapla(n))
            e.bind("<Enter>", lambda _e, w=e: (not self.kilitli) and w.configure(highlightbackground=ACCENT))
            e.bind("<Leave>", lambda _e, w=e: (not self.kilitli) and w.configure(highlightbackground=LINE))
            self.secenek_etiketleri.append(e)

        self.geri_bildirim = tk.Label(self.kap, text="", bg=BG, font=(FONT, 13, "bold"),
                                      wraplength=GENISLIK, justify="left", anchor="w")
        self.geri_bildirim.pack(fill="x", pady=(16, 8))

        son = self.i == len(self.sorular) - 1
        self.sonraki_btn = ttk.Button(self.kap, text="Sonucu gör" if son else "Sonraki soru",
                                      style="Ana.TButton", command=self.sonraki)

    def cubugu_guncelle(self):
        for k, f in enumerate(self.parcalar):
            if k < len(self.sonuclar):
                f.configure(bg=OK if self.sonuclar[k]["dogru_mu"] else BAD)
            elif k == self.i:
                f.configure(bg=ACCENT)
            else:
                f.configure(bg=LINE)

    def cevapla(self, idx):
        if self.kilitli:
            return
        self.kilitli = True
        s = self.sorular[self.i]
        secilen = s["secenekler"][idx]
        dogru_mu = secilen == s["dogru"]
        self.sonuclar.append({"soru": s["soru"], "secilen": secilen, "dogru": s["dogru"], "dogru_mu": dogru_mu})

        for n, e in enumerate(self.secenek_etiketleri):
            metin = s["secenekler"][n]
            if metin == s["dogru"]:
                e.configure(bg=OK_BG, highlightbackground=OK, text=f"✓    {metin}")
            elif n == idx:
                e.configure(bg=BAD_BG, highlightbackground=BAD, text=f"✗    {metin}")
            else:
                e.configure(fg=MUTED, highlightbackground=LINE)
            e.configure(cursor="arrow")

        if dogru_mu:
            self.geri_bildirim.configure(text="Doğru!", fg=OK)
        else:
            self.geri_bildirim.configure(text=f"Yanlış. Doğru cevap: {s['dogru']}", fg=BAD)

        self.cubugu_guncelle()
        self.sonraki_btn.pack(anchor="w")
        self.sonraki_btn.focus_set()

    def sonraki(self):
        if not self.kilitli:
            return
        if self.i < len(self.sorular) - 1:
            self.i += 1
            self.soru_goster()
        else:
            puan = sum(1 for r in self.sonuclar if r["dogru_mu"])
            en_iyiyi_kaydet(self.test_id, puan)
            self.sonuc_goster()

    def tus_basildi(self, olay):
        if not self.test_id or not self.sorular or not self.secenek_etiketleri:
            return
        if not self.kilitli:
            tus = olay.char.upper()
            if tus in HARFLER[:len(self.secenek_etiketleri)]:
                self.cevapla(HARFLER.index(tus))
            elif tus.isdigit() and 1 <= int(tus) <= len(self.secenek_etiketleri):
                self.cevapla(int(tus) - 1)
        elif olay.keysym == "Return":
            self.sonraki()

    # ---------- sonuç ----------
    def sonuc_goster(self):
        self.temizle()
        self.secenek_etiketleri = []
        toplam = len(self.sonuclar)
        puan = sum(1 for r in self.sonuclar if r["dogru_mu"])
        yuzde = round(puan / toplam * 100)
        test = TESTLER[self.test_id]

        self.etiket(self.kap, f"{test['baslik']} testi bitti", 10, fg=MUTED).pack(anchor="w")

        satir = tk.Frame(self.kap, bg=BG)
        satir.pack(anchor="w", pady=(6, 0))
        tk.Label(satir, text=str(puan), bg=BG, fg=INK, font=(FONT, 64, "bold")).pack(side="left")
        tk.Label(satir, text=f"/{toplam}", bg=BG, fg=MUTED, font=(FONT, 24, "bold")).pack(side="left", anchor="s", pady=(0, 14))
        tk.Label(satir, text=f" %{yuzde} ", bg=GOLD, fg=INK, font=(FONT, 14, "bold")).pack(side="left", anchor="s", padx=14, pady=(0, 18))

        if puan == toplam:
            yorum = "Kusursuz! Hepsini doğru bildin."
        elif yuzde >= 60:
            yorum = "İyi iş, çoğunu doğru bildin."
        else:
            yorum = "Yanlışların doğru cevaplarına bakıp testi tekrar deneyebilirsin."
        self.etiket(self.kap, yorum, 13, wraplength=GENISLIK, justify="left").pack(anchor="w", pady=(0, 14))

        for r in self.sonuclar:
            renk = OK if r["dogru_mu"] else BAD
            kart = tk.Frame(self.kap, bg=SURFACE)
            kart.pack(fill="x", pady=3)
            tk.Frame(kart, bg=renk, width=6).pack(side="left", fill="y")
            ic = tk.Frame(kart, bg=SURFACE)
            ic.pack(side="left", fill="x", padx=12, pady=8)
            tk.Label(ic, text=r["soru"], bg=SURFACE, fg=INK, font=(FONT, 11, "bold"),
                     wraplength=GENISLIK - 50, justify="left", anchor="w").pack(anchor="w")
            detay = (f"Doğru: {r['dogru']}" if r["dogru_mu"]
                     else f"Senin cevabın: {r['secilen']} · Doğru cevap: {r['dogru']}")
            tk.Label(ic, text=detay, bg=SURFACE, fg=MUTED, font=(FONT, 10),
                     wraplength=GENISLIK - 50, justify="left", anchor="w").pack(anchor="w")

        butonlar = tk.Frame(self.kap, bg=BG)
        butonlar.pack(anchor="w", pady=(18, 0))
        ttk.Button(butonlar, text="Testi tekrarla", style="Ana.TButton",
                   command=lambda: self.testi_baslat(self.test_id)).pack(side="left", padx=(0, 10))
        ttk.Button(butonlar, text="Başka test seç", style="Hayalet.TButton",
                   command=self.ana_ekran).pack(side="left")


if __name__ == "__main__":
    SinavUygulamasi().mainloop()