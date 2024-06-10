import tkinter as tk
from tkinter import colorchooser
from PIL import ImageGrab
import base64, requests


class DrawingApp:
    def __init__(self, root):
        self.root = root
        self.root.title("AI Drawing Board")
        self.root.geometry("800x600")

        # Open in full-screen mode
        self.root.attributes("-fullscreen", True)

        # Disable resizing
        self.root.resizable(False, False)

        self.brush_size = 5
        self.brush_color = "black"

        self.canvas = tk.Canvas(root, bg="white", cursor="cross")
        self.canvas.pack(fill=tk.BOTH, expand=True)

        self.setup_menu()

        self.old_x = None
        self.old_y = None

        self.canvas.bind('<B1-Motion>', self.paint)
        self.canvas.bind('<ButtonRelease-1>', self.reset)

    def setup_menu(self):
        self.menu = tk.Menu(self.root)
        self.root.config(menu=self.menu)

        self.file_menu = tk.Menu(self.menu, tearoff=0)
        self.menu.add_cascade(label="File", menu=self.file_menu)
        self.file_menu.add_command(label="Save as PNG", command=self.save_as_png)
        self.file_menu.add_separator()
        self.file_menu.add_command(label="Exit", command=self.root.quit)

        self.option_menu = tk.Menu(self.menu, tearoff=0)
        self.menu.add_cascade(label="Options", menu=self.option_menu)
        self.option_menu.add_command(label="Clear Canvas", command=self.clear_canvas)
        self.option_menu.add_command(label="Brush Color", command=self.choose_color)
        self.option_menu.add_command(label="Brush Size", command=self.change_brush_size)

        self.AI_menu = tk.Menu(self.menu, tearoff=0)
        self.menu.add_cascade(label="AI Tools", menu=self.AI_menu)
        self.AI_menu.add_command(label="Detect", command=self.detect_canvas)
        # self.AI_menu.add_command(label="Brush Color", command=self.choose_color)
        # self.AI_menu.add_command(label="Brush Size", command=self.change_brush_size)

    def paint(self, event):
        if self.old_x and self.old_y:
            self.canvas.create_line(self.old_x, self.old_y, event.x, event.y,
                                    width=self.brush_size, fill=self.brush_color,
                                    capstyle=tk.ROUND, smooth=tk.TRUE)

        self.old_x = event.x
        self.old_y = event.y

    def reset(self, event):
        self.old_x = None
        self.old_y = None

    def clear_canvas(self):
        self.canvas.delete("all")

    def detect_canvas(self):
        def encode_image(image_path):
            with open(image_path, "rb") as image_file:
                return base64.b64encode(image_file.read()).decode('utf-8')

        x = self.root.winfo_rootx()
        y = self.root.winfo_rooty()
        x1 = x + self.canvas.winfo_width()
        y1 = y + self.canvas.winfo_height()

        image_path = r'D:\Clavis_Projects\fun\detect\detect.png'
        ImageGrab.grab().crop((x, y, x1, y1)).save(image_path)
        base64_image = encode_image(image_path)

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer <API-KEY>"
        }

        payload = {
            "model": "gpt-4-vision-preview",
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": "1 line answer for what this hand drawn image looks like."
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{base64_image}"
                            }
                        }
                    ]
                }
            ],
            "max_tokens": 300
        }

        # response_text = send_text_and_image_prompt(image_path)
        response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)

        desc = response.json()['choices'][0]['message']['content']

        self.canvas.create_text(400, 50, text=desc, font=("Arial", 16), fill="black")

    def save_as_png(self):
        x = self.root.winfo_rootx() + self.canvas.winfo_x()
        y = self.root.winfo_rooty() + self.canvas.winfo_y()
        x1 = x + self.canvas.winfo_width()
        y1 = y + self.canvas.winfo_height()

        ImageGrab.grab().crop((x, y, x1, y1)).save("drawing.png")

    def choose_color(self):
        self.brush_color = colorchooser.askcolor(color=self.brush_color)[1]

    def change_brush_size(self):
        size = tk.simpledialog.askinteger("Brush size", "Enter brush size (1-50)", minvalue=1, maxvalue=50)
        if size:
            self.brush_size = size


if __name__ == "__main__":
    root = tk.Tk()
    app = DrawingApp(root)
    root.mainloop()
