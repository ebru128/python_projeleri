import tkinter as tk
from tkinter import ttk, messagebox
import requests


class DovizCeviriciApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Döviz Çevirici")
        self.root.geometry("520x610")
        self.root.resizable(False, False)
        self.root.configure(bg="#eef3f8")
        
        self.colors = {
            "navy": "#102a43",
            "blue": "#1976d2",
            "blue_dark": "#125aa3",
            "text": "#243b53",
            "muted": "#627d98",
            "background": "#eef3f8",
            "card": "#ffffff",
            "line": "#d9e2ec",
            "result": "#e8f3ff",
        }

        self.style = ttk.Style()
        self.style.theme_use("clam")

        self.style.configure(
            "Currency.TCombobox",
            fieldbackground=self.colors["card"],
            background=self.colors["card"],
            foreground=self.colors["text"],
            bordercolor=self.colors["line"],
            padding=8,
            font=("Segoe UI", 11),
        )
        self.style.configure(
            "Convert.TButton",
            background=self.colors["blue"],
            foreground="white",
            borderwidth=0,
            padding=(16, 11),
            font=("Segoe UI", 11, "bold"),
        )
        self.style.map("Convert.TButton", background=[("active", self.colors["blue_dark"])])

        header = tk.Frame(root, bg=self.colors["navy"], height=145)
        header.pack(fill="x")
        header.pack_propagate(False)

        tk.Label(
            header, text="↗", bg=self.colors["navy"], fg="#7cc4ff",
            font=("Segoe UI", 30, "bold")
        ).pack(pady=(18, 0))
        tk.Label(
            header, text="Döviz Çevirici", bg=self.colors["navy"], fg="white",
            font=("Segoe UI", 22, "bold")
        ).pack()
        tk.Label(
            header, text="Güncel kurlarla hızlı ve kolay dönüşüm",
            bg=self.colors["navy"], fg="#b9d8f2", font=("Segoe UI", 10)
        ).pack(pady=(2, 12))

        main_frame = tk.Frame(root, bg=self.colors["card"], highlightthickness=1,
                              highlightbackground=self.colors["line"])
        main_frame.pack(fill="both", expand=True, padx=28, pady=25)

        content = tk.Frame(main_frame, bg=self.colors["card"])
        content.pack(fill="both", expand=True, padx=28, pady=24)
        content.columnconfigure(0, weight=1)
        content.columnconfigure(1, weight=1)

        tk.Label(content, text="Dönüştürmek istediğiniz miktarı girin",
                 bg=self.colors["card"], fg=self.colors["text"],
                 font=("Segoe UI", 11, "bold")).grid(
                     row=0, column=0, columnspan=2, sticky="w", pady=(0, 8)
                 )

        self.amount_entry = tk.Entry(
            content, font=("Segoe UI", 18, "bold"), relief="flat",
            bg="#f7fafd", fg=self.colors["text"], insertbackground=self.colors["blue"],
            highlightthickness=1, highlightbackground=self.colors["line"],
            highlightcolor=self.colors["blue"]
        )
        self.amount_entry.grid(row=1, column=0, columnspan=2, sticky="ew", ipady=8, pady=(0, 20))
        self.amount_entry.insert(0, "100")

        self.currencies = ["USD", "EUR", "TRY", "GBP", "CAD", "CHF", "JPY", "AZN"]

        tk.Label(content, text="Kaynak", bg=self.colors["card"], fg=self.colors["muted"],
                 font=("Segoe UI", 9, "bold")).grid(row=2, column=0, sticky="w", pady=(0, 6))
        tk.Label(content, text="Hedef", bg=self.colors["card"], fg=self.colors["muted"],
                 font=("Segoe UI", 9, "bold")).grid(row=2, column=1, sticky="w", padx=(12, 0), pady=(0, 6))

        self.from_currency_cb = ttk.Combobox(content, values=self.currencies, state="readonly",
                                             style="Currency.TCombobox")
        self.from_currency_cb.grid(row=3, column=0, sticky="ew", pady=(0, 18))
        self.from_currency_cb.set("USD")

        self.to_currency_cb = ttk.Combobox(content, values=self.currencies, state="readonly",
                                           style="Currency.TCombobox")
        self.to_currency_cb.grid(row=3, column=1, sticky="ew", padx=(12, 0), pady=(0, 18))
        self.to_currency_cb.set("TRY")

        swap_btn = tk.Button(content, text="↔  Birimleri Değiştir", command=self.birimleri_degistir,
                             bg="#f0f6fc", fg=self.colors["blue"], activebackground="#dceeff",
                             activeforeground=self.colors["blue_dark"], relief="flat", cursor="hand2",
                             font=("Segoe UI", 9, "bold"), padx=10, pady=6)
        swap_btn.grid(row=4, column=0, columnspan=2, pady=(0, 16))

        convert_btn = ttk.Button(content, text="Dönüştür  →", command=self.cevir, style="Convert.TButton")
        convert_btn.grid(row=5, column=0, columnspan=2, sticky="ew", pady=(0, 20))

        result_frame = tk.Frame(content, bg=self.colors["result"], padx=16, pady=14)
        result_frame.grid(row=6, column=0, columnspan=2, sticky="ew")
        result_frame.columnconfigure(0, weight=1)

        tk.Label(result_frame, text="SONUÇ", bg=self.colors["result"], fg=self.colors["blue"],
                 font=("Segoe UI", 8, "bold")).grid(row=0, column=0, sticky="w")
        self.result_label = tk.Label(result_frame, text="Dönüşüm sonucu burada görünecek",
                                     bg=self.colors["result"], fg=self.colors["text"],
                                     font=("Segoe UI", 14, "bold"), anchor="w")
        self.result_label.grid(row=1, column=0, sticky="ew", pady=(4, 2))

        self.rate_label = tk.Label(result_frame, text="", bg=self.colors["result"],
                                   fg=self.colors["muted"], font=("Segoe UI", 9))
        self.rate_label.grid(row=2, column=0, sticky="w")

        self.status_label = tk.Label(content, text="Hazır", bg=self.colors["card"],
                                     fg=self.colors["muted"], font=("Segoe UI", 9))
        self.status_label.grid(row=7, column=0, columnspan=2, pady=(16, 0))

        self.amount_entry.focus_set()
        self.root.bind("<Return>", lambda event: self.cevir())

    def birimleri_degistir(self):
        kaynak = self.from_currency_cb.get()
        hedef = self.to_currency_cb.get()
        self.from_currency_cb.set(hedef)
        self.to_currency_cb.set(kaynak)
        self.status_label.config(text="Para birimleri değiştirildi", fg=self.colors["blue"])

    def cevir(self):
        kaynak = self.from_currency_cb.get()
        hedef = self.to_currency_cb.get()
        miktar_str = self.amount_entry.get().strip()

        # Miktar doğrulaması
        try:
            miktar = float(miktar_str)
            if miktar <= 0:
                messagebox.showwarning("Uyarı", "Lütfen 0'dan büyük bir miktar girin.")
                return
        except ValueError:
            messagebox.showerror("Hata", "Lütfen geçerli bir sayısal miktar girin.")
            return

        self.status_label.config(text="Güncel kurlar alınıyor...", fg=self.colors["blue"])
        self.root.update_idletasks()

        url = f"https://open.er-api.com/v6/latest/{kaynak}"
        try:
            response = requests.get(url, timeout=5)
            response.raise_for_status()
            data = response.json()

            if data.get("result") == "success":
                kurlar = data.get("rates", {})
                if hedef in kurlar:
                    kur = kurlar[hedef]
                    sonuc = miktar * kur
                    
                    self.result_label.config(text=f"{miktar:,.2f} {kaynak} = {sonuc:,.2f} {hedef}")
                    self.rate_label.config(text=f"Anlık Kur: 1 {kaynak} = {kur:.4f} {hedef}")
                    self.status_label.config(text="Dönüşüm başarıyla tamamlandı", fg="#2e7d32")
                else:
                    self.status_label.config(text="Kur bulunamadı", fg="#c62828")
                    messagebox.showerror("Hata", f"'{hedef}' para birimi kuru bulunamadı.")
            else:
                self.status_label.config(text="Kur bilgisi alınamadı", fg="#c62828")
                messagebox.showerror("Hata", "Döviz kurları alınamadı.")

        except (requests.exceptions.RequestException, ValueError) as e:
            self.status_label.config(text="Bağlantı kurulamadı", fg="#c62828")
            messagebox.showerror("Bağlantı Hatası", f"İnternet bağlantısı veya API hatası:\n{e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = DovizCeviriciApp(root)
    root.mainloop()