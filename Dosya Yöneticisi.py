import os
import shutil
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog

class FileExplorer:
    def __init__(self, root):
        self.root = root
        self.root.title("Python Dosya Yöneticisi & Editör")
        self.root.geometry("1050x600")

        self.current_path = os.path.expanduser("~")
        self.clipboard = None
        self.clipboard_action = None
        self.current_preview_file = None

        # --- ÜST ARAÇ ÇUBUĞU ---
        top_frame = ttk.Frame(self.root, padding=5)
        top_frame.pack(fill=tk.X)

        # Üst Klasör Butonu
        self.btn_up = ttk.Button(top_frame, text="▲ Üst Klasör", command=self.go_up)
        self.btn_up.pack(side=tk.LEFT, padx=2)

        # GİZLİ İŞLEMLER MENÜSÜ (Üstüne basınca açılır)
        self.action_menu = tk.Menu(self.root, tearoff=0)
        self.action_menu.add_command(label="📋 Kopyala", command=self.copy_item)
        self.action_menu.add_command(label="📌 Yapıştır", command=self.paste_item)
        self.action_menu.add_separator()
        self.action_menu.add_command(label="📁 Yeni Klasör", command=self.create_folder)
        self.action_menu.add_command(label="🗑️ Sil", command=self.delete_item)

        # İşlemler Butonu (Menüyü açan buton)
        self.btn_actions = ttk.Button(top_frame, text="İşlemler ⚙️", command=self.show_action_menu)
        self.btn_actions.pack(side=tk.LEFT, padx=2)

        # Adres Çubuğu
        self.path_entry = ttk.Entry(top_frame)
        self.path_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(10, 2))
        self.path_entry.bind("<Return>", lambda e: self.load_dir(self.path_entry.get()))

        self.btn_go = ttk.Button(top_frame, text="Git", command=lambda: self.load_dir(self.path_entry.get()))
        self.btn_go.pack(side=tk.LEFT, padx=2)

        # --- ANA PANEL (PanedWindow) ---
        main_paned = ttk.PanedWindow(self.root, orient=tk.HORIZONTAL)
        main_paned.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # SOL PANEL: Dosya Listesi
        left_frame = ttk.Frame(main_paned)
        main_paned.add(left_frame, weight=3)

        columns = ("name", "type", "size")
        self.tree = ttk.Treeview(left_frame, columns=columns, show="headings", selectmode="browse")
        
        self.tree.heading("name", text="İsim")
        self.tree.heading("type", text="Tür")
        self.tree.heading("size", text="Boyut")

        self.tree.column("name", width=300, anchor=tk.W)
        self.tree.column("type", width=90, anchor=tk.CENTER)
        self.tree.column("size", width=90, anchor=tk.E)

        scrollbar_tree = ttk.Scrollbar(left_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar_tree.set)
        scrollbar_tree.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree.pack(fill=tk.BOTH, expand=True)

        self.tree.bind("<Double-1>", self.on_double_click)
        self.tree.bind("<<TreeviewSelect>>", self.on_select_item)
        
        # Sağ tıklandığında da gizli menüyü açma özelliği
        self.tree.bind("<Button-3>", self.show_context_menu)

        # SAĞ PANEL: Metin Düzenleyici
        right_frame = ttk.LabelFrame(main_paned, text="Metin Dosyası Önizleme ve Düzenleme", padding=5)
        main_paned.add(right_frame, weight=2)

        preview_top_frame = ttk.Frame(right_frame)
        preview_top_frame.pack(fill=tk.X, pady=(0, 5))

        self.lbl_preview_file = ttk.Label(preview_top_frame, text="Hiçbir dosya seçilmedi", font=("Helvetica", 9, "italic"))
        self.lbl_preview_file.pack(side=tk.LEFT, fill=tk.X, expand=True)

        self.btn_save = ttk.Button(preview_top_frame, text="Değişiklikleri Kaydet", command=self.save_file_content, state=tk.DISABLED)
        self.btn_save.pack(side=tk.RIGHT)

        text_scroll = ttk.Scrollbar(right_frame, orient=tk.VERTICAL)
        self.text_editor = tk.Text(right_frame, wrap=tk.WORD, yscrollcommand=text_scroll.set, font=("Consolas", 10))
        text_scroll.config(command=self.text_editor.yview)
        
        text_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.text_editor.pack(fill=tk.BOTH, expand=True)

        self.load_dir(self.current_path)

    def show_action_menu(self):
        """Üstteki İşlemler butonuna basılınca açılan menü"""
        x = self.btn_actions.winfo_rootx()
        y = self.btn_actions.winfo_rooty() + self.btn_actions.winfo_height()
        self.action_menu.post(x, y)

    def show_context_menu(self, event):
        """Dosya listesinde sağ tıklandığında açılan menü"""
        item = self.tree.identify_row(event.y)
        if item:
            self.tree.selection_set(item)
            self.action_menu.post(event.x_root, event.y_root)

    def load_dir(self, path):
        if not os.path.exists(path) or not os.path.isdir(path):
            messagebox.showerror("Hata", "Geçersiz klasör yolu!")
            return

        self.current_path = os.path.abspath(path)
        self.path_entry.delete(0, tk.END)
        self.path_entry.insert(0, self.current_path)

        for item in self.tree.get_children():
            self.tree.delete(item)

        self.clear_preview()

        try:
            items = os.listdir(self.current_path)
            for item in items:
                full_path = os.path.join(self.current_path, item)
                if os.path.isdir(full_path):
                    self.tree.insert("", tk.END, values=(item, "Klasör", "-"))
                else:
                    size = f"{os.path.getsize(full_path) / 1024:.1f} KB"
                    self.tree.insert("", tk.END, values=(item, "Dosya", size))
        except PermissionError:
            messagebox.showwarning("Erişim Engellendi", "Bu klasörü açmak için izniniz yok!")

    def on_select_item(self, event):
        selected = self.tree.selection()
        if not selected:
            self.clear_preview()
            return
        
        item_name = self.tree.item(selected[0], "values")[0]
        full_path = os.path.join(self.current_path, item_name)

        if os.path.isfile(full_path):
            text_extensions = ('.txt', '.py', '.json', '.html', '.css', '.js', '.md', '.csv', '.xml', '.yaml', '.yml', '.ini', '.log')
            if full_path.lower().endswith(text_extensions):
                self.load_file_preview(full_path)
            else:
                self.clear_preview()
                self.lbl_preview_file.config(text=f"'{item_name}' metin dosyası olmadığı için önizlenemiyor.")
        else:
            self.clear_preview()

    def load_file_preview(self, file_path):
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
            self.text_editor.delete("1.0", tk.END)
            self.text_editor.insert("1.0", content)
            self.current_preview_file = file_path
            self.lbl_preview_file.config(text=f"Düzenlenen: {os.path.basename(file_path)}")
            self.btn_save.config(state=tk.NORMAL)
        except UnicodeDecodeError:
            try:
                with open(file_path, "r", encoding="latin-1") as f:
                    content = f.read()
                self.text_editor.delete("1.0", tk.END)
                self.text_editor.insert("1.0", content)
                self.current_preview_file = file_path
                self.lbl_preview_file.config(text=f"Düzenlenen: {os.path.basename(file_path)}")
                self.btn_save.config(state=tk.NORMAL)
            except Exception as e:
                self.clear_preview()
                self.lbl_preview_file.config(text="Dosya okunamadı.")
        except Exception as e:
            self.clear_preview()
            self.lbl_preview_file.config(text=f"Hata: {e}")

    def save_file_content(self):
        if not self.current_preview_file:
            return
        try:
            content = self.text_editor.get("1.0", tk.END + "-1c")
            with open(self.current_preview_file, "w", encoding="utf-8") as f:
                f.write(content)
            messagebox.showinfo("Başarılı", "Değişiklikler başarıyla kaydedildi!")
        except Exception as e:
            messagebox.showerror("Hata", f"Dosya kaydedilemedi: {e}")

    def clear_preview(self):
        self.text_editor.delete("1.0", tk.END)
        self.current_preview_file = None
        self.lbl_preview_file.config(text="Hiçbir metin dosyası seçilmedi.")
        self.btn_save.config(state=tk.DISABLED)

    def on_double_click(self, event):
        selected = self.tree.selection()
        if not selected:
            return
        item_name = self.tree.item(selected[0], "values")[0]
        new_path = os.path.join(self.current_path, item_name)
        if os.path.isdir(new_path):
            self.load_dir(new_path)

    def go_up(self):
        parent_path = os.path.dirname(self.current_path)
        if parent_path and parent_path != self.current_path:
            self.load_dir(parent_path)

    def copy_item(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Uyarı", "Lütfen bir dosya veya klasör seçin.")
            return
        item_name = self.tree.item(selected[0], "values")[0]
        self.clipboard = os.path.join(self.current_path, item_name)
        self.clipboard_action = "copy"
        messagebox.showinfo("Kopyalandı", f"'{item_name}' panoya kopyalandı.")

    def paste_item(self):
        if not self.clipboard or not os.path.exists(self.clipboard):
            messagebox.showwarning("Uyarı", "Panoda yapıştırılacak geçerli bir öge yok.")
            return

        item_name = os.path.basename(self.clipboard)
        target_path = os.path.join(self.current_path, item_name)

        try:
            if os.path.isdir(self.clipboard):
                shutil.copytree(self.clipboard, target_path)
            else:
                shutil.copy2(self.clipboard, target_path)
            self.load_dir(self.current_path)
        except Exception as e:
            messagebox.showerror("Hata", f"Yapıştırma işlemi başarısız: {e}")

    def create_folder(self):
        folder_name = simpledialog.askstring("Yeni Klasör", "Klasör adı girin:")
        if folder_name:
            new_path = os.path.join(self.current_path, folder_name)
            try:
                os.makedirs(new_path, exist_ok=True)
                self.load_dir(self.current_path)
            except Exception as e:
                messagebox.showerror("Hata", f"Klasör oluşturulamadı: {e}")

    def delete_item(self):
        selected = self.tree.selection()
        if not selected:
            return
        item_name = self.tree.item(selected[0], "values")[0]
        target_path = os.path.join(self.current_path, item_name)

        if messagebox.askyesno("Silme Onayı", f"'{item_name}' ögesini silmek istediğinize emin misiniz?"):
            try:
                if os.path.isdir(target_path):
                    shutil.rmtree(target_path)
                else:
                    os.remove(target_path)
                self.load_dir(self.current_path)
            except Exception as e:
                messagebox.showerror("Hata", f"Silme başarısız: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = FileExplorer(root)
    root.mainloop()