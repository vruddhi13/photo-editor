import tkinter as tk
from tkinter.ttk import *
from tkinter import *
from tkinter import filedialog, messagebox, Canvas, Button, Frame, Label,Scale, HORIZONTAL
from PIL import Image, ImageTk, ImageOps, ImageEnhance, ImageFilter, ImageDraw
from networkx.algorithms.isomorphism.tree_isomorphism import root_trees

from main import update_image_display


scaled_image=None
canvas_width = 1450
canvas_height = 840

root = Tk()

# Canvas for image display (Expands to the right of the sidebar)
canvas = Canvas(root, bg="darkgrey", width=canvas_width, height=canvas_height, relief="solid", borderwidth=2)
canvas.pack(fill=tk.BOTH, expand=True, side=tk.LEFT)


def open_image():
    global image, original_image, image_path
    image_path = filedialog.askopenfilename(filetypes=[("Image Files", "*.jpeg *.jpg *.png *.gif")])
    if image_path:
        image = Image.open(image_path)
        original_image = image.copy()  # Save a copy of the original image
        update_image_display(image)

def save_image():
    global image
    if image:
        file_path = filedialog.asksaveasfilename(defaultextension=".png", filetypes=[("PNG files", "*.png"), ("JPEG files", "*.jpg")])
        if file_path:
            image.save(file_path)
            messagebox.showinfo("Save", "Image saved successfully")

# Edit menu revert to original
def revert_to_original():
    global image,image_path
    if image_path:
        image = Image.open(image_path)
        update_image_display(image)
    else:
        messagebox.showerror(image)

# Crop image
def crop_image():
    global image, crop_rect
    if image and crop_rect:
        x1, y1, x2, y2 = crop_rect # ex: x1=200, y1=150, x2=350, y2=250

        # convert canvas coordinates to original image coordinates
        offset_x = (canvas_width - scaled_image.width) // 2 # 0
        offset_y = (canvas_height - scaled_image.height) // 2 # 0

        x1 = max(0, x1 - offset_x) # 200 - 0 = 200
        y1 = max(0, y1 - offset_y) # 150 - 0 = 150
        x2 = max(0, x2 - offset_x) # 350 - 0 = 350
        y2 = max(0, y2 - offset_y) # 250 - 0 = 250

        scale_factor = scaled_image.width / image.width

        x1 = int(x1 / scale_factor) # 200 / 0.5 = 400
        y1 = int(y1 / scale_factor) # 150 / 0.5 = 300
        x2 = int(x2 / scale_factor) # 350 / 0.5 = 700
        y2 = int(y2 / scale_factor) # 250 / 0.5 = 500

        if x1<x2 and y1<y2: # 400<700 and 300<500   In this case, 400 < 700 is True, meaning the top-left corner is indeed to the left of the bottom-right corner horizontally.
            cropped_image = image.crop((x1,y1, x2,y2)) # Crops the image from (400, 300) to (700, 500)
            update_image_display(cropped_image)
            image = cropped_image
        else:
            messagebox.showerror("Invalid Selection", "Please select a valid crop area.")

#Mouse drag to create a rectangle for cropping
def on_press(event):
    global crop_rect
    crop_rect = (event.x, event.y, event.x, event.y) #Initialize crop rectangle

def on_drag(event):
    global crop_rect
    crop_rect = (crop_rect[0], crop_rect[1], event.x, event.y)
    redraw_crop_rectangle()

def on_release(event):
    redraw_crop_rectangle() # Crop the image when mouse is released

def redraw_crop_rectangle():
    canvas.delete("crop_rect")
    if crop_rect:
        x1, y1, x2, y2 = crop_rect
        canvas.create_rectangle(x1, y1, x2, y2, outline="red", width=2, tags="crop_rect")


# rotate image 90 degree clockwise
def rotate_90_cw():
    global image
    if image:
        image = image.rotate(-90, expand=True)
        update_image_display(image)

# rotate image 90 degrees CounterClockWise
def rotate_90_ccw():
    global image
    if image:
        image = image.rotate(90, expand=True)
        update_image_display(image)

# open new window with resize button click event on
def open_new_window():
    newWindow = tk.Toplevel(root)
    newWindow.title("Resize Image")
    newWindow.geometry("300x200")

    width_label = Label(newWindow, text="Width (px)")
    width_label.pack(pady=10)

    width_textbox = tk.Text(newWindow, height=1, width=10)
    width_textbox.pack()

    height_label = Label(newWindow, text="Height (px)")
    height_label.pack(pady=10)

    height_textbox = tk.Text(newWindow, height=1, width=10)
    height_textbox.pack()

    def resize_img():
        global image
        if image:
            # Get width and height from textboxes
            width = int(width_textbox.get("1.0", "end-1c"))  # Remove extra newline character
            height = int(height_textbox.get("1.0", "end-1c"))

            # resize the already opened image
            resized_image = image.resize((width, height), Image.Resampling.LANCZOS)
            update_image_display(resized_image)
            image = resized_image

    submit = Button(newWindow, text="Submit", command=resize_img)
    submit.pack(pady=10)