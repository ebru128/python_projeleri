import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import threading
import re
from nltk.tokenize import sent_tokenize
from googleapiclient.discovery import build
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

class PlagiarismCheckerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Python İntihal Denetleyicisi (NLP & Google API)")
        self.root.geometry("850x650")

        # Üst Panel
        top_frame = ttk.Frame(self.root, padding=10)
        top_frame.pack(fill=tk.X)

        ttk.Label(top_frame, text="İntihal Kontrolü Yapılacak Metin:", font=("Helvetica", 11, "bold")).pack(anchor=tk.W)

        settings_frame = ttk.Frame(self.root, padding=(10, 0, 10, 5))
        settings_frame.pack(fill=tk.X)

        ttk.Label(settings_frame, text="Google API Key:").pack(side=tk.LEFT)
        self.api_key_entry = ttk.Entry(settings_frame, width=28, show="*")
        self.api_key_entry.pack(side=tk.LEFT, padx=(5, 15))

        ttk.Label(settings_frame, text="Search Engine ID:").pack(side=tk.LEFT)
        self.search_engine_entry = ttk.Entry(settings_frame, width=28)
        self.search_engine_entry.pack(side=tk.LEFT, padx=5)

        # Metin Giriş Alanı
        self.txt_input = scrolledtext.ScrolledText(self.root, wrap=tk.WORD, height=10, font=("Calibri", 11))
        self.txt_input.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        # İşlem Butonu ve İlerleme Çubuğu
        action_frame = ttk.Frame(self.root, padding=5)
        action_frame.pack(fill=tk.X, padx=10)

        self.btn_check = ttk.Button(action_frame, text="İntihal Denetimi Yap", command=self.start_check)
        self.btn_check.pack(side=tk.LEFT, padx=5)

        self.progress = ttk.Progressbar(action_frame, orient=tk.HORIZONTAL, mode='indeterminate')
        self.progress.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)

        self.lbl_status = ttk.Label(self.root, text="Hazır", padding=5)
        self.lbl_status.pack(anchor=tk.W, padx=10)

        # Sonuç Alanı (Treeview Tablosu)
        result_frame = ttk.LabelFrame(self.root, text="Analiz Sonuçları ve Benzerlik Oranları", padding=10)
        result_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        columns = ("sentence", "similarity", "source")
        self.tree = ttk.Treeview(result_frame, columns=columns, show="headings", selectmode="browse")

        self.tree.heading("sentence", text="Cümle")
        self.tree.heading("similarity", text="Benzerlik Oranı")
        self.tree.heading("source", text="Eşleşen Kaynak (URL)")

        self.tree.column("sentence", width=400, anchor=tk.W)
        self.tree.column("similarity", width=120, anchor=tk.CENTER)
        self.tree.column("source", width=250, anchor=tk.W)

        tree_scroll = ttk.Scrollbar(result_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=tree_scroll.set)
        
        tree_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree.pack(fill=tk.BOTH, expand=True)

    def start_check(self):
        text = self.txt_input.get("1.0", tk.END).strip()
        if not text:
            messagebox.showwarning("Uyarı", "Lütfen analiz edilecek bir metin girin.")
            return

        api_key = self.api_key_entry.get().strip()
        search_engine_id = self.search_engine_entry.get().strip()
        if not api_key or not search_engine_id:
            messagebox.showerror(
                "Eksik bilgi",
                "Önce Google API Key ve Search Engine ID alanlarını doldurun.",
            )
            return

        self.btn_check.config(state=tk.DISABLED)
        self.progress.start(10)
        self.lbl_status.config(text="NLP analizi yapılıyor ve Google üzerinde aranıyor...")

        # Tabloyu temizle
        for item in self.tree.get_children():
            self.tree.delete(item)

        # Threading kullanarak GUI'nin donmasını önle
        threading.Thread(
            target=self.run_plagiarism_check,
            args=(text, api_key, search_engine_id),
            daemon=True,
        ).start()

    def run_plagiarism_check(self, text, api_key, search_engine_id):
        try:
            # 1. NLP Aşaması: Cümlelere Ayırma (Tokenization)
            try:
                # Türkçe model yoksa aşağıdaki düzenli ifade ile devam edilir.
                sentences = sent_tokenize(text, language="turkish")
            except LookupError:
                sentences = re.split(r"(?<=[.!?])\s+", text)

            sentences = [sentence.strip() for sentence in sentences if sentence.strip()]

            results = []
            service = build("customsearch", "v1", developerKey=api_key)

            for sentence in sentences:
                clean_sentence = self.clean_text(sentence)
                if len(clean_sentence.split()) < 4:  # Çok kısa cümleleri sorgulama
                    continue

                # 2. Google API ile Arama Yapma
                query = f'"{clean_sentence}"'  # Tam eşleşme için tırnak içinde ara
                res = service.cse().list(q=query, cx=search_engine_id, num=3).execute()

                items = res.get("items", [])
                max_similarity = 0.0
                best_match_url = "Eşleşme Bulunamadı (Özgün)"

                if items:
                    for item in items:
                        snippet = item.get("snippet", "")
                        link = item.get("link", "")
                        
                        # 3. NLP & Makine Öğrenmesi Aşaması: Cosine Similarity ile Benzerlik Hesabı
                        similarity = self.calculate_similarity(clean_sentence, snippet)
                        if similarity > max_similarity:
                            max_similarity = similarity
                            best_match_url = link

                results.append((sentence, f"%{max_similarity * 100:.1f}", best_match_url))

            self.root.after(0, self.update_ui_results, results)

        except Exception as e:
            self.root.after(0, self.show_error, str(e))

    def clean_text(self, text):
        """Noktalama işaretlerini temizler ve küçük harfe çevirir."""
        text = re.sub(r'[^\w\s]', '', text)
        return text.strip().lower()

    def calculate_similarity(self, text1, text2):
        """TF-IDF Vectorizer ve Cosine Similarity kullanarak iki metin arasındaki benzerliği ölçer."""
        if not text1 or not text2:
            return 0.0
        
        vectorizer = TfidfVectorizer().fit_transform([text1, text2])
        vectors = vectorizer.toarray()
        return cosine_similarity([vectors[0]], [vectors[1]])[0][0]

    def update_ui_results(self, results):
        self.progress.stop()
        self.btn_check.config(state=tk.NORMAL)
        self.lbl_status.config(text=f"Analiz tamamlandı. Toplam {len(results)} cümle incelendi.")

        for sentence, similarity, url in results:
            self.tree.insert("", tk.END, values=(sentence, similarity, url))

    def show_error(self, err_msg):
        self.progress.stop()
        self.btn_check.config(state=tk.NORMAL)
        self.lbl_status.config(text="Hata oluştu.")
        messagebox.showerror("Hata", f"İşlem sırasında bir hata oluştu:\n{err_msg}")

if __name__ == "__main__":
    root = tk.Tk()
    app = PlagiarismCheckerApp(root)
    root.mainloop()