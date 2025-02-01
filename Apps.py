import cv2
import ctypes
import PIL
import numpy as np
from PIL import Image, ImageTk
import tkinter as tk
import tkinter.messagebox
from tkinter import filedialog
import tkinter.filedialog
import time
class LoadingScreen(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Loading...")
        new_width =500
        new_height=260
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
        self.load_gif("icons/loading.gif")  # Replace with your GIF file path
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
            self.after(100, self.animate)  # Adjust frame rate


class MainWindow(tk.Tk):
    def __init__(self):
        tk.Tk.__init__(self)
        width, height = ctypes.windll.user32.GetSystemMetrics(0), ctypes.windll.user32.GetSystemMetrics(1)
        self.desktopWidth = width
        self.desktopHeight = height
        self.iconbitmap("icons/icon.ico")
        self.title("IMagic")
        self.geometry(f"{self.desktopWidth}x{self.desktopHeight}+0+0")
        self.state("zoomed")
        self.resizable(0, 0)

        # Create UI components
        self.menuBar = tk.Menu(self)
        self.config(menu=self.menuBar)
        self.create_menus()

        # Create main container frame
        self.mainFrame = tk.Frame(self)
        self.mainFrame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Create the image container frame
        self.imageContainerFrame = tk.Frame(self.mainFrame, bd=1)
        self.imageContainerFrame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        # Sidebar frame (initially empty, will be populated after loading image)
        self.sidebarFrame=tk.Frame(self.mainFrame, bd=1, bg="lightgrey", width=350)
        self.sidebarFrame.pack(side=tk.LEFT, fill=tk.Y)
        self.sidebarFrame.pack_forget()  # Hide sidebar initially

        # Image canvas
        self.imageCanvas=tk.Canvas(self.imageContainerFrame)
        self.imageCanvas.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        self.imageFileName = None
        self.currentImage = None
        self.currentImageWidth = None
        self.currentImageHeight = None
        self.zoomFactor = 1.0
		#-----Mouse Move--------->
        self.x=None
        self.y=None
        self.z=None
        self.imageCanvas.bind("<ButtonPress-1>", self._onPress)
        self.imageCanvas.bind("<B1-Motion>", self._onScrool)
        self.imageCanvas.bind("<ButtonRelease-1>", self._onRelease)

    def _onPress(self,event):
        self.x=event.x
        self.y=event.y
        self.z=self.imageCanvas.create_rectangle(self.x, self.y,self.x, self.y,outline='red', width=2)
    def _onScrool(self, event):
        if self.z:
            self.imageCanvas.coords(self.z,self.x,self.y,event.x,event.y)
    def _onRelease(self, event):
        if self.z:
            self.imageCanvas.delete(self.z)
            self.z=None
            end_x,end_y=event.x,event.y
            self._resizeImage(self.x,self.y,end_x,end_y)
    def _resizeImage(self,start_x,start_y,end_x,end_y):
        if self.currentImage:
            img=Image.open(self.imageFileName)
            cropBox=(start_x,start_y,end_x,end_y)
            croppedImg=img.crop(cropBox)
            self.currentImage=ImageTk.PhotoImage(croppedImg)
            self.imageCanvas.create_image(0, 0, image=self.currentImage, anchor="nw")
            self.imageCanvas.config(scrollregion=self.imageCanvas.bbox(tk.ALL))
            self.imageFileName = "resized_image.png"
            croppedImg.save(self.imageFileName)
    def _enable_resize(self):
        pass

    def create_menus(self):
        # File Menu
        self.fileMenu = tk.Menu(self.menuBar, tearoff=0)
        self.fileMenu.add_command(label="New")
        self.fileMenu.add_command(label="Open", command=self._openImage)
        self.fileMenu.add_command(label="Save", command=self._saveImage)
        self.fileMenu.add_command(label="Save As", command=self._saveAs)
        self.fileMenu.add_separator()
        self.fileMenu.add_command(label="Exit", command=self._exit)
        self.menuBar.add_cascade(label="File", menu=self.fileMenu)

        # Edit Menu
        self.editMenu = tk.Menu(self.menuBar, tearoff=0)
        self.editMenu.add_command(label="Cut")
        self.editMenu.add_command(label="Copy")
        self.editMenu.add_command(label="Paste")
        self.menuBar.add_cascade(label="Edit", menu=self.editMenu)

        # View Menu
        self.viewMenu = tk.Menu(self.menuBar, tearoff=0)
        self.viewMenu.add_command(label="Zoom In", command=self._zoom_in)
        self.viewMenu.add_command(label="Zoom Out", command=self._zoom_out)
        self.menuBar.add_cascade(label="View", menu=self.viewMenu)

	#TransformMenu ccreate heare
        self.transformMenu=tkinter.Menu(self.menuBar,tearoff=0)
        self.transformMenu.add_command(label="Crop")
        self.transformMenu.add_command(label="Rotate",command=self._rotate_image)
        self.transformMenu.add_command(label="Rotate 90\u00b0",command=lambda: self._rotate_image(90))
        self.transformMenu.add_command(label="Rotate 90\u00b0 Left",command=lambda: self._rotate_image(-90))
        self.transformMenu.add_command(label="Rotate 180\u00b0",command=lambda: self._rotate_image(180))
        self.transformMenu.add_command(label="Flip Horizontal",command=lambda: self._flip_image('horizontal'))
        self.transformMenu.add_command(label="Flop Vertical",command=lambda: self._flip_image('vertical'))
        self.menuBar.add_cascade(label="transform",menu=self.transformMenu)

    #Filter create heare
        self.filterMenu = tkinter.Menu(self.menuBar, tearoff=0)
        self.filterMenu.add_command(label="Mean", command=self._mean_filter)
        self.filterMenu.add_command(label="Median", command=self._median_filter)
        self.filterMenu.add_command(label="Fourier Transform", command=self._fourier_transform)
        self.filterMenu.add_command(label="Gaussian Smoothing", command=self._gaussian_smoothing)
        self.filterMenu.add_command(label="Unsharp", command=self._unsharp)
        self.filterMenu.add_command(label="Laplacian", command=self._laplacian)
        self.menuBar.add_cascade(label="Filter", menu=self.filterMenu)

	#toolBar
        self.toolBar=tkinter.Frame(self,relief=tkinter.RAISED,bd=1)
        self.toolBar.pack(side=tkinter.TOP,fill=tkinter.X)


    #ToolBar buttons
        self.imagePick=PIL.ImageTk.PhotoImage(PIL.Image.open("icons/pick.png"))
        self.toolBarPickButton=tkinter.Button(self.toolBar,image=self.imagePick,cursor="hand2")
        self.toolBarPickButton.pack(side=tkinter.LEFT,padx=2,pady=2)

        self.imageNew=PIL.ImageTk.PhotoImage(PIL.Image.open("icons/new.png"))
        self.toolBarNewButton=tkinter.Button(self.toolBar,image=self.imageNew,cursor="hand2")
        self.toolBarNewButton.pack(side=tkinter.LEFT,padx=(15,2),pady=2)

        self.imageOpen=PIL.ImageTk.PhotoImage(PIL.Image.open("icons/open.png"))
        self.toolBarOpenButton=tkinter.Button(self.toolBar,image=self.imageOpen,command=self._openImage,cursor="hand2")
        self.toolBarOpenButton.pack(side=tkinter.LEFT,padx=2,pady=2)

        self.imageExit=PIL.ImageTk.PhotoImage(PIL.Image.open("icons/exit.png"))
        self.toolBarExitButton=tkinter.Button(self.toolBar,image=self.imageExit,command=self._exit,cursor="hand2")
        self.toolBarExitButton.pack(side=tkinter.RIGHT,padx=2,pady=2)

        
    def create_sidebar(self):
    # Add buttons or other widgets to the sidebar
        # Clear previous sidebar content
        for widget in self.sidebarFrame.winfo_children():
            widget.destroy()

        self.sidebarLabel = tk.Label(self.sidebarFrame, text="Toolbar", bg="lightgrey", font=("Helvetica", 16))
        self.sidebarLabel.pack(padx=55, pady=10)

    # Load PNG icons for zoom in and zoom out
        self.imageZoomIn = ImageTk.PhotoImage(Image.open("icons/zoom_in.png"))
        self.imageZoomOut = ImageTk.PhotoImage(Image.open("icons/zoom_out.png"))
        #self.imageMean = ImageTk.PhotoImage(Image.open("icons/mean.png"))
        self.imageSave = ImageTk.PhotoImage(Image.open("icons/save.png"))

    # Add zoom in button with icon
        self.toolBarZoomInButton = tk.Button(self.sidebarFrame, image=self.imageZoomIn, cursor="hand2", command=self._zoom_in)
        self.toolBarZoomInButton.pack(pady=3)

    # Add zoom out button with icon
        self.toolBarZoomOutButton = tk.Button(self.sidebarFrame, image=self.imageZoomOut, cursor="hand2", command=self._zoom_out)
        self.toolBarZoomOutButton.pack(pady=5)
    #Save Image Button
        self.toolBarSave = tk.Button(self.sidebarFrame, image=self.imageSave, cursor="hand2", command=self._saveImage)
        self.toolBarSave.pack(pady=5)

        self.imageRotate = ImageTk.PhotoImage(Image.open("icons/rotate.png"))
        self.toolBarRotateButton = tk.Button(self.sidebarFrame, image=self.imageRotate, cursor="hand2", command=self._rotate_image)
        self.toolBarRotateButton.pack(pady=5)

        self.imageBrightness = ImageTk.PhotoImage(Image.open("icons/brightness.png"))
        self.toolBarBrightnessButton = tk.Button(self.sidebarFrame, image=self.imageBrightness, cursor="hand2", command=self._brightness)
        self.toolBarBrightnessButton.pack(pady=5)

    # Contrast Button
        self.imageContrast = ImageTk.PhotoImage(Image.open("icons/contrast.png"))
        self.toolBarContrastButton = tk.Button(self.sidebarFrame, image=self.imageContrast, cursor="hand2", command=self._Contrast)
        self.toolBarContrastButton.pack(pady=5)

    # Crop Button
        self.imageCrop = ImageTk.PhotoImage(Image.open("icons/crop.png"))
        self.toolBarCropButton = tk.Button(self.sidebarFrame, image=self.imageCrop, cursor="hand2")
        self.toolBarCropButton.pack(pady=5)

    # Grayscale Button
        self.imageGrayscale = ImageTk.PhotoImage(Image.open("icons/grayscale.png"))
        self.toolBarGrayscaleButton = tk.Button(self.sidebarFrame, image=self.imageGrayscale, cursor="hand2", command=self._grayScale)
        self.toolBarGrayscaleButton.pack(pady=5)

    def _exit(self):
        self.quit()
        self.destroy()

    def _openImage(self):
        imgfn = filedialog.askopenfilename(
            initialdir="/",
            title="Select image file",
            filetypes=(("JPEG files", "*.jpg"), ("PNG files", "*.png")),
        )
        if imgfn:
            self.imageFileName = imgfn
            self._loadImage()
            self.create_sidebar()  # Create and display the sidebar after the image is loaded
            self.sidebarFrame.pack(side=tk.RIGHT, fill=tk.Y)  # Show the sidebar

    def _loadImage(self):
        img = Image.open(self.imageFileName)
        self.currentImageWidth, self.currentImageHeight = img.size
        self.currentImage = ImageTk.PhotoImage(img)
        self.imageCanvas.create_image(0, 0, image=self.currentImage, anchor="nw")
        self.imageCanvas.config(scrollregion=self.imageCanvas.bbox(tk.ALL))

    def _saveImage(self):
        if self.imageFileName:
            img = Image.open(self.imageFileName)
            savePath = filedialog.asksaveasfilename(
                defaultextension=".jpg",
                filetypes=[("JPEG files", "*.jpg"), ("PNG files", "*.png")],
            )
            if savePath:
                img.save(savePath)

    def _saveAs(self):
        if self.imageFileName:
            img = Image.open(self.imageFileName)
            savePath = filedialog.asksaveasfilename(
                defaultextension=".jpg",
                filetypes=[("JPEG files", "*.jpg"), ("PNG files", "*.png")],
            )
            if savePath:
                img.save(savePath)

    def _zoom_in(self):
        self.zoomFactor *= 1.1
        self._update_image()

    def _zoom_out(self):
        self.zoomFactor /= 1.1
        self._update_image()

    def _update_image(self):
        img = Image.open(self.imageFileName)
        newSize = (
            int(self.currentImageWidth * self.zoomFactor),
            int(self.currentImageHeight * self.zoomFactor),
        )
        img = img.resize(newSize, Image.LANCZOS)
        self.currentImage = ImageTk.PhotoImage(img)
        self.imageCanvas.create_image(0, 0, image=self.currentImage, anchor="nw")
        self.imageCanvas.config(scrollregion=self.imageCanvas.bbox(tk.ALL))
    
    def _rotate_image(self, angle=90):
        if self.currentImage is None:
            return
        img=Image.open(self.imageFileName)
        img=img.rotate(angle,expand=True)
        self.imageFileName=f"image is:{angle}.jpg"
        img.save(self.imageFileName)
        self._loadImage()
    def _flip_image(self, direction):
        if self.currentImage is None:
            return
        img=Image.open(self.imageFileName)
        if direction=='horizontal':
            img=img.transpose(Image.FLIP_LEFT_RIGHT)
        elif direction=='vertical':
            img=img.transpose(Image.FLIP_TOP_BOTTOM)
        self.imageFileName=f"flipped image:{direction}.jpg"
        img.save(self.imageFileName)
        self._loadImage()
    def _brightness(self):
        if self.currentImage is None:
            return
        brightness=tk.simpledialog.askfloat("Brightness","Enter brightness value (0.0 - 255.0):", minvalue=0.0, maxvalue=255.0)
		#brightness=150
        if brightness is not None:
            imageData=cv2.imread(self.imageFileName)
            for r in range(imageData.shape[0]):
                for c in range(imageData.shape[1]):
                    rgb=imageData[r][c]
                    red=rgb[0]
                    green=rgb[1]
                    blue=rgb[2]
                    red+=brightness
                    green+=brightness
                    blue+=brightness
                    if red<0:red=0
                    if red>255:red=255
                    if green<0:green=0
                    if green>255:green=255
                    if blue<0:blue=0
                    if blue>255:blue=255
                    imageData[r][c]=(red,green,blue)			
                    self.imageFileName="brightness_value.jpg"
                cv2.imwrite(self.imageFileName,imageData)
                self._loadImage()
            tkinter.messagebox.showinfo("Brightness:","Convert is Successfull Brightness")
    def _grayScale(self):
        if self.currentImage is None:
            return
        grayScale=tk.simpledialog.askfloat("Gray Scale","GrayScale value (0.0 - 255.0):", minvalue=0.0, maxvalue=255.0)
		#brightness=150
        if grayScale is not None:
            imageData=cv2.imread(self.imageFileName)
            #imageData=np.clip()
            for r in range(imageData.shape[0]):
                for c in range(imageData.shape[1]):
                    rgb=imageData[r][c]
                    red=int(rgb[0])
                    green=int(rgb[1])
                    blue=int(rgb[2])
                    red+=grayScale
                    green+=grayScale
                    blue+=grayScale
                    total=int((red+green+blue)/3)
                    total=max(0, min(255, total))
                    imageData[r][c]=(total,total,total)
                    self.imageFileName="Gray_value.jpg"
                cv2.imwrite(self.imageFileName,imageData)
                self._loadImage()
            tkinter.messagebox.showinfo("Gray Scale:","Convert Successfull in GrayScale")
    def _Contrast(self):
        if self.currentImage is None:
            return
        Contrast=tk.simpledialog.askfloat("Constrast","Contrast value (0.0 - 255.0):", minvalue=0.0, maxvalue=255.0)
        if Contrast is not None:
            imageData=cv2.imread(self.imageFileName)
            f=(259*(Contrast+255))/(255*(259-Contrast))
            for r in range(imageData.shape[0]):
                for c in range(imageData.shape[1]):
                    rgb=imageData[r][c]
                    red=rgb[0]
                    green=rgb[1]
                    blue=rgb[2]
                    red+=Contrast
                    green+=Contrast
                    blue+=Contrast
                    newRed=(f*(red-128))+128
                    newGreen=(f*(green-128))+128
                    newBlue=(f*(blue-128))+128
                    if newRed>255:newRed=255
                    if newRed<0:newRed=0
                    if newGreen>255:newGreen=255
                    if newGreen<0:newGreen=0
                    if newBlue>255:newBlue=255
                    if newBlue<0:newBlue=0
                    imageData[r][c]=(newRed,newGreen,newBlue)			
                    self.imageFileName="Contrast.jpg"
                cv2.imwrite(self.imageFileName,imageData)
                self._loadImage()
            tkinter.messagebox.showinfo("Success is:","Contrast is Successfull")
    def _mean_filter(self):
        if self.currentImage is None:
            return
        imageData = cv2.imread(self.imageFileName)
        kernel = np.ones((5, 5), np.float32) / 25  # Simple 5x5 averaging kernel
        result = cv2.filter2D(imageData, -1, kernel)
        self.imageFileName = "mean_filtered.jpg"
        cv2.imwrite(self.imageFileName, result)
        self._loadImage()
        time.sleep(4)
        tkinter.messagebox.showinfo("Mean Filter", "Mean filter applied successfully.")

# Apply Median Filter
    def _median_filter(self):
        if self.currentImage is None:
            return
        imageData = cv2.imread(self.imageFileName)
        result = cv2.medianBlur(imageData, 5)  # 5x5 kernel for median filtering
        self.imageFileName = "median_filtered.jpg"
        cv2.imwrite(self.imageFileName, result)
        self._loadImage()
        time.sleep(4)
        tkinter.messagebox.showinfo("Median Filter", "Median filter applied successfully.")

# Apply Fourier Transform (For frequency domain manipulations, e.g., filtering)
    def _fourier_transform(self):
        if self.currentImage is None:
            return
        imageData = cv2.imread(self.imageFileName, cv2.IMREAD_GRAYSCALE)
        dft = cv2.dft(np.float32(imageData), flags=cv2.DFT_COMPLEX_OUTPUT)
        dft_shift = np.fft.fftshift(dft)  # Shift zero frequency components to center
        magnitude_spectrum = cv2.magnitude(dft_shift[:, :, 0], dft_shift[:, :, 1])
        self.imageFileName = "fourier_transformed.jpg"
        cv2.imwrite(self.imageFileName, magnitude_spectrum)
        self._loadImage()
        time.sleep(4)
        tkinter.messagebox.showinfo("Fourier Transform", "Fourier Transform applied successfully.")

# Apply Gaussian Smoothing
    def _gaussian_smoothing(self):
        if self.currentImage is None:
            return
        imageData = cv2.imread(self.imageFileName)
        result = cv2.GaussianBlur(imageData, (5, 5), 0)  # 5x5 kernel for Gaussian blur
        self.imageFileName = "gaussian_smoothing.jpg"
        cv2.imwrite(self.imageFileName, result)
        self._loadImage()
        time.sleep(4)
        tkinter.messagebox.showinfo("Gaussian Smoothing", "Gaussian smoothing applied successfully.")

# Apply Unsharp Mask (Enhancing edges)
    def _unsharp(self):
        if self.currentImage is None:
            return
        imageData = cv2.imread(self.imageFileName)
        blurred = cv2.GaussianBlur(imageData, (5, 5), 1.5)  # Blur image
        unsharp = cv2.addWeighted(imageData, 1.5, blurred, -0.5, 0)  # Sharpen the image
        self.imageFileName = "unsharp_masked.jpg"
        cv2.imwrite(self.imageFileName, unsharp)
        self._loadImage()
        time.sleep(4)
        tkinter.messagebox.showinfo("Unsharp Mask", "Unsharp mask applied successfully.")

# Apply Laplacian Filter (Edge detection)
    def _laplacian(self):
        if self.currentImage is None:
            return
        imageData = cv2.imread(self.imageFileName, cv2.IMREAD_GRAYSCALE)
        laplacian = cv2.Laplacian(imageData, cv2.CV_64F)
        self.imageFileName = "laplacian_filtered.jpg"
        cv2.imwrite(self.imageFileName, laplacian)
        self._loadImage()
        time.sleep(4)
        tkinter.messagebox.showinfo("Laplacian Filter", "Laplacian filter applied successfully.")

def show_main_ui():
    loading_screen.destroy()
    main_window = MainWindow()
    main_window.mainloop()
# Main Application Flow
loading_screen = LoadingScreen()
loading_screen.after(9000, show_main_ui)  # Wait for 5 seconds before showing main UI
loading_screen.mainloop()