import tkinter as tk
from tkinter.colorchooser import askcolor
from PIL import Image, ImageTk

# Initialize global variables
current_color = "black"
pen_size = 5
current_tool = "pen"
canvas_objects = {}  # Store objects added to the canvas (e.g., stickers)
current_object = None
start_x, start_y = 0, 0

# Functions
def set_pen_color():
    """Choose a color for the pen."""
    global current_color
    color = askcolor()[1]
    if color:
        current_color = color

def set_pen_size(size):
    """Set the pen size."""
    global pen_size
    pen_size = size

def set_tool(tool):
    """Set the current tool (pen, eraser, select)."""
    global current_tool
    current_tool = tool

def draw(event):
    """Draw on the canvas."""
    if current_tool == "pen":
        x, y = event.x, event.y
        canvas.create_line(x, y, event.x + 1, event.y + 1, fill=current_color, width=pen_size, capstyle=tk.ROUND)
    elif current_tool == "eraser":
        x, y = event.x, event.y
        canvas.create_line(x, y, x + 1, y + 1, fill="white", width=pen_size, capstyle=tk.ROUND)

def add_sticker(image_path):
    """Add a sticker to the canvas."""
    global canvas_objects
    x, y = canvas.winfo_width() // 2, canvas.winfo_height() // 2
    sticker_image = Image.open(image_path).resize((100, 100), Image.LANCZOS)
    sticker_tk = ImageTk.PhotoImage(sticker_image)
    sticker_id = canvas.create_image(x, y, image=sticker_tk, anchor="center", tags="sticker")
    canvas_objects[sticker_id] = {"image": sticker_tk, "original_image": sticker_image}

    # Bind events for the sticker
    canvas.tag_bind(sticker_id, "<ButtonPress-1>", lambda e, obj=sticker_id: on_object_press(e, obj))
    canvas.tag_bind(sticker_id, "<B1-Motion>", lambda e, obj=sticker_id: on_object_drag(e, obj))

def on_object_press(event, obj):
    """Handle object press for dragging."""
    global current_object, start_x, start_y
    current_object = obj
    start_x, start_y = event.x, event.y

def on_object_drag(event, obj):
    """Handle dragging an object."""
    global start_x, start_y
    dx = event.x - start_x
    dy = event.y - start_y
    canvas.move(obj, dx, dy)
    start_x, start_y = event.x, event.y

def clear_canvas():
    """Clear the entire canvas."""
    canvas.delete("all")

# GUI Setup
root = tk.Tk()
root.title("Basic Whiteboard")
root.geometry("1000x700")

# Toolbar
toolbar = tk.Frame(root, bg="lightgrey", height=50)
toolbar.pack(side=tk.TOP, fill=tk.X)

# Pen Color Button
color_button = tk.Button(toolbar, text="Color", command=set_pen_color)
color_button.pack(side=tk.LEFT, padx=5, pady=5)

# Pen Size Options
pen_size_label = tk.Label(toolbar, text="Pen Size:")
pen_size_label.pack(side=tk.LEFT, padx=5)
for size in [2, 5, 10, 20]:
    tk.Button(toolbar, text=str(size), command=lambda s=size: set_pen_size(s)).pack(side=tk.LEFT, padx=2)

# Tool Options
pen_button = tk.Button(toolbar, text="Pen", command=lambda: set_tool("pen"))
pen_button.pack(side=tk.LEFT, padx=5)

eraser_button = tk.Button(toolbar, text="Eraser", command=lambda: set_tool("eraser"))
eraser_button.pack(side=tk.LEFT, padx=5)

# Sticker Button
sticker_button = tk.Button(toolbar, text="Add Sticker", command=lambda: add_sticker("path_to_your_sticker_image.png"))
sticker_button.pack(side=tk.LEFT, padx=5)

# Clear Canvas Button
clear_button = tk.Button(toolbar, text="Clear", command=clear_canvas)
clear_button.pack(side=tk.RIGHT, padx=5)

# Canvas
canvas = tk.Canvas(root, bg="white", width=800, height=600)
canvas.pack(fill=tk.BOTH, expand=True)
canvas.bind("<B1-Motion>", draw)

root.mainloop()
