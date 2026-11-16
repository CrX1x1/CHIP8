import tkinter as tk

class SpriteEditor:
    def __init__(self, root):
        self.root = root
        self.root.title("Sprite Editor")
        self.root.configure(bg="#000000")

        self.width = 8
        self.height = 8
        self.scale = 30
        self.data = [[0] * self.width for _ in range(15)]
        self.draw_mode = 1 #maybe 1 for draw, 0 for erase

        self.setup_ui()
        self.draw_grid()
        self.update()

    def setup_ui(self):
        controls = tk.Frame(self.root, bg="#000000")
        controls.pack(padx=10, pady=10)
        tk.Label(controls, text="Sprite Editor", bg="#000000", fg="#FFFFFF").pack()
        self.height_label = tk.IntVar(value=8)
        height_spin = tk.Spinbox(controls, from_=1, to=15, textvariable=self.height_label, command=self.change_height)
        height_spin.pack()
        #clear and invert button
        tk.Button(controls, text="Clear", command=self.clear_grid).pack()
        tk.Button(controls, text="Invert", command=self.invert).pack()
        self.canvas = tk.Canvas(
            self.root,
            width=self.width * self.scale,
            height=self.height * self.scale,
            bg="#000000",
            highlightthickness=0
        )
        self.canvas.pack(padx=10, pady=10)
        self.canvas.bind("<Button-1>", self.on_click)
        self.canvas.bind("<B1-Motion>", self.on_drag)

        #output box
        self.output = tk.Text(self.root, height=10, width=50, font=("Consolas", 10))
        self.output.pack(padx=10, pady=10)
        self.copy_button = tk.Button(self.root, text="Copy", command=self.copy)
        self.copy_button.pack(padx=10, pady=10)
    def change_height(self):
        try:
            val = int(self.height_label.get())
            self.height = max(1, min(val, 15))
        except ValueError:
            self.height = 8
        self.draw_grid()
        self.update()
    def draw_grid(self):
        self.canvas.delete("all")
        self.canvas.config(height = self.height * self.scale)
        for y in range(self.height):
            for x in range(self.width):
                self.canvas.create_rectangle(
                    x * self.scale,
                    y * self.scale,
                    (x + 1) * self.scale,
                    (y + 1) * self.scale,
                    fill="#FFFFFF" if self.data[y][x] else "#333333",
                    outline="#666666"
                )
    def get_cell(self, event):
        r = event.x // self.scale
        c = event.y // self.scale
        if 0 <= r < self.width and 0 <= c < self.height:
            return (c, r)
        return None, None
    def on_click(self, event):
        r, c = self.get_cell(event)
        if r is not None and c is not None:
            self.draw_mode = 0 if self.data[r][c] else 1
            self.data[r][c] = self.draw_mode
            self.draw_grid()
            self.update()
    def on_drag(self, event):
        r, c = self.get_cell(event)
        if r is not None and c is not None and self.data[r][c] != self.draw_mode:
            self.data[r][c] = self.draw_mode
            self.draw_grid()
            self.update()
    def clear_grid(self):
        self.data = [[0 for _ in range(self.width)] for _ in range(self.height)]
        self.draw_grid()
        self.update()
    def invert(self):
        for r in range(self.height):
            for c in range(self.width):
                self.data[r][c] ^= 0x1
        self.draw_grid()
        self.update()
    def draw(self):
        self.canvas.delete("all")
        for y in range(self.height):
            for x in range(self.width):
                self.canvas.create_rectangle(
                        x * self.scale,
                        y * self.scale,
                        (x + 1) * self.scale,
                        (y + 1) * self.scale,
                        fill="#FFFFFF" if self.data[y][x] else "#333333",
                        outline=""
                )
                

    def update(self):
        byte_list = []
        for r in range(self.height):
            binstr = "".join(str(bit) for bit in self.data[r])
            byte_list.append(f"0x{int(binstr, 2):02X}")
        formatted = f"{' '.join(byte_list)}"
        self.output.delete(1.0, tk.END)
        self.output.insert(tk.END, formatted)

    def copy(self):
        data = self.output.get(1.0, tk.END).strip()
        self.root.clipboard_clear()
        self.root.clipboard_append(data)
        self.copy_button.config(text="Copied!")
        self.root.after(2000, lambda: self.copy_button.config(text="Copy"))
root = tk.Tk()
app = SpriteEditor(root)
root.mainloop()