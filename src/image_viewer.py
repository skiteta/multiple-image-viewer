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

        self.master.geometry("1100x660")
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
        self.create_widgets()
        self.canvas1.bind("<ButtonPress-1>", self.start_point_get)
        self.canvas1.bind("<Button1-Motion>", self.oval_drawing)
        self.canvas1.bind("<ButtonRelease-1>", self.release_action)

    def create_widgets(self):
        self.canvas1 = tk.Canvas(self)
        self.canvas1.configure(width=960, height=540, bg='black')
        self.canvas1.grid(column=1, row=0)
        self.canvas1.grid(padx=20, pady=20)

        frame_button = ttk.LabelFrame(self)
        frame_button.grid(column=1, row=1)
        frame_button.grid(padx=0, pady=0)

        button_open = ttk.Button(frame_button)
        button_open.configure(text='load')
        button_open.grid(column=0, row=1)
        button_open.configure(command=self.load_image)

        button_next = ttk.Button(frame_button)
        button_next.config(text='next')
        button_next.grid(column=1, row=1)
        button_next.configure(command=self.next_image)

        button_before = ttk.Button(frame_button)
        button_before.config(text='before')
        button_before.grid(column=2, row=1)
        button_before.configure(command=self.before_image)

        button_save = ttk.Button(frame_button)
        button_save.config(text='save')
        button_save.grid(column=3, row=1)
        button_save.configure(command=self.save)

    def load_image(self):
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

    def next_image(self):
        if self.current_id < self.frame_num - 1:
            self.current_id += 1
        print(f'===== FRAME {self.current_id} =====')
        self.canvas1.create_image(483, 273, image=self.images[self.current_id])

    def before_image(self):
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

    def start_point_get(self, event):
        if not (self.start_x is None or self.start_y is None or self.end_x is None or self.end_y is None):
            is_in_before_rectangle = self.start_x <= event.x <= self.end_x and self.start_y <= event.y <= self.end_y
            if is_in_before_rectangle:
                # self.canvas1.bind('oval1', "<Button1-Motion>", self.drag)
                self.drag(event)
                return

        self.canvas1.delete("oval1")
        self.oval = self.canvas1.create_oval(event.x, event.y, event.x + 1, event.y + 1, outline="red", tag="oval1")
        self.start_x, self.start_y = event.x, event.y

    def oval_drawing(self, event):
        width, height = 960, 540
        if event.x < 0:
            cur_end_x = 0
        else:
            cur_end_x = min(width, event.x)
        if event.y < 0:
            cur_end_y = 0
        else:
            cur_end_y = min(height, event.y)
        self.end_x, self.end_y = cur_end_x, cur_end_y
        self.canvas1.coords("oval1", self.start_x, self.start_y, self.end_x, self.end_y)

    def drag(self, event):
        self.start_x = event.x
        self.start_y = event.y
        print(self.oval)
        self.canvas1.move(
            self.oval,
            event.x - self.start_x,
            event.y - self.start_y
        )

    def release_action(self, event):
        start_x, start_y, end_x, end_y = [
            round(n * 2) for n in self.canvas1.coords("oval1")
        ]

        if abs(start_x - end_x) == abs(start_y - end_y) == 2:
            return

        print(f'===== FRAME {self.current_id} COORDINATES =====')
        print("start_x : " + str(start_x) + "\n" + "start_y : " +
              str(start_y) + "\n" + "end_x : " + str(end_x) + "\n" +
              "end_y : " + str(end_y))
        x_center = start_x + abs(end_x - start_x) // 2
        y_center = start_y + abs(end_y - start_y) // 2
        radius = ((end_x - x_center) ** 2 + (end_y - y_center) ** 2) ** 0.5 // 2
        self.frame_data[self.current_id] = {
            'frame_id': self.current_id,
            'x': x_center,
            'y': y_center,
            'radius': radius
        }
        # self.next_image()


if __name__ == "__main__":
    root = tk.Tk()
    app = Application(master=root)
    app.mainloop()