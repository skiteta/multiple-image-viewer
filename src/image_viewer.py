import tkinter as tk
from tkinter import ttk
from tkinter import *
from tkinter import filedialog
from PIL import Image, ImageTk
import cv2


class Application(tk.Frame):
    def __init__(self, master):
        super().__init__(master)
        self.pack()

        self.master.geometry("1060x610")
        self.master.title("image viewer")

        self.canvas1 = None
        self.images = []
        self.start_x = None
        self.start_y = None
        self.end_x = None
        self.end_y = None
        self.oval = None
        self.current_id = 0
        self.frame_num = None
        self.frame_data = {}
        self.scale_var = tk.DoubleVar()
        self.scale = None
        self.slider = None
        self.create_widgets()
        self.canvas1.bind("<KeyPress>", self.key_event)
        self.canvas1.focus_set()

    def next_image(self, event):
        self.canvas1.focus_set()
        if self.current_id < self.frame_num - 1:
            self.current_id += 1
        self.scale_var.set(self.scale_var.get() + 1.0)
        self.scroll(event, self.current_id)

    def before_image(self, event):
        self.canvas1.focus_set()
        if self.current_id > 0:
            self.current_id -= 1
        self.scale_var.set(self.scale_var.get() - 1.0)
        self.scroll(event, self.current_id)

    def scroll(self, event, scale_value=None):
        self.canvas1.focus_set()
        if scale_value is None:
            scale_value = int(self.scale_var.get())
        self.current_id = scale_value
        print(f'===== FRAME {self.current_id} =====')
        self.canvas1.delete('all')
        self.canvas1.create_image(483, 273, image=self.images[self.current_id])

    def key_event(self, event):
        key = event.keysym
        if key == 'n':
            self.next_image(event)
        elif key == 'p':
            self.before_image(event)
        elif key == 's':
            self.save()
        elif key == 'l':
            self.load_image()

    def create_widgets(self):
        side_panel = tk.Frame(self.master, borderwidth=2, relief=tk.SUNKEN)
        button_width = 8
        load_images_button = ttk.Button(side_panel, text='load images', width=button_width)
        load_images_button.configure(command=self.load_images)
        load_images_button.pack()

        load_movie_button = ttk.Button(side_panel, text='load movie', width=button_width)
        load_movie_button.configure(command=self.load_movie)
        load_movie_button.pack()

        next_button = ttk.Button(side_panel, text='next', width=button_width)
        next_button.configure(command=self.next_image)
        next_button.pack()

        before_button = ttk.Button(side_panel, text='before', width=button_width)
        before_button.configure(command=self.before_image)
        before_button.pack()

        side_panel.pack(side=tk.RIGHT, fill=tk.Y)

        self.slider = tk.Frame(self.master, borderwidth=2, relief=tk.SUNKEN)
        self.scale = tk.Scale(self.slider,
                              variable=self.scale_var,
                              command=self.scroll,
                              orient=tk.HORIZONTAL,
                              length=930,
                              width=20,
                              sliderlength=10,
                              from_=0,
                              to=0,
                              resolution=1,
                              tickinterval=len(self.images) // 2)
        self.scale.pack()
        self.slider.pack(side=tk.BOTTOM, fill=tk.X)

        self.canvas1 = tk.Canvas(self.master)
        self.canvas1.pack(expand=True, fill=tk.BOTH)

    def load_images(self):
        self.canvas1.focus_set()
        self.current_id = 0
        filenames = filedialog.askopenfilenames()
        self.images = []
        for filename in filenames:
            image = cv2.imread(filename)
            image = cv2.resize(image, (960, 540), interpolation=cv2.INTER_AREA)
            image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            image_array = Image.fromarray(image_rgb)
            tk_image = ImageTk.PhotoImage(image_array)
            self.images.append(tk_image)
        self.set_images()

    def load_movie(self):
        self.canvas1.focus_set()
        self.current_id = 0
        filename = filedialog.askopenfilename()
        self.master.title(filename.split('/')[-1])
        cap = cv2.VideoCapture(filename)
        if not cap.isOpened():
            print("can not open this movie")
            return

        self.images = []
        while True:
            ret, frame = cap.read()
            if ret:
                image = cv2.resize(frame, (960, 540), interpolation=cv2.INTER_AREA)
                image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
                image_array = Image.fromarray(image_rgb)
                tk_image = ImageTk.PhotoImage(image_array)
                self.images.append(tk_image)
            else:
                break
        self.set_images()

    def set_images(self):
        self.frame_num = len(self.images)
        self.frame_data = {i: {
            'frame_id': i,
            'x': None,
            'y': None,
            'radius': None
        } for i in range(self.frame_num)}
        self.canvas1.create_image(483, 273, image=self.images[self.current_id])
        self.scale.destroy()
        self.scale = tk.Scale(self.slider,
                              variable=self.scale_var,
                              command=self.scroll,
                              orient=tk.HORIZONTAL,
                              length=930,
                              width=20,
                              sliderlength=10,
                              from_=0,
                              to=len(self.images) - 1,
                              resolution=1,
                              tickinterval=len(self.images) // 2)
        self.scale.pack()


if __name__ == "__main__":
    root = tk.Tk()
    app = Application(master=root)
    app.mainloop()
