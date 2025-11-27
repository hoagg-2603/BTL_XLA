import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
from processors import ImageProcessor

class AppGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Công Cụ Xử Lý Ảnh Số - Nhóm ...")
        self.root.geometry("1280x720")
        
        # Khởi tạo bộ xử lý logic
        self.processor = ImageProcessor()
        
        # Biến lưu trữ ảnh
        self.original_image = None
        self.processed_image = None

        # --- GIAO DIỆN CHÍNH ---
        
        # 1. Thanh công cụ phía trên (Toolbar)
        self.create_toolbar()

        # 2. Khu vực chính (Chia cột trái/phải)
        self.main_frame = tk.Frame(self.root)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Cột Trái: Bảng Điều Khiển
        self.create_control_panel()

        # Cột Phải: Hiển thị Ảnh
        self.create_display_panel()

    def create_toolbar(self):
        toolbar = tk.Frame(self.root, bd=1, relief=tk.RAISED, bg="#e1e1e1")
        toolbar.pack(side=tk.TOP, fill=tk.X)

        # Nút Tải Ảnh
        btn_load = tk.Button(toolbar, text="📂 Tải Ảnh / CSV", command=self.load_file, 
                             bg="white", font=("Arial", 10))
        btn_load.pack(side=tk.LEFT, padx=5, pady=5)

        # Nút Lưu Ảnh
        btn_save = tk.Button(toolbar, text="💾 Lưu Kết Quả", command=self.save_file, 
                             bg="white", font=("Arial", 10))
        btn_save.pack(side=tk.LEFT, padx=5, pady=5)

    def create_control_panel(self):
        # Tạo khung chứa các nút điều khiển bên trái
        control_frame = tk.Frame(self.main_frame, width=320)
        control_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))

        # --- NHÓM 1: LÀM MỊN ẢNH (SMOOTHING) ---
        group_smooth = tk.LabelFrame(control_frame, text="1. Làm Mịn & Khử Nhiễu", 
                                     font=("Arial", 10, "bold"), fg="blue", padx=10, pady=10)
        group_smooth.pack(fill=tk.X, pady=(0, 15))

        # Slider chọn Kernel Size
        tk.Label(group_smooth, text="Kích thước Kernel:").pack(anchor="w")
        self.kernel_var = tk.IntVar(value=3)
        self.scale_kernel = tk.Scale(group_smooth, from_=3, to=15, resolution=2, 
                                     orient=tk.HORIZONTAL, variable=self.kernel_var)
        self.scale_kernel.pack(fill=tk.X, pady=(0, 10))

        # Các nút chức năng
        tk.Button(group_smooth, text="Mean Filter", command=self.on_mean).pack(fill=tk.X, pady=2)
        tk.Button(group_smooth, text="Gaussian Filter", command=self.on_gaussian).pack(fill=tk.X, pady=2)
        tk.Button(group_smooth, text="Median Filter", command=self.on_median).pack(fill=tk.X, pady=2)


        # --- NHÓM 2: PHÁT HIỆN BIÊN (EDGE DETECTION) ---
        group_edge = tk.LabelFrame(control_frame, text="2. Phát Hiện Biên", 
                                   font=("Arial", 10, "bold"), fg="red", padx=10, pady=10)
        group_edge.pack(fill=tk.X)

        # Slider chọn Ngưỡng (Threshold)
        tk.Label(group_edge, text="Ngưỡng Lọc (Threshold):").pack(anchor="w")
        tk.Label(group_edge, text="(0 = Xem độ lớn biên gốc)", font=("Arial", 8, "italic"), fg="gray").pack(anchor="w")
        
        self.thresh_var = tk.IntVar(value=0) # Mặc định 0
        self.scale_thresh = tk.Scale(group_edge, from_=0, to=255, 
                                     orient=tk.HORIZONTAL, variable=self.thresh_var)
        self.scale_thresh.pack(fill=tk.X, pady=(0, 10))

        # Các nút chức năng
        tk.Button(group_edge, text="Sobel", command=self.on_sobel).pack(fill=tk.X, pady=2)
        tk.Button(group_edge, text="Prewitt", command=self.on_prewitt).pack(fill=tk.X, pady=2)
        tk.Button(group_edge, text="Laplacian", command=self.on_laplacian).pack(fill=tk.X, pady=2)

    def create_display_panel(self):
        display_frame = tk.Frame(self.main_frame)
        display_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        # Khung Ảnh Gốc
        self.panel_origin = tk.LabelFrame(display_frame, text="Ảnh Gốc (Original)")
        self.panel_origin.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)
        
        self.lbl_img_origin = tk.Label(self.panel_origin, text="[Chưa tải ảnh]", bg="#f0f0f0")
        self.lbl_img_origin.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Khung Ảnh Kết Quả
        self.panel_result = tk.LabelFrame(display_frame, text="Kết Quả Xử Lý (Result)")
        self.panel_result.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5)
        
        self.lbl_img_result = tk.Label(self.panel_result, text="[Chưa có kết quả]", bg="#f0f0f0")
        self.lbl_img_result.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

    # --- CÁC HÀM XỬ LÝ SỰ KIỆN ---

    def load_file(self):
        file_path = filedialog.askopenfilename(filetypes=[
            ("Image Files", "*.jpg;*.png;*.jpeg;*.bmp"),
            ("CSV Files", "*.csv"),
            ("All Files", "*.*")
        ])
        if file_path:
            try:
                # Gọi hàm load từ processor
                self.original_image = self.processor.load_image(file_path)
                self.processed_image = self.original_image.copy() # Reset kết quả
                
                # Hiển thị
                self.show_image(self.original_image, self.lbl_img_origin)
                self.show_image(self.processed_image, self.lbl_img_result)
            except Exception as e:
                messagebox.showerror("Lỗi Tải Ảnh", str(e))

    def save_file(self):
        if self.processed_image is None:
            messagebox.showwarning("Cảnh báo", "Chưa có ảnh kết quả để lưu!")
            return
        
        file_path = filedialog.asksaveasfilename(
            defaultextension=".jpg",
            filetypes=[("JPEG", "*.jpg"), ("PNG", "*.png"), ("CSV", "*.csv")]
        )
        
        if file_path:
            try:
                # Gọi hàm save từ processor (đã fix lỗi tiếng Việt)
                self.processor.save_image(self.processed_image, file_path)
                messagebox.showinfo("Thành công", f"Đã lưu ảnh tại:\n{file_path}")
            except Exception as e:
                messagebox.showerror("Lỗi Lưu Ảnh", str(e))

    def show_image(self, img_array, label_widget):
        if img_array is None: return
        
        # Resize ảnh thông minh để vừa khung hình
        h, w = img_array.shape[:2]
        display_h = 550 # Chiều cao tối đa hiển thị
        
        if h > display_h:
            scale = display_h / h
            display_w = int(w * scale)
            display_h = int(h * scale)
        else:
            display_w = w
            display_h = h
        
        # Convert NumPy -> PIL -> ImageTk
        img_pil = Image.fromarray(img_array)
        img_pil = img_pil.resize((display_w, display_h), Image.Resampling.LANCZOS)
        img_tk = ImageTk.PhotoImage(img_pil)
        
        label_widget.config(image=img_tk, text="")
        label_widget.image = img_tk # Giữ tham chiếu

    def check_image_loaded(self):
        if self.original_image is None:
            messagebox.showwarning("Cảnh báo", "Vui lòng tải ảnh trước!")
            return False
        return True

    # --- SỰ KIỆN NHÓM LÀM MỊN ---
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

    # --- SỰ KIỆN NHÓM BIÊN (CẬP NHẬT THÊM THRESHOLD) ---
    def on_sobel(self):
        if self.check_image_loaded():
            # Lấy giá trị ngưỡng từ thanh trượt
            t = self.thresh_var.get()
            self.processed_image = self.processor.apply_sobel(self.original_image, threshold=t)
            self.show_image(self.processed_image, self.lbl_img_result)

    def on_prewitt(self):
        if self.check_image_loaded():
            t = self.thresh_var.get()
            self.processed_image = self.processor.apply_prewitt(self.original_image, threshold=t)
            self.show_image(self.processed_image, self.lbl_img_result)

    def on_laplacian(self):
        if self.check_image_loaded():
            t = self.thresh_var.get()
            self.processed_image = self.processor.apply_laplacian(self.original_image, threshold=t)
            self.show_image(self.processed_image, self.lbl_img_result)