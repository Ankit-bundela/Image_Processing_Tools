import os
import tkinter as tk
import cv2
from PIL import Image

import tkinter as tk
from PIL import Image, ImageTk


from tkinter import filedialog, colorchooser
from PIL import Image, ImageTk, ImageEnhance
import ctypes
from model.image_processor import ImageProcessor
from PIL import ImageFilter

class LoadingScreen(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Loading...")
        new_width = 500
        new_height = 260
        self.geometry(f"{new_width}x{new_height}")
        self.resizable(False, False)
        # Center the window
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x = (screen_width - new_width) // 2
        y = (screen_height - new_height) // 2
        self.geometry(f"{new_width}x{new_height}+{x}+{y}")

        self.loading_label = tk.Label(self)
        self.loading_label.pack(expand=True)

        self.gif_frames = []
        self.load_gif("icons/loading.gif")  # Make sure the path is correct
        self.current_frame = 0
        self.animate()

    def load_gif(self, gif_path):
        try:
            gif = Image.open(gif_path)
            while True:
                frame = ImageTk.PhotoImage(gif.copy())
                self.gif_frames.append(frame)
                gif.seek(len(self.gif_frames))  # Move to the next frame
        except EOFError:
            pass

    def animate(self):
        if self.gif_frames:
            self.loading_label.config(image=self.gif_frames[self.current_frame])
            self.current_frame = (self.current_frame + 1) % len(self.gif_frames)
            self.after_id=self.after(100, self.animate)  # Adjust speed if needed

class MainWindow(tk.Tk):
    def __init__(self):
        super().__init__()
        width, height = ctypes.windll.user32.GetSystemMetrics(0), ctypes.windll.user32.GetSystemMetrics(1)
        self.desktopWidth = width
        self.desktopHeight = height
        self.title("IMagic")
        self.geometry(f"{self.desktopWidth}x{self.desktopHeight}+0+0")
        self.state("zoomed")
        self.resizable(True, True)
        self.dark_mode = False
        os.makedirs("images", exist_ok=True)

        # Menus
        self.menuBar = tk.Menu(self)
        self.config(menu=self.menuBar)
        self._create_menus()
        # Toolbar
        self.toolBar = tk.Frame(self, relief=tk.RAISED, bd=1)
        self.toolBar.pack(side=tk.TOP, fill=tk.X)
        self._add_toolbar_buttons()

        # Main Container
        self.mainFrame = tk.Frame(self)
        self.mainFrame.pack(fill=tk.BOTH, expand=True)

        # Canvas
        self.imageContainerFrame = tk.Frame(self.mainFrame, bd=1)
        self.imageContainerFrame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.canvas = tk.Canvas(self.imageContainerFrame, bg="white" )
        self.canvas.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        # Sidebar Frame (initially hidden)
        self.sidebar = tk.Frame(self.mainFrame, width=300, bd=1, relief=tk.GROOVE)
        # Mouse crop
        self.canvas.bind("<ButtonPress-1>", self._on_press)
        self.canvas.bind("<B1-Motion>", self._on_drag)
        self.canvas.bind("<ButtonRelease-1>", self._on_release)

        self.imageFileName = None
        self.processor = None
        self.zoomFactor = 1.0
        self.undoImage = None
        self.originalImage = None  # For reset
        self.x = None
        self.y = None
        self.rect_id = None

    def _create_menus(self):
        self.fileMenu = tk.Menu(self.menuBar, tearoff=0)
        self.fileMenu.add_command(label="New")
        self.fileMenu.add_command(label="Open", command=self._open_image)
        self.fileMenu.add_command(label="Close", command=self.quit)
        self.fileMenu.add_command(label="Save", command=self._save_image)
        self.fileMenu.add_command(label="Save as", command=self._save_as)
        self.fileMenu.add_separator()
        self.fileMenu.add_command(label="Exit", command=self.quit)
        self.menuBar.add_cascade(label="File", menu=self.fileMenu)

        self.editMenu = tk.Menu(self.menuBar, tearoff=0)
        self.editMenu.add_command(label="Undo", command=self._undo)
        self.menuBar.add_cascade(label="Edit", menu=self.editMenu)

        self.viewMenu = tk.Menu(self.menuBar, tearoff=0)
        self.viewMenu.add_command(label="Zoom in", command=self._zoom_in)
        self.viewMenu.add_command(label="Zoom out", command=self._zoom_out)
        self.menuBar.add_cascade(label="View", menu=self.viewMenu)
        self.viewMenu.add_separator()
        self.viewMenu.add_command(label="Toggle Dark Mode", command=self._toggle_dark_mode)

        self.transformMenu = tk.Menu(self.menuBar, tearoff=0)
        self.transformMenu.add_command(label="Rotate 90°", command=lambda: self._rotate_image(90))
        self.transformMenu.add_command(label="Rotate -90°", command=lambda: self._rotate_image(-90))
        self.transformMenu.add_command(label="Rotate 180°", command=lambda: self._rotate_image(180))
        self.transformMenu.add_command(label="Flip Horizontal", command=lambda: self._flip_image('horizontal'))
        self.transformMenu.add_command(label="Flip Vertical", command=lambda: self._flip_image('vertical'))
        self.menuBar.add_cascade(label="Transform", menu=self.transformMenu)

        self.filterMenu = tk.Menu(self.menuBar, tearoff=0)
        self.filterMenu.add_command(label="Brightness", command=self._brightness)
        self.filterMenu.add_command(label="Contrast", command=self._contrast)
        self.filterMenu.add_command(label="Grayscale", command=self._grayscale)
        self.filterMenu.add_separator()
        self.filterMenu.add_command(label="Mean", command=self._mean_filter)
        self.filterMenu.add_command(label="Median", command=self._median_filter)
        self.filterMenu.add_command(label="Fourier Transform", command=self._fourier_transform)
        self.filterMenu.add_command(label="Gaussian Smoothing", command=self._gaussian_smoothing)
        self.filterMenu.add_command(label="Unsharp Masking", command=self._unsharp_masking)
        self.filterMenu.add_command(label="Laplacian", command=self._laplacian_filter)
        self.menuBar.add_cascade(label="Filter", menu=self.filterMenu)

    def _add_toolbar_buttons(self):
        self.leftFrame = tk.Frame(self.toolBar)
        self.leftFrame.pack(side=tk.LEFT)
        self.rightFrame = tk.Frame(self.toolBar)
        self.rightFrame.pack(side=tk.RIGHT)
        open_image = ImageTk.PhotoImage(Image.open("icons/open.png"))
        self.open_button = tk.Button(
            self.leftFrame,
            image=open_image,
            command=self._open_image,
            cursor="hand2"
    )
        self.open_button.image = open_image
        self.open_button.pack(side=tk.LEFT, padx=2, pady=2)

        settings_image = ImageTk.PhotoImage(Image.open("icons/settings.png"))
        self.settings_button = tk.Button(
            self.rightFrame,
            image=settings_image,
            command=self._open_settings,
            cursor="hand2"
    )
        self.settings_button.image = settings_image
        self.settings_button.pack(side=tk.RIGHT, padx=2, pady=2)
        self.other_buttons = []

    def _add_remaining_toolbar_buttons(self):
        icon_names = [
        ("save", self._save_as),
        ("zoom_in", self._zoom_in),
        ("Zoom_out", self._zoom_out),
        ("rotate", lambda: self._rotate_image(90)),
        ("brightness", self._brightness),
        ("contrast", self._contrast),
        ("grayscale", self._grayscale),
        ("dark", self._toggle_dark_mode),
        ("undo", self._undo),
        ("camera",self._open_camera)
    ]

        for name, command in icon_names:
            image = ImageTk.PhotoImage(Image.open(f"icons/{name}.png"))
            button = tk.Button(
            self.leftFrame,
            image=image,
            command=command,
            cursor="hand2"
        )
            button.image = image
            button.pack(side=tk.LEFT, padx=2, pady=2)
            self.other_buttons.append(button)




    def _open_image(self):
        path = filedialog.askopenfilename(filetypes=[("Images", "*.jpg *.png *.jpeg")])
        if path:
            self.imageFileName = path
            self.processor = ImageProcessor(path)
            self._load_image(path)
            self._show_sidebar(path)
                # बाकी icons add करो अगर अभी तक नहीं बने
        if not self.other_buttons:
            self._add_remaining_toolbar_buttons()


    def _open_camera(self):
        cap = cv2.VideoCapture(0)
        cv2.namedWindow("Camera Feed")

        while True:
            ret, frame = cap.read()
            if not ret:
                break

            cv2.imshow("Camera Feed", frame)

            key = cv2.waitKey(1)

            if key % 256 == 27:
            # ESC pressed - Exit
                print("Closing camera.")
                break
            elif key % 256 == 32:
            # SPACE pressed - Capture image
                img_name = "captured_image.png"
                cv2.imwrite(img_name, frame)
                print(f"Image saved as {img_name}")

                cap.release()
                cv2.destroyAllWindows()
                self._load_image(img_name)
                return

        cap.release()
        cv2.destroyAllWindows()

    def _open_settings(self):
        popup = tk.Toplevel(self)
        popup.title("About IMagic")
        popup.geometry("450x570")
        popup.configure(bg="#ffffff")
        popup.resizable(False, False)

    # User Icon
        user_icon = Image.open("icons/user.png").resize((100, 100), Image.LANCZOS)
        user_photo = ImageTk.PhotoImage(user_icon)
        tk.Label(popup, image=user_photo, bg="#ffffff").pack(pady=(20, 10))
        popup.user_photo = user_photo  # prevent garbage collection

    # App Title
        tk.Label(popup, text="IMagic", font=("Segoe UI", 20, "bold"), bg="#ffffff", fg="#2c3e50").pack()

    # Subtitle
        tk.Label(
        popup,
        text="Image Processing Toolkit",
        font=("Segoe UI", 12),
        bg="#ffffff",
        fg="#7f8c8d"
    ).pack(pady=(0, 10))

    # Divider
        tk.Frame(popup, bg="#bdc3c7", height=1).pack(fill=tk.X, padx=20, pady=10)

    # Details Section
        details = {
        "Version": "1.0.0",
        "Author": "Ankit Bundela",
        "Email": "ankit.b@example.com",
        "License": "MIT",
        "Built with": "Python, Tkinter, PIL, OpenCV"
    }

        for key, value in details.items():
            frame = tk.Frame(popup, bg="#ffffff")
            frame.pack(fill=tk.X, padx=30, pady=3)
            tk.Label(frame, text=f"{key}:", font=("Segoe UI", 10, "bold"), width=12, anchor="w", bg="#ffffff").pack(side=tk.LEFT)
            tk.Label(frame, text=value, font=("Segoe UI", 10), anchor="w", bg="#ffffff", fg="#34495e").pack(side=tk.LEFT)

    # Divider
        tk.Frame(popup, bg="#bdc3c7", height=1).pack(fill=tk.X, padx=20, pady=10)

    # Description
        about_text = (
        "IMagic helps you process images with advanced\n"
        "filters, transformations, and enhancements.\n"
        "Built with love for learners and professionals."
    )
        tk.Label(
        popup,
        text=about_text,
        font=("Segoe UI", 10),
        bg="#ffffff",
        fg="#2d3436",
        justify=tk.CENTER
    ).pack(padx=30, pady=5)

    # Close Button
        tk.Button(
        popup,
    text="Close",
    command=popup.destroy,
    font=("Segoe UI", 10, "bold"),
    bg="#27ae60",
    fg="white",
    activebackground="#219150",
    width=20,   # 20 characters wide
    cursor="hand2",
    relief="flat",
        bd=0,
    ).pack(pady=20, ipady=6)

        
    # Center the popup
        popup.update_idletasks()
        x = self.winfo_rootx() + self.winfo_width() // 2 - 225  
        y = self.winfo_rooty() + self.winfo_height() // 2 - 250
        popup.geometry(f"+{x}+{y}")

    def _toggle_dark_mode(self):
        self.dark_mode = not self.dark_mode

        if self.dark_mode:
        # Dark colors
            bg_color = "#2e2e2e"
            fg_color = "#ffffff"
            sidebar_bg = "#3c3c3c"
            button_bg = "#444444"
        else:
        # Light colors
            bg_color = "#f0f0f0"
            fg_color = "#000000"
            sidebar_bg = "#f5f5f5"
            button_bg = "#dddddd"

    # Main window background
        self.configure(bg=bg_color)
        self.mainFrame.configure(bg=bg_color)
        self.imageContainerFrame.configure(bg=bg_color)
        self.toolBar.configure(bg=bg_color)
        self.canvas.configure(bg="black" if self.dark_mode else "white")
    # Update toolbar buttons
        for child in self.toolBar.winfo_children():
            if isinstance(child, tk.Button):
                child.configure(bg=button_bg)

    # Update sidebar
        if self.sidebar.winfo_ismapped():
            for widget in self.sidebar.winfo_children():
                cls = widget.__class__.__name__
                if cls in ("Label", "Button"):
                    widget.configure(bg=sidebar_bg, fg=fg_color)
                elif cls == "Scale":
                    widget.configure(bg=sidebar_bg, fg=fg_color, troughcolor="#666666" if self.dark_mode else "#d9d9d9")
                elif cls == "Frame":
                    widget.configure(bg="#555555" if self.dark_mode else "gray")
            self.sidebar.configure(bg=sidebar_bg)
    def _load_image(self, path):
        img = Image.open(path)
        self.originalImage = img.copy()
        canvas_width = self.canvas.winfo_width() or self.desktopWidth
        canvas_height = self.canvas.winfo_height() or self.desktopHeight
        img.thumbnail((canvas_width, canvas_height), Image.LANCZOS)
        self.currentImageWidth, self.currentImageHeight = img.size
        self.currentImage = ImageTk.PhotoImage(img)
        self.canvas.delete("all")
        self.canvas.create_image(0, 0, image=self.currentImage, anchor="nw")
        self.canvas.config(scrollregion=self.canvas.bbox(tk.ALL))
    
    def _show_sidebar(self, path):
        for widget in self.sidebar.winfo_children():
            widget.destroy()
        #self.sidebar.configure(bg="#f5f5f5", width=240)
        self.sidebar.configure(bg="#f5f5f5", width=300)
        self.sidebar.pack_propagate(False)
        img = Image.open(path)

    # Details
        tk.Label(self.sidebar, text=f"File: {os.path.basename(path)}", anchor="w", bg="#f5f5f5").pack(fill=tk.X, padx=5, pady=2)
        tk.Label(self.sidebar, text=f"Size: {img.size}", anchor="w", bg="#f5f5f5").pack(fill=tk.X, padx=5)
        tk.Label(self.sidebar, text=f"Mode: {img.mode}", anchor="w", bg="#f5f5f5").pack(fill=tk.X, padx=5, pady=2)

    # Brightness
        tk.Label(self.sidebar, text="Brightness", bg="#f5f5f5").pack(pady=(10,0))
        brightness_slider = tk.Scale(
            self.sidebar,
            from_=-265, to=265,
            orient=tk.HORIZONTAL,
            resolution=1,
        command=self._adjust_brightness,
        bg="#f5f5f5"
    )
        brightness_slider.set(0)
        brightness_slider.pack(fill=tk.X, padx=5)

    # Contrast
        tk.Label(self.sidebar, text="Contrast", bg="#f5f5f5").pack(pady=(10,0))
        contrast_slider = tk.Scale(
            self.sidebar,
        from_=-265, to=265,
        orient=tk.HORIZONTAL,
        resolution=1,
        command=self._adjust_contrast,
        bg="#f5f5f5"
    )
        contrast_slider.set(0)
        contrast_slider.pack(fill=tk.X, padx=5)
    # Separator
        tk.Frame(self.sidebar, height=2, bg="gray").pack(fill=tk.X, pady=10, padx=5)
        tk.Label(self.sidebar, text="Filters", font=("Segoe UI", 10, "bold"), bg="#f5f5f5").pack(anchor="w", padx=5)

    # Mean Filter Slider
        tk.Label(self.sidebar, text="Mean Filter Strength", bg="#f5f5f5").pack(pady=(5,0))
        mean_slider = tk.Scale(
        self.sidebar,
        from_=1, to=10,
        orient=tk.HORIZONTAL,
        resolution=1,
        command=self._apply_mean_filter_slider,
        bg="#f5f5f5"
    )
        mean_slider.set(1)
        mean_slider.pack(fill=tk.X, padx=5)

    # Gaussian Smoothing Sigma
        tk.Label(self.sidebar, text="Gaussian Sigma", bg="#f5f5f5").pack(pady=(5,0))
        gaussian_slider = tk.Scale(
            self.sidebar,
        from_=0.1, to=5.0,
        orient=tk.HORIZONTAL,
        resolution=0.1,
        command=self._apply_gaussian_slider,
        bg="#f5f5f5"
    )
        gaussian_slider.set(1.0)
        gaussian_slider.pack(fill=tk.X, padx=5)

    # Unsharp Masking Amount
        tk.Label(self.sidebar, text="Unsharp Amount", bg="#f5f5f5").pack(pady=(5,0))
        unsharp_slider = tk.Scale(
        self.sidebar,
        from_=0.1, to=5.0,
        orient=tk.HORIZONTAL,
        resolution=0.1,
        command=self._apply_unsharp_slider,
        bg="#f5f5f5"
    )
        unsharp_slider.set(1.0)
        unsharp_slider.pack(fill=tk.X, padx=5)
        tk.Frame(self.sidebar, height=2, bg="gray").pack(fill=tk.X, pady=10, padx=5)
    # Color Picker
        tk.Button(
        self.sidebar,
        text="Color Picker",
        command=self._pick_color,
        bg="#dddddd",
        cursor="hand2"
    ).pack(pady=5, padx=5, fill=tk.X)
    # AI Auto Enhance Button
        tk.Button(
        self.sidebar,
        text="✨ AI Auto Enhance",
        command=self._ai_auto_enhance,
        bg="#27ae60",
        fg="white",
        font=("Segoe UI", 10, "bold"),
        cursor="hand2"
    ).pack(pady=10, padx=5, fill=tk.X)

        self.sidebar.pack(side=tk.RIGHT, fill=tk.Y)
    def _adjust_brightness(self, val):
        factor = 1 + (float(val) / 265)
        enhancer = ImageEnhance.Brightness(self.originalImage)
        img = enhancer.enhance(factor)
        self._update_sidebar_preview(img)

    def _adjust_contrast(self, val):
        factor = 1 + (float(val) / 265)
        enhancer = ImageEnhance.Contrast(self.originalImage)
        img = enhancer.enhance(factor)
        self._update_sidebar_preview(img)
    def _ai_auto_enhance(self):
        if self.imageFileName:
            self._save_undo()
            img = Image.open(self.imageFileName)
        enhancer_b = ImageEnhance.Brightness(img)
        img = enhancer_b.enhance(1.3)
        enhancer_c = ImageEnhance.Contrast(img)
        img = enhancer_c.enhance(1.3)
        img = img.filter(ImageFilter.UnsharpMask(radius=2, percent=150, threshold=3))
        img.save("icons/images/current_working_image.png")
        self.imageFileName = "icons/images/current_working_image.png"
        self.processor = ImageProcessor(self.imageFileName)
        self._load_image(self.imageFileName)
        self._show_success_message("AI Auto Enhance applied successfully!")

    def _apply_mean_filter_slider(self, val):
        if self.processor:
            self._save_undo()
            out_file = self.processor.apply_mean(strength=int(val))
            self._reload_after_filter(out_file)

    def _apply_gaussian_slider(self, val):
        if self.processor:
            self._save_undo()
            out_file = self.processor.apply_gaussian(sigma=float(val))
            self._reload_after_filter(out_file)

    def _apply_unsharp_slider(self, val):
        if self.processor:
            self._save_undo()
            out_file = self.processor.apply_unsharp(amount=float(val))
            self._reload_after_filter(out_file)
    def _update_sidebar_preview(self, img):
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        img.thumbnail((canvas_width, canvas_height), Image.LANCZOS)
        self.currentImage = ImageTk.PhotoImage(img)
        self.canvas.delete("all")
        self.canvas.create_image(0, 0, image=self.currentImage, anchor="nw")

    def _pick_color(self):
        color = colorchooser.askcolor()[1]
        if color:
            self._show_success_message(f"You picked color: {color}")
    def _save_undo(self):
        if self.imageFileName:
            img = Image.open(self.imageFileName)
            self.undoImage = img.copy()

    def _undo(self):
        if self.undoImage:
            self._set_current_image(self.undoImage.copy())

    def _set_current_image(self, img):
        self.currentImageWidth, self.currentImageHeight = img.size
        self.currentImage = ImageTk.PhotoImage(img)
        self.canvas.delete("all")
        self.canvas.create_image(0, 0, image=self.currentImage, anchor="nw")
        self.canvas.config(scrollregion=self.canvas.bbox(tk.ALL))
        img.save("icons/images/current_working_image.png")
        self.imageFileName = "icons/images/current_working_image.png"
        self.processor = ImageProcessor(self.imageFileName)

    def _on_press(self, event):
        self.x = event.x
        self.y = event.y
        self.rect_id = self.canvas.create_rectangle(self.x, self.y, self.x, self.y, outline='red', width=2)

    def _on_drag(self, event):
        if self.rect_id:
            self.canvas.coords(self.rect_id, self.x, self.y, event.x, event.y)

    def _on_release(self, event):
        if self.rect_id:
            self._save_undo()
            self.canvas.delete(self.rect_id)
            self.rect_id = None
            self._resize_image(self.x, self.y, event.x, event.y)

    def _resize_image(self, start_x, start_y, end_x, end_y):
        if self.imageFileName:
            img = Image.open(self.imageFileName)
            orig_w, orig_h = img.size
            disp_w, disp_h = self.currentImageWidth, self.currentImageHeight
            scale_x = orig_w / disp_w
            scale_y = orig_h / disp_h
            crop_box = (
                min(int(start_x * scale_x), int(end_x * scale_x)),
                min(int(start_y * scale_y), int(end_y * scale_y)),
                max(int(start_x * scale_x), int(end_x * scale_x)),
                max(int(start_y * scale_y), int(end_y * scale_y))
            )
            croppedImg = img.crop(crop_box)
            self._set_current_image(croppedImg)    
    def _show_success_message(self, text):
        popup = tk.Toplevel(self)
        popup.title("Success")
        popup.geometry("300x120")
        popup.update_idletasks()
        x = self.winfo_rootx() + self.winfo_width() // 2 - 150
        y = self.winfo_rooty() + self.winfo_height() // 2 - 60
        popup.geometry(f"+{x}+{y}")
        popup.transient(self)
        popup.grab_set()
        label = tk.Label(popup, text=text, font=("Segoe UI", 11), pady=10)
        label.pack(padx=20, fill=tk.BOTH)
        ok_btn = tk.Button(popup, text="OK", width=10, font=("Segoe UI", 10), command=popup.destroy)
        ok_btn.pack(pady=10)
        ok_btn.focus_set()
        self.wait_window(popup)
    def _brightness(self):
        if self.processor:
            self._save_undo()
            val = 150  # Fixed brightness value
            out_file = self.processor.apply_brightness(val)
            self._load_image(out_file)
            self._show_success_message("Brightness applied successfully!")

    def _contrast(self):
        if self.processor:
            self._save_undo()
            val = 160  # Fixed contrast value
            out_file = self.processor.apply_contrast(val)
            self._load_image(out_file)
            self._show_success_message("Contrast applied successfully!")
    
    def _grayscale(self):
        if self.processor:
            self._save_undo()
            out_file = self.processor.apply_grayscale()
            self._load_image(out_file)

    def _rotate_image(self, angle=90):
        if self.processor:
            self._save_undo()
            out_file = self.processor.rotate(angle)
            self._load_image(out_file)

    def _flip_image(self, direction):
        if self.processor:
            self._save_undo()
            out_file = self.processor.flip(direction)
            self._load_image(out_file)

    def _zoom_in(self):
        if self.imageFileName:
            self.zoomFactor *= 1.1
            self._update_image()

    def _zoom_out(self):
        if self.imageFileName:
            self.zoomFactor /= 1.1
            self._update_image()

    def _update_image(self):
        img = Image.open(self.imageFileName)
        newSize = (
            int(self.currentImageWidth * self.zoomFactor),
            int(self.currentImageHeight * self.zoomFactor)
        )
        img = img.resize(newSize, Image.LANCZOS)
        self.currentImageWidth, self.currentImageHeight = img.size
        self.currentImage = ImageTk.PhotoImage(img)
        self.canvas.delete("all")
        self.canvas.create_image(0, 0, image=self.currentImage, anchor="nw")
        self.canvas.config(scrollregion=self.canvas.bbox(tk.ALL))

    def _save_image(self):
        if self.imageFileName:
            img = Image.open(self.imageFileName)
            save_path = filedialog.asksaveasfilename(defaultextension=".jpg", filetypes=[("JPEG files", "*.jpg"), ("PNG files", "*.png")])
            if save_path:
                img.save(save_path)

    def _save_as(self):
        self._save_image()

    def _set_current_image(self, img):
        canvas_width = self.canvas.winfo_width() or self.desktopWidth
        canvas_height = self.canvas.winfo_height() or self.desktopHeight
        img.thumbnail((canvas_width, canvas_height), Image.LANCZOS)
        self.currentImageWidth, self.currentImageHeight = img.size
        self.currentImage = ImageTk.PhotoImage(img)
        self.canvas.delete("all")
        self.canvas.create_image(0, 0, image=self.currentImage, anchor="nw")
        self.canvas.config(scrollregion=self.canvas.bbox(tk.ALL))
        img.save("icons/images/current_working_image.png")
        self.imageFileName = "icons/images/current_working_image.png"
        self.processor = ImageProcessor(self.imageFileName)

    def _mean_filter(self):
        if self.processor:
            self._save_undo()
            out_file = self.processor.apply_mean()
            self._reload_after_filter(out_file)

    def _median_filter(self):
        if self.processor:
            self._save_undo()
            out_file = self.processor.apply_median()
            self._reload_after_filter(out_file)

    def _fourier_transform(self):
        if self.processor:
            self._save_undo()
            out_file = self.processor.apply_fourier()
            self._reload_after_filter(out_file)

    def _gaussian_smoothing(self):
        if self.processor:
            self._save_undo()
            out_file = self.processor.apply_gaussian()
            self._reload_after_filter(out_file)

    def _unsharp_masking(self):
        if self.processor:
            self._save_undo()
            out_file = self.processor.apply_unsharp()
            self._reload_after_filter(out_file)

    def _laplacian_filter(self):
        if self.processor:
            self._save_undo()
            out_file = self.processor.apply_laplacian()
            self._reload_after_filter(out_file)

    def _reload_after_filter(self, out_file):
        self.imageFileName = out_file
        self.processor = ImageProcessor(out_file)
        self._load_image(out_file)


def show_main_ui():
    loading_screen.after_cancel(loading_screen.after_id)
    loading_screen.destroy()
    main_window = MainWindow()
    main_window.mainloop()
# Main Application Flow
loading_screen = LoadingScreen()
loading_screen.after(5000, show_main_ui)  # 5000 ms = 5 seconds, adjust as needed
loading_screen.mainloop()

