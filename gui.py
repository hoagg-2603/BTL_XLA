import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from PIL import Image, ImageTk
from processors import ImageProcessor

class AppGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Công Cụ Xử Lý Ảnh Số - Nhóm ...")
        self.root.geometry("1200x700")
        
        # Khởi tạo bộ xử lý
        self.processor = ImageProcessor()
        self.original_image = None
        self.processed_image = None

        # --- GIAO DIỆN CHÍNH ---
        # 1. Thanh công cụ (Toolbar)
        self.create_toolbar()

        # 2. Khu vực chính (Main Area)
        self.main_frame = tk.Frame(self.root)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Cột trái: Điều khiển (Controls)
        self.create_control_panel()

        # Cột phải: Hiển thị ảnh (Display)
        self.create_display_panel()

    def create_toolbar(self):
        toolbar = tk.Frame(self.root, bd=1, relief=tk.RAISED)
        toolbar.pack(side=tk.TOP, fill=tk.X)

        btn_load = tk.Button(toolbar, text="📂 Tải Ảnh/CSV", command=self.load_file)
        btn_load.pack(side=tk.LEFT, padx=2, pady=2)

        btn_save = tk.Button(toolbar, text="💾 Lưu Kết Quả", command=self.save_file)
        btn_save.pack(side=tk.LEFT, padx=2, pady=2)

    def create_control_panel(self):
        control_frame = tk.LabelFrame(self.main_frame, text="Bảng Điều Khiển", width=300)
        control_frame.pack(side=tk.LEFT, fill=tk.Y, padx=5)

        # Nhóm 1: Làm mịn ảnh
        lbl_smooth = tk.Label(control_frame, text="--- Làm Mịn Ảnh ---", fg="blue", font=("Arial", 10, "bold"))
        lbl_smooth.pack(pady=(10, 5))

        # Slider chọn Kernel Size (Tham số nâng cao)
        self.kernel_var = tk.IntVar(value=3)
        tk.Label(control_frame, text="Kích thước Kernel:").pack()
        # Chỉ cho phép số lẻ: 3, 5, 7, 9...
        self.scale_kernel = tk.Scale(control_frame, from_=3, to=15, resolution=2, orient=tk.HORIZONTAL, variable=self.kernel_var)
        self.scale_kernel.pack(fill=tk.X, padx=10)

        tk.Button(control_frame, text="Mean Filter", command=self.on_mean).pack(fill=tk.X, padx=10, pady=2)
        tk.Button(control_frame, text="Gaussian Filter", command=self.on_gaussian).pack(fill=tk.X, padx=10, pady=2)
        tk.Button(control_frame, text="Median Filter", command=self.on_median).pack(fill=tk.X, padx=10, pady=2)

        # Nhóm 2: Phát hiện biên
        lbl_edge = tk.Label(control_frame, text="--- Phát Hiện Biên ---", fg="red", font=("Arial", 10, "bold"))
        lbl_edge.pack(pady=(20, 5))

        tk.Button(control_frame, text="Sobel", command=self.on_sobel).pack(fill=tk.X, padx=10, pady=2)
        tk.Button(control_frame, text="Prewitt", command=self.on_prewitt).pack(fill=tk.X, padx=10, pady=2)
        tk.Button(control_frame, text="Laplacian", command=self.on_laplacian).pack(fill=tk.X, padx=10, pady=2)

    def create_display_panel(self):
        display_frame = tk.Frame(self.main_frame)
        display_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        # Khung ảnh gốc
        self.panel_origin = tk.LabelFrame(display_frame, text="Ảnh Gốc")
        self.panel_origin.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)
        self.lbl_img_origin = tk.Label(self.panel_origin, text="Chưa tải ảnh")
        self.lbl_img_origin.pack(expand=True)

        # Khung ảnh kết quả
        self.panel_result = tk.LabelFrame(display_frame, text="Kết Quả Xử Lý")
        self.panel_result.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5)
        self.lbl_img_result = tk.Label(self.panel_result, text="Chưa có kết quả")
        self.lbl_img_result.pack(expand=True)

    # --- CÁC HÀM SỰ KIỆN (CALLBACKS) ---
    def load_file(self):
        file_path = filedialog.askopenfilename(filetypes=[
            ("Image Files", "*.jpg;*.png;*.jpeg;*.bmp"),
            ("CSV Files", "*.csv"),
            ("All Files", "*.*")
        ])
        if file_path:
            try:
                self.original_image = self.processor.load_image(file_path)
                self.processed_image = self.original_image.copy() # Reset kết quả
                self.show_image(self.original_image, self.lbl_img_origin)
                self.show_image(self.processed_image, self.lbl_img_result)
            except Exception as e:
                messagebox.showerror("Lỗi", str(e))

    def save_file(self):
        if self.processed_image is None:
            messagebox.showwarning("Cảnh báo", "Chưa có ảnh kết quả để lưu!")
            return
        
        # Hộp thoại lưu file
        file_path = filedialog.asksaveasfilename(
            defaultextension=".jpg",
            filetypes=[("JPEG", "*.jpg"), ("PNG", "*.png"), ("CSV", "*.csv")]
        )
        
        if file_path:
            try:
                # Gọi hàm save bên processor (đã sửa ở trên)
                self.processor.save_image(self.processed_image, file_path)
                messagebox.showinfo("Thành công", f"Đã lưu ảnh tại:\n{file_path}")
            except Exception as e:
                messagebox.showerror("Lỗi", f"Không thể lưu ảnh!\nChi tiết: {str(e)}")

    def show_image(self, img_array, label_widget):
        """Hiển thị ảnh numpy array lên Tkinter Label"""
        if img_array is None: return
        
        # Resize ảnh để vừa khung hình hiển thị (giữ tỉ lệ)
        h, w = img_array.shape[:2]
        display_h = 500
        scale = display_h / h
        display_w = int(w * scale)
        
        # Convert sang định dạng PIL
        img_pil = Image.fromarray(img_array)
        img_pil = img_pil.resize((display_w, display_h))
        img_tk = ImageTk.PhotoImage(img_pil)
        
        label_widget.config(image=img_tk, text="")
        label_widget.image = img_tk # Giữ tham chiếu để không bị Garbage Collection xóa

    # --- SỰ KIỆN NÚT BẤM ---
    def check_image_loaded(self):
        if self.original_image is None:
            messagebox.showwarning("Cảnh báo", "Vui lòng tải ảnh trước!")
            return False
        return True

    def on_mean(self):
        if self.check_image_loaded():
            k = self.kernel_var.get()
            self.processed_image = self.processor.apply_mean_filter(self.original_image, k)
            self.show_image(self.processed_image, self.lbl_img_result)

    def on_gaussian(self):
        if self.check_image_loaded():
            k = self.kernel_var.get()
            self.processed_image = self.processor.apply_gaussian_filter(self.original_image, k)
            self.show_image(self.processed_image, self.lbl_img_result)

    def on_median(self):
        if self.check_image_loaded():
            k = self.kernel_var.get()
            self.processed_image = self.processor.apply_median_filter(self.original_image, k)
            self.show_image(self.processed_image, self.lbl_img_result)

    def on_sobel(self):
        if self.check_image_loaded():
            self.processed_image = self.processor.apply_sobel(self.original_image)
            self.show_image(self.processed_image, self.lbl_img_result)

    def on_prewitt(self):
        if self.check_image_loaded():
            self.processed_image = self.processor.apply_prewitt(self.original_image)
            self.show_image(self.processed_image, self.lbl_img_result)

    def on_laplacian(self):
        if self.check_image_loaded():
            self.processed_image = self.processor.apply_laplacian(self.original_image)
            self.show_image(self.processed_image, self.lbl_img_result)