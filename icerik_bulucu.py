import tkinter as tk
from tkinter import ttk, messagebox
import webbrowser
import requests
from bs4 import BeautifulSoup
import threading
from urllib.parse import urljoin

class ContentAggregatorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("İçerik Bulucu - Teknoloji Haber Toplayıcı")
        self.root.geometry("800x500")

        # Üst Panel (Arama ve Buton)
        top_frame = ttk.Frame(self.root, padding=10)
        top_frame.pack(fill=tk.X)

        self.title_label = ttk.Label(top_frame, text="Hacker News Son Başlıklar", font=("Helvetica", 14, "bold"))
        self.title_label.pack(side=tk.LEFT)

        self.search_entry = ttk.Entry(top_frame, width=28)
        self.search_entry.pack(side=tk.LEFT, padx=(20, 6))
        self.search_entry.insert(0, "Aramak istediğiniz konu")
        self.search_entry.bind("<FocusIn>", self.clear_search_placeholder)
        self.search_entry.bind("<Return>", lambda _event: self.start_fetching())

        self.btn_fetch = ttk.Button(top_frame, text="İçerik Ara", command=self.start_fetching)
        self.btn_fetch.pack(side=tk.RIGHT)

        # Durum Bilgisi
        self.status_label = ttk.Label(self.root, text="Başlamak için 'İçerikleri Getir' butonuna basın.", padding=5)
        self.status_label.pack(anchor=tk.W)

        # Liste Alanı (Treeview)
        columns = ("title", "url")
        self.tree = ttk.Treeview(self.root, columns=columns, show="headings", selectmode="browse")
        
        self.tree.heading("title", text="İçerik Başlığı")
        self.tree.heading("url", text="Bağlantı (URL)")
        
        self.tree.column("title", width=400, anchor=tk.W)
        self.tree.column("url", width=350, anchor=tk.W)
        
        self.tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        # Scrollbar Ekleme
        scrollbar = ttk.Scrollbar(self.tree, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Çift Tıklama Olayı (Web sitesini açmak için)
        self.tree.bind("<Double-1>", self.open_link)

    def start_fetching(self):
        """Arayüzün donmaması için veri çekme işlemini ayrı bir thread'de başlatır."""
        search_term = self.search_entry.get().strip()
        if search_term == "Aramak istediğiniz konu":
            search_term = ""

        self.btn_fetch.config(state=tk.DISABLED)
        message = f"'{search_term}' aranıyor..." if search_term else "Son içerikler çekiliyor..."
        self.status_label.config(text=message)
        
        # Liste temizle
        for item in self.tree.get_children():
            self.tree.delete(item)

        threading.Thread(target=self.fetch_content, args=(search_term,), daemon=True).start()

    def clear_search_placeholder(self, _event):
        if self.search_entry.get() == "Aramak istediğiniz konu":
            self.search_entry.delete(0, tk.END)

    def fetch_content(self, search_term):
        """Hacker News'te anahtar kelimeyle arama yapar veya son başlıkları getirir."""
        url = "https://news.ycombinator.com/"
        headers = {"User-Agent": "Mozilla/5.0"}

        try:
            if search_term:
                response = requests.get(
                    "https://hn.algolia.com/api/v1/search",
                    params={"query": search_term, "tags": "story", "hitsPerPage": 30},
                    timeout=10,
                )
                response.raise_for_status()
                articles = []
                for result in response.json().get("hits", []):
                    title = result.get("title") or result.get("story_title")
                    link = result.get("url") or f"https://news.ycombinator.com/item?id={result.get('objectID')}"
                    if title and link:
                        articles.append((title, link))
            else:
                response = requests.get(url, headers=headers, timeout=10)
                response.raise_for_status()
                soup = BeautifulSoup(response.text, "html.parser")
                articles = []
                for title_tag in soup.find_all("span", class_="titleline"):
                    link_tag = title_tag.find("a")
                    if link_tag:
                        articles.append((link_tag.text, urljoin(url, link_tag["href"])))

            self.root.after(0, self.update_treeview, articles, search_term)
        except Exception as e:
            self.root.after(0, self.show_error, f"Baglanti hatasi: {str(e)}")

    def update_treeview(self, articles, search_term):
        """Verileri tabloya ekler"""
        for title, link in articles:
            self.tree.insert("", tk.END, values=(title, link))
        
        description = f"'{search_term}' için" if search_term else ""
        self.status_label.config(text=f"{description} toplam {len(articles)} içerik listelendi. Bağlantıyı açmak için çift tıklayın.")
        self.btn_fetch.config(state=tk.NORMAL)

    def show_error(self, message):
        """Hata durumunda kullanıcıyı bilgilendirir"""
        messagebox.showerror("Hata", message)
        self.status_label.config(text="İşlem başarısız.")
        self.btn_fetch.config(state=tk.NORMAL)

    def open_link(self, event):
        """Seçilen satırın bağlantısını varsayılan tarayıcıda açar"""
        selected_item = self.tree.selection()
        if selected_item:
            item_values = self.tree.item(selected_item[0], "values")
            if len(item_values) > 1:
                url = item_values[1]
                webbrowser.open(url)

if __name__ == "__main__":
    root = tk.Tk()
    app = ContentAggregatorApp(root)
    root.mainloop()