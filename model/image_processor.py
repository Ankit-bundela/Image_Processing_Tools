from PIL import Image, ImageEnhance, ImageOps
from PIL import ImageFilter
import os
import cv2
import numpy as np


class ImageProcessor:
    def __init__(self, image_path):
        self.image_path = image_path
        self.image_data = Image.open(image_path).convert("RGB")
        self.cv_image = cv2.imread(image_path)

        # Ensure output folder exists
        if not os.path.exists("icons/images"):
            os.makedirs("icons/images")

    def apply_brightness(self, value):
        enhancer = ImageEnhance.Brightness(self.image_data)
        img = enhancer.enhance(value / 128)
        output_file = "icons/images/brightness.jpg"
        img.save(output_file)
        self.image_data = img
        return output_file

    def apply_grayscale(self):
        img = ImageOps.grayscale(self.image_data).convert("RGB")
        output_file = "icons/images/grayscale.jpg"
        img.save(output_file)
        self.image_data = img
        return output_file

    def apply_contrast(self, contrast_val):
        enhancer = ImageEnhance.Contrast(self.image_data)
        img = enhancer.enhance(contrast_val / 128)
        output_file = "icons/images/contrast.jpg"
        img.save(output_file)
        self.image_data = img
        return output_file

    def zoom_in(self, scale=1.2):
        w, h = self.image_data.size
        new_size = (int(w * scale), int(h * scale))
        img = self.image_data.resize(new_size, Image.LANCZOS)
        output_file = "icons/images/zoom_in.jpg"
        img.save(output_file)
        self.image_data = img
        return output_file

    def zoom_out(self, scale=0.8):
        w, h = self.image_data.size
        new_size = (int(w * scale), int(h * scale))
        img = self.image_data.resize(new_size, Image.LANCZOS)
        output_file = "icons/images/zoom_out.jpg"
        img.save(output_file)
        self.image_data = img
        return output_file

    def rotate(self, angle):
        img = self.image_data.rotate(angle, expand=True)
        output_file = "icons/images/rotated.jpg"
        img.save(output_file)
        self.image_data = img
        return output_file

    def flip(self, direction):
        if direction == "horizontal":
            img = self.image_data.transpose(Image.FLIP_LEFT_RIGHT)
        elif direction == "vertical":
            img = self.image_data.transpose(Image.FLIP_TOP_BOTTOM)
        else:
            raise ValueError("Invalid direction")
        output_file = "icons/images/flipped.jpg"
        img.save(output_file)
        self.image_data = img
        return output_file


    def apply_median(self):
        out_path = "icons/images/median_filter.png"
        median = cv2.medianBlur(self.cv_image, 5)
        cv2.imwrite(out_path, median)
        return out_path

    def apply_fourier(self):
        out_path = "icons/images/fourier_transform.png"
        img_gray = cv2.cvtColor(self.cv_image, cv2.COLOR_BGR2GRAY)
        dft = cv2.dft(np.float32(img_gray), flags=cv2.DFT_COMPLEX_OUTPUT)
        dft_shift = np.fft.fftshift(dft)
        magnitude_spectrum = 20 * np.log(
            cv2.magnitude(dft_shift[:, :, 0], dft_shift[:, :, 1]) + 1
        )
        # Normalize to 0-255
        magnitude_spectrum = cv2.normalize(magnitude_spectrum, None, 0, 255, cv2.NORM_MINMAX)
        magnitude_spectrum = np.uint8(magnitude_spectrum)
        cv2.imwrite(out_path, magnitude_spectrum)
        return out_path
    
    def apply_mean(self, strength=1):
        img = self.image_data.copy()  # use existing loaded image
        for _ in range(strength):
            img = img.filter(ImageFilter.BoxBlur(1))
        output = "icons/images/mean_output.png"
        img.save(output)
        self.image_data = img  # update current image
        return output
    
    def apply_gaussian(self, sigma=1.0):
        img = Image.open(self.image_path)
        img = img.filter(ImageFilter.GaussianBlur(radius=sigma))
        output = "icons/images/gaussian_output.png"
        img.save(output)
        return output
    
    def apply_unsharp(self, amount=1.0):
        img = self.image_data.copy()
        img = img.filter(ImageFilter.UnsharpMask(radius=2, percent=int(amount * 100), threshold=3))
        output = "icons/images/unsharp_output.png"
        img.save(output)
        self.image_data = img
        return output    
    def apply_laplacian(self):
        out_path = "icons/images/laplacian.png"
        img_gray = cv2.cvtColor(self.cv_image, cv2.COLOR_BGR2GRAY)
        laplacian = cv2.Laplacian(img_gray, cv2.CV_64F)
        laplacian = cv2.convertScaleAbs(laplacian)
        cv2.imwrite(out_path, laplacian)
        return out_path
