import tkinter as tk
from tkinter.ttk import *
from tkinter import *
from tkinter import filedialog, messagebox, Canvas, Button, Frame, Label, Scale, HORIZONTAL, Scrollbar
from PIL import Image, ImageTk, ImageOps, ImageEnhance, ImageFilter, ImageDraw
from utils import open_image, crop_image, rotate_90_cw, rotate_90_ccw, save_image, on_drag, on_press, on_release, open_new_window, revert_to_original
from filters_file import apply_bw, apply_sharpen, apply_blur, apply_sepia, apply_warmer, apply_smoothen_filter
from adjustment import apply_brightness, apply_contrast, apply_sharpness, apply_temperature, apply_saturation
from sidebar_operations import show_filter_sidebar, show_adjust_sidebar, hide_adjust_sidebar, hide_filter_sidebar, create_filter_option, create_adjustment_option, adjustment_sidebar_canvas, create_adjustment_slider_option, create_icon_button
from toggler_sidebars import toggle_sidebar, toggle_draw_sidebar, toggle_adjust_sidebar

# Functions
image = None
crop_rect = None
canvas_width = 1450
canvas_height = 840

def update_image_display(image):
    global image_on_canvas, scaled_image

    # Get current canvas dimensions dynamically
    current_width = canvas.winfo_width()
    current_height = canvas.winfo_height()

    # Fallback to default dimensions if not set yet
    if current_width <= 1 or current_height <= 1:
        current_width = canvas_width
        current_height = canvas_height

    # Clear the canvas
    canvas.delete("all")

    # Calculate the scaling factor
    scale_x = current_width / image.width
    scale_y = current_height / image.height
    scale_factor = min(scale_x, scale_y)

    # Resize the image
    new_width = int(image.width * scale_factor)
    new_height = int(image.height * scale_factor)
    scaled_image = image.resize((new_width, new_height), Image.Resampling.LANCZOS)

    # Center the image on the canvas
    image_on_canvas = ImageTk.PhotoImage(scaled_image)
    canvas.create_image(
        (current_width - new_width) // 2,
        (current_height - new_height) // 2,
        anchor="nw",
        image=image_on_canvas
    )

def on_mouse_wheel(event, canvas):
    canvas.yview_scroll(int(-1*(event.delta/120)), "units")

# GUI code
root = tk.Tk()
root.title('Photo Custom')
root.attributes("-fullscreen", True)  # Make the window fullscreen
root.geometry("1920x1080")

canvas_width = 1450
canvas_height = 840

# Dark Mode Colors
dark_bg = "#1E1E1E"
dark_sidebar = "#2A2A2A"
dark_button = "#3B3B3B"
button_hover = "#4B4B4B"
button_active = "#555555"
dark_text = "#F0F0F0"
highlight_color = "#4CAF50"  # For highlight buttons

frame_bg = "#252525"
button_color = "#292929"
font_fg = "#FFFFFF"

# Change the root background to dark mode
root.configure(bg=dark_bg)

# Menu (Updated with dark theme)
menu_font = ("Poppins", 16)

menubar = tk.Menu(root, bg=dark_sidebar, fg=dark_text, activebackground="#444444", activeforeground=dark_text)
file = tk.Menu(menubar, tearoff=0, bg=dark_sidebar, fg=dark_text)
menubar.add_cascade(label='File', menu=file)
file.add_command(label='Open', command=open_image)
file.add_command(label='Save', command=save_image)
file.add_separator()
file.add_command(label='Exit', command=root.quit)

edit = tk.Menu(menubar, tearoff=0, font=menu_font, bg=dark_sidebar, fg=dark_text)
menubar.add_cascade(label='Edit', menu=edit)
edit.add_command(label="Revert to Original", command=revert_to_original)

tools = tk.Menu(menubar, tearoff=0, font=menu_font, bg=dark_sidebar, fg=dark_text)
menubar.add_cascade(label='Tools', menu=tools)
tools.add_command(label='Crop', accelerator='shift+x', command=crop_image)
tools.add_separator()
tools.add_command(label='Rotate 90º CW', command=rotate_90_cw)
tools.add_command(label="Rotate 90 CCW", command=rotate_90_ccw)

root.config(menu=menubar)

# Sidebar for filters with scrollable functionality
sidebar_canvas = Canvas(root, width=150, height=canvas_height, bg=dark_sidebar)
sidebar_scrollbar = Scrollbar(root, orient="vertical", command=sidebar_canvas.yview)

sidebar_frame = Frame(sidebar_canvas, bg=dark_sidebar)

# Configure canvas and scrollbar
sidebar_canvas.configure(yscrollcommand=sidebar_scrollbar.set)
sidebar_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
sidebar_canvas.create_window((0, 0), window=sidebar_frame, anchor="nw")

# Add a function to update the scrolling region
def update_scroll_region(event):
    sidebar_canvas.config(scrollregion=sidebar_canvas.bbox("all"))

sidebar_frame.bind("<Configure>", update_scroll_region)
# Bind the mouse wheel event to the sidebar canvas for vertical scrolling
sidebar_canvas.bind_all("<MouseWheel>", lambda event, canvas=sidebar_canvas: on_mouse_wheel(event, canvas))

# Pack the sidebar canvas
sidebar_canvas.pack(side=tk.LEFT, fill=tk.Y)

# ----------------------filter sidebar canvas -----------------------
# Example filter creation
bw_image_path = r"C:\Users\HP\OneDrive\Pictures\b&w.jpeg"  # Replace with your image path
bw_filter = create_filter_option(sidebar_frame, bw_image_path, "B&W", apply_bw)

warmer_image_path = r"C:\Users\HP\OneDrive\Pictures\warm-contrast.jpeg"
warmer_filter = create_filter_option(sidebar_frame, warmer_image_path, "Warm Contrast", apply_warmer)

blur_image_path = r"C:\Users\HP\OneDrive\Pictures\blur.jpeg"
blur_filter = create_filter_option(sidebar_frame, blur_image_path, "Blur", apply_blur)

sharpen_film_path = r"C:\Users\HP\OneDrive\Pictures\sharpen.jpeg"
sharpen_filter = create_filter_option(sidebar_frame, sharpen_film_path, "Sharpen", apply_sharpen)

sepia_image_path = r"C:\Users\HP\OneDrive\Pictures\sepia2.jpg"
sepia_filter = create_filter_option(sidebar_frame, sepia_image_path, "Sepia", apply_sepia)

smooth_image_path = r"C:\Users\HP\OneDrive\Pictures\golden.jpeg"
smooth_filter = create_filter_option(sidebar_frame, smooth_image_path, "Smooth", apply_smoothen_filter)


#Main Frame container
main_frame = tk.Frame(root, bg=dark_bg)
main_frame.pack(fill=tk.Y, side=tk.LEFT)

#Resize frame
resize_frame = tk.Frame(main_frame, bg=dark_bg)
resize_frame.pack(side=tk.TOP, fill=tk.X)

resize_button = Button(resize_frame, text="Resize", command=open_new_window, font=("Poppins", 14), bg=highlight_color, fg=dark_text, relief="flat")
resize_button.pack(side=tk.TOP, pady=10, padx=10)

#Filter Frame
filter_frame = tk.Frame(main_frame, bg=dark_bg)
filter_frame.pack(side=tk.TOP, fill=tk.X)

# Filter menu (Button on the left side)
filter_button = Button(filter_frame, text="Filters", command=toggle_sidebar, font=("Poppins", 14), bg=highlight_color, fg=dark_text, relief="flat")
filter_button.pack(side=tk.TOP, pady=10, padx=10)

#Load icon Path
resize_icon_path = r"E:/PyCharm Community Edition 2024.2.1/PythonProjects/photo_customize/assests/Transform.png"
filter_icon_path = r"E:/PyCharm Community Edition 2024.2.1/PythonProjects/photo_customize/assests/Color Swatch 01.png"
adjust_icon_path = r"E:/PyCharm Community Edition 2024.2.1/PythonProjects/photo_customize/assests/Filters 1.png"
draw_icon_path = r"E:/PyCharm Community Edition 2024.2.1/PythonProjects/photo_customize/assests/Color Picker.png"

# Load and resize images for buttons
resize_icon = Image.open(resize_icon_path).resize((30,30))
filter_icon = Image.open(filter_icon_path).resize((30,30))
adjust_icon = Image.open(adjust_icon_path).resize((30,30))
draw_icon = Image.open(draw_icon_path).resize((30,30))

#convert to Tkinter-compatible images
resize_icon_tk = ImageTk.PhotoImage(resize_icon)
filter_icon_tk = ImageTk.PhotoImage(filter_icon)
adjust_icon_tk = ImageTk.PhotoImage(adjust_icon)
draw_icon_tk = ImageTk.PhotoImage(draw_icon)

#adjustment sidebar
adjustment_sidebar_canvas = Canvas(root, width=150, height=canvas_height,background=frame_bg)
adjustment_sidebar_frame = Frame(adjustment_sidebar_canvas,background=frame_bg)

adjustment_sidebar_canvas.create_window((0, 0), window=adjustment_sidebar_frame, anchor="nw")

#Adjustment effects
adjust_frame = tk.Frame(main_frame, background=frame_bg)
adjust_frame.pack(side=tk.TOP, fill=tk.X)

#Create slider for adjustments
brightness_slider = create_adjustment_slider_option(adjustment_sidebar_frame, "Brightness", apply_brightness)
contrast_slider = create_adjustment_slider_option(adjustment_sidebar_frame, "Contrast", apply_contrast)
saturation_slider = create_adjustment_slider_option(adjustment_sidebar_frame, "Saturation", apply_saturation)
sharpness_slider = create_adjustment_slider_option(adjustment_sidebar_frame, "Sharpness", apply_sharpness)
temperature_slider = create_adjustment_slider_option(adjustment_sidebar_frame, "Temperature", apply_temperature)

#--------------Drawing tools-------------------
is_drawing = False
drawing_color = "black"
line_width = 2

# Frame for Draw Sidebar

draw_sidebar_canvas = Canvas(root, width=150, height=canvas_height, background=frame_bg)
draw_sidebar_frame = Frame(draw_sidebar_canvas, background=frame_bg)

# Create the drawing sidebar
draw_sidebar_canvas.create_window((0, 0), window=draw_sidebar_frame, anchor="nw")

# Frame for Draw Sidebar
draw_frame = tk.Frame(main_frame,background=frame_bg)
draw_frame.pack(side=tk.TOP, fill=tk.X)


# Modern Buttons with Icons and Text
create_icon_button(resize_frame, resize_icon_tk, "Resize", open_new_window)
create_icon_button(filter_frame, filter_icon_tk, "Filter", toggle_sidebar)
create_icon_button(adjust_frame, adjust_icon_tk, "Adjust", toggle_adjust_sidebar)
create_icon_button(draw_frame, draw_icon_tk, "Draw", toggle_draw_sidebar)

#---------------Canvas----------------
# Canvas for image display (Expands to the right of the sidebar)
canvas = Canvas(root, bg="#030303", width=canvas_width, height=canvas_height, relief="solid", borderwidth=2)
canvas.pack(fill=tk.BOTH, expand=True, side=tk.LEFT)

# Mouse events for cropping
canvas.bind("<ButtonPress-1>", on_press)  # Left mouse button press to start cropping
canvas.bind("<B1-Motion>", on_drag)  # Dragging the mouse while holding the left button
canvas.bind("<ButtonRelease-1>", on_release)  # Left mouse button release to finalize cropping
canvas.bind("<Configure>", lambda event: update_image_display(image))

root.mainloop()
