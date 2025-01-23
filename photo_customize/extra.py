import tkinter as tk
from tkinter.ttk import *
from tkinter import *
from tkinter import filedialog, messagebox, Canvas, Button, Frame, Label,Scale, HORIZONTAL
from PIL import Image, ImageTk, ImageOps, ImageEnhance, ImageFilter, ImageDraw
from tkinter.colorchooser import askcolor


# Functions

crop_rect = None
canvas_width = 1450
canvas_height = 840
canvas =None
original_image=None
scale_factor = 1
is_drawing = False
drawing_layer = None
image = None
draw = None
is_erasing = False
prev_x, prev_y = None, None
x_offset = 0
y_offset = 0

eraser_size = 10

def update_image_display(image):
    global image_on_canvas, scaled_image, scale_factor, x_offset, y_offset, drawing_layer

    # Get current canvas dimensions dynamically
    current_width = canvas.winfo_width()
    current_height = canvas.winfo_height()

    # Fallback to default dimensions if not set yet
    if current_width <= 1 or current_height <= 1:
        current_width = canvas_width
        current_height = canvas_height

    # Calculate the scaling factors for width and height
    scale_x = current_width / image.width
    scale_y = current_height / image.height

    # Use the smaller scaling factor to maintain aspect ratio
    scale_factor = min(scale_x, scale_y)

    # Resize the image
    new_width = int(image.width * scale_factor)
    new_height = int(image.height * scale_factor)
    scaled_image = image.resize((new_width, new_height), Image.Resampling.LANCZOS)

    # Calculate offsets for centering the image on the canvas
    x_offset = (current_width - new_width) // 2
    y_offset = (current_height - new_height) // 2

    # Ensure the drawing layer matches the size of the scaled image
    drawing_layer = drawing_layer.resize(scaled_image.size)

    # Ensure both images are in RGBA mode
    scaled_image_rgba = scaled_image.convert("RGBA")
    drawing_layer_rgba = drawing_layer.convert("RGBA")

    # Alpha composite the drawing layer onto the scaled image
    combined_image = Image.alpha_composite(scaled_image_rgba, drawing_layer_rgba)

    # Convert the combined image to Tkinter-compatible format
    combined_image_tk = ImageTk.PhotoImage(combined_image)

    # Clear the canvas and display the updated image
    canvas.delete("all")
    canvas.create_image(x_offset, y_offset, anchor="nw", image=combined_image_tk)
    canvas.image = combined_image_tk

    # Debugging outputs to confirm calculations
    # print("Canvas Dimensions:", current_width, current_height)
    # print("Original Image Dimensions:", image.width, image.height)
    # print("Scaled Image Dimensions:", new_width, new_height)
    # print("Scale Factor:", scale_factor)
    # print("Offsets:", x_offset, y_offset)


def open_image():
    global image, original_image, image_path, draw1,drawing_layer
    image_path = filedialog.askopenfilename(filetypes=[("Image Files", "*.jpeg *.jpg *.png *.gif")])
    if image_path:
        image = Image.open(image_path).convert("RGBA")
        drawing_layer = Image.new("RGBA", image.size, (0, 0, 0, 0))  # Create a transparent drawing layer
        draw1 = ImageDraw.Draw(drawing_layer)  # Create a drawing object
        update_image_display(image)

def save_image():
    global image
    if image:
        file_path = filedialog.asksaveasfilename(defaultextension=".png", filetypes=[("PNG files", "*.png"), ("JPEG files", "*.jpg")])
        if file_path:
            image.save(file_path)

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

#Filters

def apply_bw():
    global image
    if image:
        grayscale_img = ImageOps.grayscale(image)
        image = grayscale_img
        update_image_display(grayscale_img)

def apply_warmer():
    global image
    if image:
        enhancer = ImageEnhance.Color(image)
        warm_img = enhancer.enhance(1.5)
        image = warm_img

        # Convert the image to PhotoImage for display in Tkinter
        image_tk = ImageTk.PhotoImage(warm_img)

        # Update the displayed image
        update_image_display(warm_img)

def apply_blur():
    global image
    if image:
        #Apply gaussian blur to image
        blured_img = image.filter(ImageFilter.GaussianBlur(radius=3))
        image = blured_img

        update_image_display(blured_img)

def apply_sepia():
    global image
    if image:
        if image.mode != "RGB":
            image = image.convert("RGB")
        #Apply sepia filter
        sepia_filter = ImageEnhance.Color(image).enhance(0.5)
        sepia_image = ImageEnhance.Brightness(sepia_filter).enhance(0.9)
        image = sepia_image

        update_image_display(sepia_image)

def apply_sharpen():
    global image
    if image:
        if image.mode != 'RGB':
            image = image.convert("RGB")

        #Apply sharpen filter
        sharpen_filter = image.filter(ImageFilter.SHARPEN)
        image = sharpen_filter
        update_image_display(sharpen_filter)

def apply_smoothen_filter():
    global image
    if image:
        if image.mode != "RGB":
            image = image.convert("RGB")

        smooth_filter = image.filter(ImageFilter.SMOOTH)
        image = smooth_filter
        update_image_display(smooth_filter)

# Sidebar and Canvas for filter
def show_filter_sidebar():
    global canvas_width
    # Show the sidebar with filter buttons
    sidebar_canvas.pack(side=tk.LEFT, fill=tk.Y, padx=10)
    canvas_width = 1170  # Adjust the canvas width to accommodate the sidebar
    canvas.config(width=canvas_width)
    update_image_display(image)

def hide_filter_sidebar():
    global canvas_width
    # Hide the sidebar
    sidebar_canvas.pack_forget()
    canvas_width = 1450  # Reset canvas width when sidebar is hidden
    canvas.config(width=canvas_width)
    update_image_display(image)

#sidebar for adjustment
def show_adjust_sidebar():
    global canvas_width
    adjustment_sidebar_canvas.pack(side=tk.LEFT, fill=tk.Y, padx=10)
    canvas_width = 1150
    canvas.config(width=canvas_width)
    update_image_display(image)

def hide_adjust_sidebar():
    global canvas_width
    #Hide the adjustment sidebar
    adjustment_sidebar_canvas.pack_forget()
    canvas_width=1450
    canvas.config(width=canvas_width)
    update_image_display(image)

def show_draw_sidebar():
    global canvas_width
    draw_sidebar_canvas.pack(side=tk.LEFT, fill=tk.Y, padx=10)
    canvas_width=1150
    canvas.config(width=canvas_width)
    update_image_display(image)

def hide_draw_sidebar():
    global canvas_width
    #hide the sidebar of draw
    draw_sidebar_canvas.pack_forget()
    canvas_width=1450
    canvas.config(width=canvas_width)
    update_image_display(image)


# Function to apply brightness adjustment
def apply_brightness(value):
    global image, original_image
    if image:
        # Convert the slider value to a scale (e.g., 0.5 to 1.5)
        factor = float(value)

        # If it's the first time we are adjusting, save the original image
        if not hasattr(apply_brightness, 'original_image_saved'):
            original_image = image.copy()
            apply_brightness.original_image_saved = True

        # If the factor is less than 1.0, apply darkening (decrease brightness)
        # If the factor is greater than 1.0, apply brightening (increase brightness)
        enhancer = ImageEnhance.Brightness(original_image)  # Use original image as base
        enhanced_image = enhancer.enhance(factor)

        image = enhanced_image  # Update the global image to the new adjusted image
        update_image_display(enhanced_image)


# Function to reset the image to original (if needed)
def reset_brightness():
    global image, original_image
    if original_image:
        image = original_image.copy()  # Reset to the original state
        update_image_display(image)

        # Reset the slider to the default (1.0 for no change)
        brightness_slider.set(1.0)  # Reset slider position to no change


# Function to apply contrast adjustment
def apply_contrast(value):
    global image, original_image
    if image:
        # Convert the slider value to a float (contrast factor)
        factor = float(value)

        # If it's the first time we are adjusting, save the original image
        if not hasattr(apply_contrast, 'original_image_saved'):
            original_image = image.copy()  # Save the original image for reference
            apply_contrast.original_image_saved = True

        # Apply the contrast enhancement based on the original image
        enhancer = ImageEnhance.Contrast(original_image)  # Use the original image as the base
        enhanced_image = enhancer.enhance(factor)  # Apply the contrast factor

        image = enhanced_image  # Update the global image to the new adjusted image
        update_image_display(enhanced_image)  # Display the enhanced image



def apply_saturation(value):
    global image, original_image
    if image:
        # Convert the slider value to a float (contrast factor)
        factor = float(value)

        # If it's the first time we are adjusting, save the original image
        if not hasattr(apply_saturation, 'original_image_saved'):
            original_image = image.copy()  # Save the original image for reference
            apply_saturation.original_image_saved = True

        # Apply the contrast enhancement based on the original image
        enhancer = ImageEnhance.Color(original_image)  # Use the original image as the base
        enhanced_image = enhancer.enhance(factor)  # Apply the contrast factor

        image = enhanced_image  # Update the global image to the new adjusted image
        update_image_display(enhanced_image)  # Display the enhanced image

def apply_sharpness(value):
    global image, original_image
    if image:
        # Convert the slider value to a float (contrast factor)
        factor = float(value)

        # If it's the first time we are adjusting, save the original image
        if not hasattr(apply_sharpness, 'original_image_saved'):
            original_image = image.copy()  # Save the original image for reference
            apply_sharpness.original_image_saved = True

        # Apply the contrast enhancement based on the original image
        enhancer = ImageEnhance.Sharpness(original_image)  # Use the original image as the base
        enhanced_image = enhancer.enhance(factor)  # Apply the contrast factor

        image = enhanced_image  # Update the global image to the new adjusted image
        update_image_display(enhanced_image)  # Display the enhanced image

def apply_temperature(value):
    global image, original_image
    if image:
        # Convert the image to RGB to manipulate the color channels
        rgb_image = original_image.convert('RGB')  # Use the original image for adjustments
        r, g, b = rgb_image.split()  # Split the channels

        factor = float(value)  # The temperature factor from the slider

        if factor > 1.0:
            # Warm effect: Increase red channel, decrease blue channel
            r = r.point(lambda i: min(255, i * factor))
            b = b.point(lambda i: max(0, i / factor))
        elif factor < 1.0:
            # Cool effect: Decrease red channel, increase blue channel
            r = r.point(lambda i: max(0, i * factor))
            b = b.point(lambda i: min(255, i / factor))

        # Merge the channels back to create the adjusted image
        adjusted_image = Image.merge("RGB", (r, g, b))
        image = adjusted_image  # Update the global image to the adjusted one
        update_image_display(adjusted_image)  # Display the adjusted image

def create_filter_option(parent, image_path, filter_name, command):
    """Creates a styled filter option with an image and a label."""
    # Frame to hold the image and label
    frame = Frame(parent, bg="#292828", width=120, height=150, highlightbackground="white", highlightthickness=1)
    frame.pack_propagate(False)  # Disable resizing to maintain fixed size
    frame.pack(pady=10, padx=10)

    # Load and display the image
    img = Image.open(image_path).resize((100, 100), Image.Resampling.LANCZOS)
    photo = ImageTk.PhotoImage(img)
    img_label = Label(frame, image=photo, bg="black")
    img_label.image = photo  # Store reference to avoid garbage collection
    img_label.pack(pady=5)

    # Add the filter name label
    text_label = Label(frame, text=filter_name, bg="black", fg="white", font=("Arial", 10))
    text_label.pack()

    # Bind a click event to the entire frame
    img_label.bind("<Button-1>", lambda e: command())

    return frame


def create_adjustment_option(parent,name, command):
    frame = Frame(parent, bg="#292828", width=120, height=50, highlightbackground="white", highlightthickness=0)
    frame.pack_propagate(False)
    frame.pack(pady=10, padx=10)

    #add the adjustment label
    text_label = Label(frame, text=name, bg="black", fg="white", font=('Arial',10))
    text_label.pack()

    #bind click event to button
    button = Button(frame, text="Apply", command=command)
    button.pack()

    return frame


def on_mouse_wheel(event, canvas):
    canvas.yview_scroll(int(-1*(event.delta/120)), "units")

def on_hover(event):
    event.widget.config(bg="#282828")  # Lighter shade on hover

def on_leave(event):
    event.widget.config(bg=button_color)  # Reset to original color

#Adjustment Slider
# Function to create a slider for adjustment (brightness, contrast, etc.)

def create_adjustment_slider_option(parent, label_text, command, from_=0.5, to=2.0):
    frame = tk.Frame(parent, bg=frame_bg)
    frame.pack(fill=tk.X, pady=5, padx=15)

    label = tk.Label(frame, text=label_text, bg=frame_bg, fg=font_fg)
    label.pack(side=tk.TOP, anchor="w")

    slider = tk.Scale(
        frame,
        from_=from_,
        to=to,
        resolution=0.1,
        orient=tk.HORIZONTAL,
        command=command,  # This will pass the current slider value to the command function
        bg=frame_bg,
        fg=font_fg,
        troughcolor='white',
        highlightthickness=0
    )
    slider.pack(fill=tk.X, pady=5, padx=10)
    slider.set(1.0)  # Set the slider to the neutral value (1.0 means no change)
    return slider


# Drawing tools functions

# Function to start drawing on the canvas
def start_drawing(event):
    global is_drawing, prev_x, prev_y
    if is_draw_tool_active:
        is_drawing = True
        prev_x, prev_y = event.x, event.y


# def draw_on_image(current_x, current_y):
#     global prev_x, prev_y, scale_factor
#     if is_draw_tool_active:
#         draw1 = ImageDraw.Draw(image)
#
#         # Adjust coordinates for offsets and scale factor
#         original_x1 = (prev_x - x_offset) / scale_factor
#         original_y1 = (prev_y - y_offset) / scale_factor
#         original_x2 = (current_x - x_offset) / scale_factor
#         original_y2 = (current_y - y_offset) / scale_factor
#
#         # Draw on the original image
#         draw1.line([original_x1, original_y1, original_x2, original_y2], fill=drawing_color, width=line_width)

# Function to draw on the canvas
def draw_or_erase(event):
    global prev_x, prev_y, drawing_layer, draw1
    if not is_drawing:
        return
    current_x, current_y = event.x, event.y
    if is_erasing:
        # Erase functionality on the drawing layer
        erase_area = [
            current_x - eraser_size, current_y - eraser_size,
            current_x + eraser_size, current_y + eraser_size
        ]
        draw1.rectangle(erase_area, fill=(0, 0, 0, 0))  # Erase with transparency
    else:
        # Draw on the drawing layer
        draw1.line([prev_x, prev_y, current_x, current_y], fill=drawing_color, width=line_width)
        print(f"Drawing from ({prev_x}, {prev_y}) to ({current_x}, {current_y})")
        print(f"Drawing Layer: {drawing_layer}")

    # Update the canvas with the combined image
    update_image_display(image)
    prev_x, prev_y = current_x, current_y

# Function to stop drawing
def stop_drawing(event):
    global is_drawing
    is_drawing = False

# Function to change the pen color
def change_pen_color():
    global drawing_color
    color = askcolor()[1]
    if color:
        drawing_color = color

def activate_draw():
    global is_drawing, is_erasing
    is_drawing = True
    is_erasing = False
    print("Drawing")

def activate_eraser():
    global is_drawing, is_erasing
    is_drawing = False
    is_erasing = True
    print("erasing")

# Function to change the line width using slider
def change_line_width(value):
    global line_width
    line_width = int(value)

# Function to clear the canvas
def clear_canvas():
    global image, is_drawing, is_draw_tool_active
    is_drawing = False
    is_draw_tool_active = False
    image = original_image.copy()
    update_image_display(image)

def reset_canvas_and_image():
    global image
    image = original_image.copy()  # Reset image to the original state
    update_image_display(image)  # Re-render the image

def create_draw_option(parent, label_text, command):
    frame = tk.Frame(parent, bg=frame_bg)
    frame.pack(fill=tk.X, pady=5, padx=10)

    button = tk.Button(frame,text=label_text, command=command, bg=frame_bg, fg=font_fg)
    button.pack(side=tk.TOP, fill=tk.X, pady=20, padx=20)

    return frame

def change_line_width(value):
    global line_width
    line_width = round(float(value))  # Convert to float and round to nearest integer


# GUI code
root = tk.Tk()
root.title('Photo Custom')
root.attributes("-fullscreen", True)  # Make the window fullscreen
root.geometry("1920x1080")

canvas_width = 1450
canvas_height = 840

# Menu
menu_font = ("Helvetica", 10)
menu_bg = "#26293A"
menu_fg = "#FFFFFF"

# Create custom menu bar using a Frame
menu_bar_frame = tk.Frame(root, bg=menu_bg, height=30)
menu_bar_frame.pack(side="top", fill="x")

# Add File menu
file_menu_button = tk.Menubutton(menu_bar_frame, text="File", bg=menu_bg, fg=menu_fg, font=menu_font, relief="flat")
file_menu_button.pack(side="left", padx=10)
file_dropdown = tk.Menu(file_menu_button, tearoff=0, bg=menu_bg, fg=menu_fg, font=menu_font)
file_menu_button.config(menu=file_dropdown)
file_dropdown.add_command(label="Open", command=open_image)
file_dropdown.add_command(label="Save", command=save_image)
file_dropdown.add_separator()
file_dropdown.add_command(label="Exit", command=root.quit)

# Add Edit menu
edit_menu_button = tk.Menubutton(menu_bar_frame, text="Edit", bg=menu_bg, fg=menu_fg, font=menu_font, relief="flat")
edit_menu_button.pack(side="left", padx=10)
edit_dropdown = tk.Menu(edit_menu_button, tearoff=0, bg=menu_bg, fg=menu_fg, font=menu_font)
edit_menu_button.config(menu=edit_dropdown)
edit_dropdown.add_command(label="Revert to Original", command=revert_to_original)

# Add Tools menu
tools_menu_button = tk.Menubutton(menu_bar_frame, text="Tools", bg=menu_bg, fg=menu_fg, font=menu_font, relief="flat")
tools_menu_button.pack(side="left", padx=10)
tools_dropdown = tk.Menu(tools_menu_button, tearoff=0, bg=menu_bg, fg=menu_fg, font=menu_font)
tools_menu_button.config(menu=tools_dropdown)
tools_dropdown.add_command(label="Crop", command=crop_image)
tools_dropdown.add_separator()
tools_dropdown.add_command(label="Rotate 90º CW", command=rotate_90_cw)
tools_dropdown.add_command(label="Rotate 90º CCW", command=rotate_90_ccw)


# Sidebar for filters with scrollable functionality

sidebar_canvas = Canvas(root, width=150, height=840, bg="#E3F2F1")
sidebar_scrollbar = Scrollbar(root, orient="vertical", command=sidebar_canvas.yview)

sidebar_frame = Frame(sidebar_canvas, bg="#030303")

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


# ----------------------filter sidebar canvas -----------------------
# Example filter creation
bw_image_path = r"C:\Users\HP\OneDrive\Pictures\b&w.jpeg" # Replace with your image path
bw_filter = create_filter_option(sidebar_frame, bw_image_path, "B&W", apply_bw)

warmer_image_path = r"C:\Users\HP\OneDrive\Pictures\warm-contrast.jpeg"
warmer_filter = create_filter_option(sidebar_frame, warmer_image_path, "Warm Contrast", apply_warmer)

blur_image_path = r"C:\Users\HP\OneDrive\Pictures\blur.jpeg"
blur_filter = create_filter_option(sidebar_frame, blur_image_path, "Blur", apply_blur)

# golden_image_path =r"C:\Users\HP\OneDrive\Pictures\golden.jpeg"
# golden_filter = create_filter_option(sidebar_frame, golden_image_path, "Golden")

sharpen_film_path = r"C:\Users\HP\OneDrive\Pictures\sharpen.jpeg"
sharpen_filter = create_filter_option(sidebar_frame, sharpen_film_path, "Sharpen",apply_sharpen)

sepia_image_path = r"C:\Users\HP\OneDrive\Pictures\sepia2.jpg"
sepia_filter = create_filter_option(sidebar_frame, sepia_image_path, "Sepia", apply_sepia)

smooth_image_path = r"C:\Users\HP\OneDrive\Pictures\golden.jpeg"
smooth_filter = create_filter_option(sidebar_frame, smooth_image_path, "Smooth", apply_smoothen_filter)

# Toggle Filter sidebar
def toggle_sidebar():
    if sidebar_canvas.winfo_ismapped():
        hide_filter_sidebar()
    else:
        if adjustment_sidebar_canvas.winfo_ismapped():
            hide_adjust_sidebar()
        if draw_sidebar_canvas.winfo_ismapped():
            hide_draw_sidebar()
        show_filter_sidebar()

#Main Frame container
frame_bg = "#252525"
button_color = "#292929"
font_fg = "#FFFFFF"

main_frame = tk.Frame(root, background=frame_bg)
main_frame.pack(fill=tk.Y, side=tk.LEFT)

#Resize frame
resize_frame = tk.Frame(main_frame, background=frame_bg)
resize_frame.pack(side=tk.TOP, fill=tk.X)

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

#Filter Frame
filter_frame = tk.Frame(main_frame, background=frame_bg)
filter_frame.pack(side=tk.TOP, fill=tk.X)

#---------------------Adjustment-------------------
#toggler of adjust
def toggle_adjust_sidebar():
    if adjustment_sidebar_canvas.winfo_ismapped():
        hide_adjust_sidebar()
    else:
        if sidebar_canvas.winfo_ismapped():
            hide_filter_sidebar()
        elif draw_sidebar_canvas.winfo_ismapped():
            hide_draw_sidebar()
        show_adjust_sidebar()

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

#--------------Drawing tools--------------
is_draw_tool_active = False
# Drawing Sidebar Toggle Function
def toggle_draw_sidebar():
    global is_draw_tool_active
    if draw_sidebar_canvas.winfo_ismapped():
        hide_draw_sidebar()
    else:
        if sidebar_canvas.winfo_ismapped():
            hide_filter_sidebar()
        elif adjustment_sidebar_canvas.winfo_ismapped():
            hide_adjust_sidebar()
        show_draw_sidebar()
        is_draw_tool_active = True

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

# Frame for Draw Sidebar
draw_frame = tk.Frame(main_frame,background=frame_bg)
draw_frame.pack(side=tk.TOP, fill=tk.X)

color_button = create_draw_option(draw_sidebar_frame,"Change Color", change_pen_color)

# Add Line Width Slider
line_width_slider = create_adjustment_slider_option(
    draw_sidebar_frame,  # Parent frame
    "Line Width",        # Label text
    change_line_width,   # Command function
    from_=1,             # Minimum line width
    to=30                # Maximum line width
)
draw_button = create_draw_option(draw_sidebar_frame, "Draw", activate_draw)
erase_button = create_draw_option(draw_sidebar_frame, "Eraser", activate_eraser)

# Create Button with Icon and Text
def create_icon_button(frame, image, text, command):
    button_frame = Frame(frame, bg=frame_bg)  # Create a frame for each button

    icon_button = Button(
        button_frame,
        command=command,
        bg=button_color,
        fg=font_fg,
        relief="flat",
        bd=0,
        image=image,  # Set the icon image
        activebackground="#282828",  # Active background color
        activeforeground=font_fg  # Active foreground color
    )
    icon_button.pack(side="top", pady=3)

    label = Label(button_frame, text=text, bg=frame_bg, fg=font_fg, font=("Helvetica", 8))
    label.pack(side="top",pady=3)  # Add label below the icon

    button_frame.pack(side="left", padx=20,pady=5)  # Pack the frame with button and label


# Modern Buttons with Icons and Text
create_icon_button(resize_frame, resize_icon_tk, "Resize", open_new_window)
create_icon_button(filter_frame, filter_icon_tk, "Filter", toggle_sidebar)
create_icon_button(adjust_frame, adjust_icon_tk, "Adjust", toggle_adjust_sidebar)
create_icon_button(draw_frame, draw_icon_tk, "Draw", toggle_draw_sidebar)


#---------------Canvas----------------
# Canvas for image display (Expands to the right of the sidebar)
canvas = Canvas(root, bg="#2C2C2C", width=canvas_width, height=canvas_height, relief="solid", borderwidth=2)
canvas.pack(fill=tk.BOTH, expand=True, side=tk.LEFT)

# Mouse events for cropping
canvas.bind("<ButtonPress-1>", on_press)  # Left mouse button press to start cropping
canvas.bind("<B1-Motion>", on_drag)  # Dragging the mouse while holding the left button
canvas.bind("<ButtonRelease-1>", on_release)  # Left mouse button release to finalize cropping
canvas.bind("<Configure>", lambda event: update_image_display(image))

# Bind mouse events for drawing
canvas.bind("<ButtonPress-1>", start_drawing)  # Left mouse button press to start drawing
canvas.bind("<B1-Motion>", draw_or_erase)  # Dragging the mouse while holding the left button
canvas.bind("<ButtonRelease-1>", stop_drawing)  # Left mouse button release to stop drawing

root.mainloop()


