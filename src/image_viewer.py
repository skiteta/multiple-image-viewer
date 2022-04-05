import csv
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
        self.master.title("Annotator")

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

    def scroll(self, event):
        self.canvas1.focus_set()
        self.current_id = int(self.scale_var.get())
        print(f'===== FRAME {self.current_id} =====')
        self.canvas1.create_image(483, 273, image=self.images[self.current_id])

    def key_event(self, event):
        key = event.keysym
        if key == 'n':
            self.next_image()
        elif key == 'b':
            self.before_image()
        elif key == 's':
            self.save()
        elif key == 'l':
            self.load_image()

    def create_widgets(self):
        side_panel = tk.Frame(self.master, borderwidth=2, relief=tk.SUNKEN)
        open_button = ttk.Button(side_panel, text='load')
        open_button.configure(command=self.load_image)
        open_button.pack()
        next_button = ttk.Button(side_panel, text='next')
        next_button.configure(command=self.next_image)
        next_button.pack()
        before_button = ttk.Button(side_panel, text='before')
        before_button.configure(command=self.before_image)
        before_button.pack()
        save_button = ttk.Button(side_panel, text='save')
        save_button.configure(command=self.save)
        save_button.pack()
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
                              tickinterval=5)
        self.scale.pack()
        self.slider.pack(side=tk.BOTTOM, fill=tk.X)

        self.canvas1 = tk.Canvas(self.master)
        self.canvas1.pack(expand=True, fill=tk.BOTH)

    def load_image(self):
        self.canvas1.focus_set()
        self.current_id = 0
        filename = filedialog.askopenfilename()
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
                              tickinterval=5)
        self.scale.pack()

    def next_image(self):
        self.canvas1.focus_set()
        if self.current_id < self.frame_num - 1:
            self.current_id += 1
        print(f'===== FRAME {self.current_id} =====')
        self.canvas1.create_image(483, 273, image=self.images[self.current_id])

    def before_image(self):
        self.canvas1.focus_set()
        if self.current_id > 0:
            self.current_id -= 1
        print(f'===== FRAME {self.current_id} =====')
        self.canvas1.create_image(483, 273, image=self.images[self.current_id])

    def save(self):
        file = filedialog.asksaveasfilename(
            title='Choose a file',
            filetypes=[('CSV', 'csv')],
            initialdir='./',
            defaultextension='.csv')
        if file:
            with open(file, 'w', encoding='utf_8') as f:
                writer = csv.writer(f)
                for i in range(self.frame_num):
                    data = self.frame_data[i]
                    writer.writerow([data.get('frame_id'), data.get('x'), data.get('y'), data.get('radius')])


if __name__ == "__main__":
    root = tk.Tk()
    app = Application(master=root)
    app.mainloop()
