import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import cv2
import numpy as np
from matplotlib import pyplot as plt
import os
import ttkbootstrap as tb

# Import modul operasi gambar (pastikan file-file ini ada di direktori yang sama)
from image_operations import *
from histogram_utils import show_histogram
from morpho_operations import apply_morphology

class ImageApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Aplikasi Pengolahan Citra Sederhana")
        self.root.geometry("1000x800")

        # Inisialisasi variabel gambar
        self.img_cv = None
        self.original_img = None
        self.result_img = None

        # Setup GUI dengan scrollbar
        self.canvas = tk.Canvas(root)
        self.scroll_y = tk.Scrollbar(root, orient="vertical", command=self.canvas.yview)
        self.frame = tk.Frame(self.canvas)

        self.frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))

        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)
        self.canvas.create_window((0, 0), window=self.frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scroll_y.set)

        self.canvas.pack(side="left", fill="both", expand=True)
        self.scroll_y.pack(side="right", fill="y")

        self.start_screen()

    def _on_mousewheel(self, event):
        self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")

    def fix_onedrive_path(self, path):
        if '@' in path:
            parts = path.split('@')
            fixed_path = parts[0] + parts[-1].split(':')[-1]
            return os.path.normpath(fixed_path)
        return os.path.normpath(path)

    def load_image(self):
        file_types = [
            ('JPEG files', '*.jpg;*.jpeg'),
            ('PNG files', '*.png'),
            ('Bitmap files', '*.bmp'),
            ('All files', '*.*')
        ]
        try:
            file_path = filedialog.askopenfilename(
                title="Pilih Gambar",
                filetypes=file_types
            )
            if not file_path:
                return

            print(f"Memuat gambar dari: {file_path}")
            file_path = self.fix_onedrive_path(file_path)
            self.img_cv = cv2.imread(file_path)

            if self.img_cv is None:
                try:
                    with Image.open(file_path) as img_pil:
                        self.img_cv = cv2.cvtColor(np.array(img_pil), cv2.COLOR_RGB2BGR)
                    print("Gambar dimuat menggunakan PIL")
                except Exception as pil_error:
                    error_msg = f"Gagal memuat gambar:\n{file_path}\nError: {str(pil_error)}"
                    messagebox.showerror("Error Memuat Gambar", error_msg)
                    return

            self.original_img = self.img_cv.copy()
            self.result_img = self.img_cv.copy()
            self.dashboard()
            self.display_image(self.img_cv, self.image_label)

        except Exception as e:
            error_msg = f"Terjadi kesalahan sistem:\n{str(e)}"
            messagebox.showerror("Error Sistem", error_msg)

    def display_image(self, img_cv, label):
        try:
            if img_cv is None:
                raise ValueError("Gambar tidak valid (None)")

            if len(img_cv.shape) == 2:
                img_rgb = cv2.cvtColor(img_cv, cv2.COLOR_GRAY2RGB)
            else:
                img_rgb = cv2.cvtColor(img_cv, cv2.COLOR_BGR2RGB)

            img_pil = Image.fromarray(img_rgb)
            width, height = img_pil.size
            max_size = (800, 600)
            if width > max_size[0] or height > max_size[1]:
                ratio = min(max_size[0]/width, max_size[1]/height)
                new_size = (int(width*ratio), int(height*ratio))
                img_pil = img_pil.resize(new_size, Image.LANCZOS)

            img_tk = ImageTk.PhotoImage(img_pil)
            label.configure(image=img_tk)
            label.image = img_tk
            self.result_img = img_cv

        except Exception as e:
            messagebox.showerror("Error Display", f"Gagal menampilkan gambar: {str(e)}")

    def start_screen(self):
        for widget in self.frame.winfo_children():
            widget.destroy()

        intro_label = tk.Label(
            self.frame,
            text="Selamat datang di Aplikasi Pengolahan Citra Sederhana\nKlik 'Input Image' dan rasakan kemudahannya.",
            font=("Helvetica", 14),
            justify="center"
        )
        intro_label.pack(pady=40)

        input_btn = tb.Button(
            self.frame,
            text="Input Image",
            bootstyle="primary",
            command=self.load_image
        )
        input_btn.pack()

    def dashboard(self):
        for widget in self.frame.winfo_children():
            widget.destroy()

        top_label = tk.Label(
            self.frame,
            text="Satu Aplikasi Banyak Solusi Gambar",
            font=("Helvetica", 16, "bold"),
            fg="#007BFF"
        )
        top_label.pack(pady=20)

        self.image_label = tk.Label(self.frame)
        self.image_label.pack(pady=5)

        self.result_label = tk.Label(self.frame)
        self.result_label.pack(pady=5)

        self.download_btn = tb.Button(
            self.frame,
            text="Download Gambar",
            bootstyle="success",
            command=self.save_result
        )
        self.download_btn.pack(pady=5)

        btn_frame = tk.Frame(self.frame)
        btn_frame.pack(pady=10)

        buttons = [
            ("Gambar Asli", self.show_original),
            ("Grayscale", self.to_grayscale),
            ("Biner", self.to_binary),
            ("Tambah Terang", self.brightness_increase),
            ("Operasi NOT", self.logic_not),
            ("Histogram", self.histogram),
            ("Sharpen", self.sharpen),
            ("Morfologi (Dilasi)", self.morphology)
        ]

        for i, (label, func) in enumerate(buttons):
            b = tb.Button(
                btn_frame,
                text=label,
                bootstyle="primary",
                command=func,
                width=25
            )
            b.grid(row=i//2, column=i%2, padx=10, pady=5)

    def save_result(self):
        """Menyimpan gambar hasil"""
        if hasattr(self, 'result_img') and self.result_img is not None:
            file_types = [
                ('PNG files', '*.png'),
                ('JPEG files', '*.jpg'),
                ('All files', '*.*')
            ]
            file_path = filedialog.asksaveasfilename(
                defaultextension=".png",
                filetypes=file_types,
                title="Simpan Gambar Hasil"
            )

            if file_path:
                # Pastikan path memiliki ekstensi valid
                valid_exts = ['.png', '.jpg', '.jpeg', '.bmp']
                ext = os.path.splitext(file_path)[1].lower()
                if ext not in valid_exts:
                    file_path += '.png'

                try:
                    print("Menyimpan ke:", file_path)
                    print("Tipe gambar:", type(self.result_img))
                    print("Ukuran gambar:", self.result_img.shape)

                    success = cv2.imwrite(file_path, self.result_img)
                    if success:
                        messagebox.showinfo("Sukses", f"Gambar berhasil disimpan di:\n{file_path}")
                    else:
                        messagebox.showerror("Error", "Gagal menyimpan gambar (cv2.imwrite mengembalikan False)")
                except Exception as e:
                    messagebox.showerror("Error", f"Gagal menyimpan gambar:\n{str(e)}")
            else:
                print("Dialog simpan dibatalkan oleh pengguna.")
        else:
            messagebox.showwarning("Peringatan", "Tidak ada gambar hasil yang bisa disimpan")

    # ===== Fungsi Operasi =====
    def show_original(self):
        if self.original_img is not None:
            self.display_image(self.original_img, self.result_label)

    def to_grayscale(self):
        if self.img_cv is not None:
            gray = convert_to_grayscale(self.img_cv)
            self.display_image(gray, self.result_label)

    def to_binary(self):
        if self.img_cv is not None:
            binary = convert_to_binary(self.img_cv)
            self.display_image(binary, self.result_label)

    def brightness_increase(self):
        if self.img_cv is not None:
            bright = cv2.add(self.img_cv, np.full(self.img_cv.shape, 30, dtype=np.uint8))
            self.display_image(bright, self.result_label)

    def logic_not(self):
        if self.img_cv is not None:
            not_img = apply_not(self.img_cv)
            self.display_image(not_img, self.result_label)

    def histogram(self):
        if self.img_cv is not None:
            show_histogram(self.img_cv)

    def sharpen(self):
        if self.img_cv is not None:
            sharp = apply_sharpening(self.img_cv)
            self.display_image(sharp, self.result_label)

    def morphology(self):
        if self.img_cv is not None:
            gray = cv2.cvtColor(self.img_cv, cv2.COLOR_BGR2GRAY)
            _, binary = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)

            se1 = np.array([[1,1,1],[1,1,1],[1,1,1]], dtype=np.uint8)
            se2 = np.array([[0,0,0],[1,1,1],[0,0,0]], dtype=np.uint8)

            morphed1 = cv2.dilate(binary, se1, iterations=1)
            morphed2 = cv2.dilate(binary, se2, iterations=1)

            morphed1_bgr = cv2.cvtColor(morphed1, cv2.COLOR_GRAY2BGR)
            morphed2_bgr = cv2.cvtColor(morphed2, cv2.COLOR_GRAY2BGR)

            cv2.putText(morphed1_bgr, 'SE: Penuh (Kotak)', (10, 25),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2, cv2.LINE_AA)

            cv2.putText(morphed2_bgr, 'SE: Horizontal', (10, 25),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 0), 2, cv2.LINE_AA)

            combined = np.hstack((morphed1_bgr, morphed2_bgr))
            self.display_image(combined, self.result_label)

if __name__ == '__main__':
    root = tb.Window(themename="cosmo")
    app = ImageApp(root)
    root.mainloop()
