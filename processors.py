import cv2
import numpy as np
import os

class ImageProcessor:
    def __init__(self):
        pass
    def _manual_convolution(self, image, kernel):
        h_img, w_img = image.shape[:2]
        k_height, k_width = kernel.shape
        pad_h = k_height // 2
        pad_w = k_width // 2
        
        if len(image.shape) == 3:
            image_padded = np.pad(image, ((pad_h, pad_h), (pad_w, pad_w), (0, 0)), mode='edge')
            output = np.zeros_like(image, dtype=np.float32)
        else:
            image_padded = np.pad(image, ((pad_h, pad_h), (pad_w, pad_w)), mode='edge')
            output = np.zeros_like(image, dtype=np.float32)

        kernel = np.flip(kernel)

        for i in range(k_height):
            for j in range(k_width):
                weight = kernel[i, j]
                if len(image.shape) == 3:
                    region = image_padded[i : i + h_img, j : j + w_img, :]
                else:
                    region = image_padded[i : i + h_img, j : j + w_img]
                output += region * weight

        return np.clip(output, 0, 255).astype(np.uint8)

    
    def load_image(self, file_path):
        if file_path.endswith('.csv'):
            try:
                data = np.genfromtxt(file_path, delimiter=',')
                if data.max() != data.min():
                    data = ((data - data.min()) / (data.max() - data.min()) * 255)
                data = data.astype(np.uint8)
                return cv2.cvtColor(data, cv2.COLOR_GRAY2RGB)
            except:
                return np.zeros((300, 300, 3), dtype=np.uint8)
        else:
            try:
                # Fix lỗi đọc đường dẫn tiếng Việt
                stream = np.fromfile(file_path, dtype=np.uint8)
                img = cv2.imdecode(stream, cv2.IMREAD_COLOR)
                if img is None: raise ValueError("File lỗi")
                return cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            except Exception as e:
                raise ValueError(f"Lỗi đọc ảnh: {e}")

    def save_image(self, image, file_path):
        try:
            # 1. Lưu CSV
            if file_path.endswith('.csv'):
                if len(image.shape) == 3:
                    gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
                else:
                    gray = image
                np.savetxt(file_path, gray, delimiter=",", fmt='%d')

            else:
                # Chuyển về BGR
                img_bgr = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
                
                # Lấy đuôi file (jpg, png)
                ext = os.path.splitext(file_path)[1]
                if not ext: ext = ".jpg"

                # Mã hóa thành dòng byte
                success, encoded_img = cv2.imencode(ext, img_bgr)
                
                if success:
                    # Ghi dòng byte xuống file (Hỗ trợ tốt tiếng Việt)
                    with open(file_path, "wb") as f:
                        f.write(encoded_img)
                else:
                    raise ValueError("Không mã hóa được ảnh.")
                    
        except Exception as e:
            print(f"Lỗi save: {e}")
            raise e

    def apply_mean_filter(self, image, kernel_size):
        if kernel_size % 2 == 0: kernel_size += 1
        kernel = np.ones((kernel_size, kernel_size), dtype=np.float32)
        kernel /= (kernel_size * kernel_size)
        return self._manual_convolution(image, kernel)

    def apply_gaussian_filter(self, image, kernel_size):
        if kernel_size % 2 == 0: kernel_size += 1
        sigma = 0.3 * ((kernel_size - 1) * 0.5 - 1) + 0.8
        ax = np.linspace(-(kernel_size - 1) / 2., (kernel_size - 1) / 2., kernel_size)
        gauss = np.exp(-0.5 * np.square(ax) / np.square(sigma))
        kernel = np.outer(gauss, gauss)
        kernel /= np.sum(kernel)
        return self._manual_convolution(image, kernel)

    def apply_median_filter(self, image, kernel_size):
        if kernel_size % 2 == 0: kernel_size += 1
        pad = kernel_size // 2
        if len(image.shape) == 3:
            img_pad = np.pad(image, ((pad, pad), (pad, pad), (0,0)), 'edge')
        else:
            img_pad = np.pad(image, ((pad, pad), (pad, pad)), 'edge')
            
        from numpy.lib.stride_tricks import sliding_window_view
        
        if len(image.shape) == 3:
            output = np.zeros_like(image)
            for c in range(3):
                windows = sliding_window_view(img_pad[:,:,c], window_shape=(kernel_size, kernel_size))
                output[:,:,c] = np.median(windows, axis=(2, 3))
        else:
            windows = sliding_window_view(img_pad, window_shape=(kernel_size, kernel_size))
            output = np.median(windows, axis=(2, 3))
        return output.astype(np.uint8)

    def _prepare_gray(self, image):
        if len(image.shape) == 3:
            return cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
        return image

    def apply_sobel(self, image):
        gray = self._prepare_gray(image)
        Gx = np.array([[-1, 0, 1], [-2, 0, 2], [-1, 0, 1]], dtype=np.float32)
        Gy = np.array([[-1, -2, -1], [0, 0, 0], [1, 2, 1]], dtype=np.float32)
        val_x = self._manual_convolution(gray, Gx)
        val_y = self._manual_convolution(gray, Gy)
        combined = cv2.addWeighted(np.abs(val_x), 0.5, np.abs(val_y), 0.5, 0)
        return cv2.cvtColor(combined.astype(np.uint8), cv2.COLOR_GRAY2RGB)

    def apply_prewitt(self, image):
        gray = self._prepare_gray(image)
        Kx = np.array([[-1, 0, 1], [-1, 0, 1], [-1, 0, 1]], dtype=np.float32)
        Ky = np.array([[-1, -1, -1], [0, 0, 0], [1, 1, 1]], dtype=np.float32)
        val_x = self._manual_convolution(gray, Kx)
        val_y = self._manual_convolution(gray, Ky)
        combined = cv2.addWeighted(np.abs(val_x), 0.5, np.abs(val_y), 0.5, 0)
        return cv2.cvtColor(combined.astype(np.uint8), cv2.COLOR_GRAY2RGB)

    def apply_laplacian(self, image):
        gray = self._prepare_gray(image)
        K = np.array([[0, 1, 0], [1, -4, 1], [0, 1, 0]], dtype=np.float32)
        val = self._manual_convolution(gray, K)
        return cv2.cvtColor(val, cv2.COLOR_GRAY2RGB)