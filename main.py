import tkinter as tk
from tkinter.ttk import *
from tkinter import *
from tkinter import ttk
from tkinter import filedialog, messagebox, Canvas, Button, Frame, Label, Scale, HORIZONTAL, font, colorchooser
from PIL import Image, ImageTk, ImageOps, ImageEnhance, ImageFilter, ImageDraw, ImageColor, ImageFont
from tkinter.colorchooser import askcolor
from PIL import Image as PILImage
import PIL
from functools import partial
import numpy as np


# Function
crop_rect = None
canvas_width = 1450
canvas_height = 840
canvas = None
original_image = None
scale_factor = 1
image = None
prev_x, prev_y = None, None
x_offset = 0
y_offset = 0
drawing_layer = None
is_drawing = False
is_erasing = False
eraser_size = 10
undo_stack = []
redo_stack = []

# API_KEY = "UReEZkcCaUziDjHsXBlsbmNawbHDJevT"
# GIPHY_URL = f"https://api.giphy.com/v1/stickers/trending?api_key={API_KEY}&limit=30&rating=G"

def update_image_display(image):
    global image_on_canvas, scaled_image, scale_factor, x_offset, y_offset, drawing_layer
    # Check if the image is valid
    if image is None:
        return

    # Get current canvas dimensions dynamically
    current_width = canvas.winfo_width()
    current_height = canvas.winfo_height()

    # Fallback to default dimensions if not set yet
    if current_width <= 1 or current_height <= 1:
        current_width = canvas_width
        current_height = canvas_height

    # Clear the canvas
    #canvas.delete("all")

    # Calculate the scaling factors for width and height
    scale_x = current_width / image.width
    scale_y = current_height / image.height

    # Use the smaller scaling factor to maintain aspect ratio
    scale_factor = min(scale_x, scale_y)

    # Resize the image
    new_width = int(image.width * scale_factor)
    new_height = int(image.height * scale_factor)
    scaled_image = image.resize((new_width, new_height), Image.Resampling.LANCZOS)

    # Resize the drawing layer to match the scaled image
    drawing_layer_resized = drawing_layer.resize((new_width, new_height), Image.Resampling.NEAREST)

    # Combine the scaled image and drawing layer
    combined_image = Image.alpha_composite(scaled_image.convert("RGBA"), drawing_layer_resized)

    # Convert to a format suitable for Tkinter canvas
    image_on_canvas = ImageTk.PhotoImage(combined_image)

    # Calculate offsets for centering the image on the canvas
    x_offset = (current_width - new_width) // 2
    y_offset = (current_height - new_height) // 2

    # Update the canvas with the scaled image
    canvas.create_image(x_offset, y_offset, anchor="nw", image=image_on_canvas)
    canvas.image = image_on_canvas

    restore_stickers()
    # After updating the image, redraw text items

    for text_id in text_ids:
        canvas.tag_raise(text_id)

    # Update the canvas with the scaled image
    # image_on_canvas = ImageTk.PhotoImage(scaled_image)
    # canvas.create_image(x_offset, y_offset, anchor="nw", image=image_on_canvas)
    # canvas.image = image_on_canvas

    # Debugging outputs to confirm calculations
    # print("Canvas Dimensions:", current_width, current_height)
    # print("Original Image Dimensions:", image.width, image.height)
    # print("Scaled Image Dimensions:", new_width, new_height)
    print("Scale Factor:", scale_factor)
    print("Offsets:", x_offset, y_offset)

# Function to restore stickers after toggling
def restore_stickers():
    if hasattr(canvas, 'stickers'):
        print(f"Restoring {len(canvas.stickers)} stickers")

        for sticker_id, (original_image, position, handle_id) in canvas.stickers.items():
            sticker_image_tk = ImageTk.PhotoImage(original_image)
            canvas.itemconfig(sticker_id, image=sticker_image_tk)
            canvas.image_refs[sticker_id] = sticker_image_tk  # Prevent garbage collection

            # Reapply the sticker's position and handle
            x, y = position
            canvas.coords(sticker_id, x, y)
            canvas.tag_raise(sticker_id)  # Ensure it is on top of other elements

            # Update the handle position
            handle_x = x + 25
            handle_y = y + 25
            canvas.coords(handle_id, handle_x, handle_y, handle_x + 10, handle_y + 10)
            canvas.tag_raise(handle_id)

            print(f"Restored Sticker ID: {sticker_id} at Position: {position}")


def open_image():
    global image, original_image, file_path, drawing_layer
    file_path = filedialog.askopenfilename(filetypes=[("Image Files", "*.jpeg *.jpg *.png *.gif")])
    if file_path:
        image = Image.open(file_path).convert("RGBA")
        original_image = image.copy()
        drawing_layer = Image.new("RGBA", image.size, (0, 0, 0, 0))  # Transparent drawing layer
        update_image_display(image)


def save_image():
    global image, drawing_layer, canvas_width, canvas_height
    # if image and drawing_layer:
    #     file_path = filedialog.asksaveasfilename(defaultextension=".png", filetypes=[("PNG files", "*.png"), ("JPEG files", "*.jpg")])
    #     if file_path:
    #         combined_image = Image.alpha_composite(image.convert("RGBA"), drawing_layer)
    #         combined_image.save(file_path)
    if image is not None and drawing_layer is not None:
        # Combine the base image with the drawing layer
        combined_image = Image.alpha_composite(image.convert("RGBA"), drawing_layer)

        # Get the stickers from the canvas
        if hasattr(canvas, 'stickers'):
            print("Stickers in canvas:", canvas.stickers)
            for sticker_id, (original_image, position, current_size) in canvas.stickers.items():
                if isinstance(original_image, PIL.Image.Image):
                    print(f"Sticker ID: {sticker_id}, Position: {position}, Size: {current_size}")
                    # Check if position is a tuple, if not, skip it
                    if isinstance(position, tuple) and len(position) == 2:
                        x, y = position
                    else:
                        print(f"Invalid position for sticker ID {sticker_id}: {position}")
                        continue  # Skip if position is not a valid tuple

                    sticker_image_resized = original_image
                    print(f"original size : {original_image.size}")

                    # Get canvas size and apply scaling to adjust sticker position
                    canvas_width = canvas.winfo_width()
                    canvas_height = canvas.winfo_height()


                    # resize the sticker image
                    adjusted_x = int(x * (image.width / canvas_width))
                    adjusted_y = int(y * (image.height / canvas_height))

                    # Add sticker to the combined image at its position
                      # Resize sticker if needed
                    sticker_position = (int(adjusted_x - current_size/2), int(adjusted_y - current_size/2))  # Adjust for centering the sticker
                    print(f"Pasting sticker ID {sticker_id} at position: {sticker_position}, with size: {sticker_image_resized.size}")
                    combined_image.paste(sticker_image_resized, sticker_position, sticker_image_resized.convert("RGBA"))

        #Add text to the combined image
        draw = ImageDraw.Draw(combined_image)

        for text_id in canvas.find_withtag("text"):
            # Get all text elements
            text_content = canvas.itemcget(text_id, "text")
            text_font = canvas.itemcget(text_id, "font")
            text_fill = canvas.itemcget(text_id, "fill")
            position = canvas.coords(text_id)

            # Debugging: Print the font string
            print(f"Font string for text ID {text_id}: {text_font}")

            # Clean the font string and parse it
            font_parts = text_font.split()
            font_family = font_parts[0] if len(font_parts) > 0 else "Arial"
            font_size = int(font_parts[1]) if len(font_parts) > 1 else 20

            # Load the font
            try:
                font = ImageFont.truetype(f"{font_family}.ttf", font_size)
            except IOError:
                font = ImageFont.load_default()
            adjusted_x = int(position[0] * (image.width / canvas_width))
            adjusted_y = int(position[1] * (image.height / canvas_height))
            draw.text((adjusted_x, adjusted_y), text_content, fill=text_fill, font=font)


    file_path = filedialog.asksaveasfilename(defaultextension=".png",
                                                 filetypes=[("PNG files", "*.png"), ("JPEG files", "*.jpg")])

    #ask for save location
    # if image is not None and drawing_layer is not None:
    if file_path:
        try:
            # combined_image = Image.alpha_composite(image.convert("RGBA"), drawing_layer)
            combined_image.save(file_path)
        except Exception as e:
            messagebox.showerror("Error", f"failed to save {e}")
            print(f"Error details: {e}")

    else:
        messagebox.showerror("Error", "No image to save")


# def save_image():
#     global image, drawing_layer, canvas_width, canvas_height
#
#     if image is not None and drawing_layer is not None:
#         # Combine the base image with the drawing layer
#         combined_image = Image.alpha_composite(image.convert("RGBA"), drawing_layer)
#
#         # Add text to the combined image
#         draw = ImageDraw.Draw(combined_image)
#
#         for text_id in canvas.find_withtag("text"):  # Get all text elements
#             text_content = canvas.itemcget(text_id, "text")
#             text_font = canvas.itemcget(text_id, "font")
#             text_fill = canvas.itemcget(text_id, "fill")
#             position = canvas.coords(text_id)
#
#             # Debugging: Print the font string
#             print(f"Font string for text ID {text_id}: {text_font}")
#
#             # Clean the font string and parse it
#             font_parts = text_font.split()
#             font_family = font_parts[0] if len(font_parts) > 0 else "Arial"
#             font_size = int(font_parts[1]) if len(font_parts) > 1 else 20
#
#             # Load the font
#             try:
#                 font = ImageFont.truetype(f"{font_family}.ttf", font_size)
#             except IOError:
#                 font = ImageFont.load_default()
#             adjusted_x = int(position[0] * (image.width / canvas_width))
#             adjusted_y = int(position[1] * (image.height / canvas_height))
#             draw.text((adjusted_x, adjusted_y), text_content, fill=text_fill, font=font)
#
#         # Prompt user to save the image
#         file_path = filedialog.asksaveasfilename(defaultextension=".png",
#                                                  filetypes=[("PNG files", "*.png"), ("JPEG files", "*.jpg")])
#
#         if file_path:
#             try:
#                 combined_image.save(file_path)
#                 print(f"Image saved successfully at {file_path}")
#             except Exception as e:
#                 messagebox.showerror("Error", f"Failed to save: {e}")
#                 print(f"Error details: {e}")
#         else:
#             messagebox.showerror("Error", "No image to save")
#

# Edit menu revert to original
def revert_to_original():
    global image, original_image, drawing_layer
    if original_image:
        image = original_image.copy()
        # Reset the drawing layer to be transparent
        drawing_layer = Image.new("RGBA", image.size, (0, 0, 0, 0))
        update_image_display(image)
    else:
        messagebox.showerror(image)


# Crop image
def crop_image():
    global image, crop_rect, drawing_layer
    if image and crop_rect:
        x1, y1, x2, y2 = crop_rect  # ex: x1=200, y1=150, x2=350, y2=250

        # convert canvas coordinates to original image coordinates
        offset_x = (canvas_width - scaled_image.width) // 2  # 0
        offset_y = (canvas_height - scaled_image.height) // 2  # 0

        x1 = max(0, x1 - offset_x)  # 200 - 0 = 200
        y1 = max(0, y1 - offset_y)  # 150 - 0 = 150
        x2 = max(0, x2 - offset_x)  # 350 - 0 = 350
        y2 = max(0, y2 - offset_y)  # 250 - 0 = 250

        scale_factor = scaled_image.width / image.width

        x1 = int(x1 / scale_factor)  # 200 / 0.5 = 400
        y1 = int(y1 / scale_factor)  # 150 / 0.5 = 300
        x2 = int(x2 / scale_factor)  # 350 / 0.5 = 700
        y2 = int(y2 / scale_factor)  # 250 / 0.5 = 500

        # Map canvas coordinates (x1, y1, x2, y2) to original image coordinates
        # x1 = (x1 - offset_x) / scale_factor
        # y1 = (y1 - offset_y) / scale_factor
        # x2 = (x2 - offset_x) / scale_factor
        # y2 = (y2 - offset_y) / scale_factor

         # Debugging output
        print(f"Crop Rectangle on Canvas: {crop_rect}")
        print(f"Offsets: ({offset_x}, {offset_y})")
        print(f"Scale Factor: {scale_factor}")
        print(f"Adjusted Crop Coordinates: ({x1}, {y1}), ({x2}, {y2})")

        # Round coordinates to nearest integer for cropping
        x1, y1, x2, y2 = map(int, (x1, y1, x2, y2))

        if x1 < x2 and y1 < y2:  # 400<700 and 300<500   In this case, 400 < 700 is True, meaning the top-left corner is indeed to the left of the bottom-right corner horizontally.
            cropped_image = image.crop((x1, y1, x2, y2))  # Crops the image from (400, 300) to (700, 500)
            # Crop the drawing layer
            cropped_drawing_layer = drawing_layer.crop((x1,y1,x2,y2))
            image = cropped_image
            drawing_layer = cropped_drawing_layer
            update_image_display(cropped_image)

        else:
            messagebox.showerror("Invalid Selection", "Please select a valid crop area.")


# Mouse drag to create a rectangle for cropping
def on_press(event):
    global crop_rect
    crop_rect = (event.x, event.y, event.x, event.y)  # Initialize crop rectangle


def on_drag(event):
    global crop_rect
    crop_rect = (crop_rect[0], crop_rect[1], event.x, event.y)

def on_release(event):
    pass  # Crop the image when mouse is released

def redraw_crop_rectangle():
    global crop_rect
    canvas.delete("crop_rect")
    if crop_rect:
        x1, y1, x2, y2 = crop_rect
        canvas.create_rectangle(x1, y1, x2, y2, outline="red", width=2, tags="crop_rect")
        canvas.update()

# Menu or button to trigger cropping action
def on_crop_menu_option():
    crop_image()  # Trigger crop when user selects crop option from menu

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


# Filters
def apply_bw():
    global image, drawing_layer
    if image:
        # combine the image and the drawing layer
        combined_image = Image.alpha_composite(image.convert('RGBA'), drawing_layer)
        grayscale_img = ImageOps.grayscale(combined_image)
        # update the image and reset the drawing
        image = grayscale_img.convert('RGBA')
        drawing_layer = Image.new("RGBA", image.size, (0, 0, 0, 0))
        update_image_display(grayscale_img)


def apply_warmer():
    global image, drawing_layer
    if image:
        # combine the image and the drawing layer
        combined_image = Image.alpha_composite(image.convert('RGBA'), drawing_layer)
        enhancer = ImageEnhance.Color(combined_image)
        warm_img = enhancer.enhance(1.5)
        image = warm_img.convert('RGBA')

        # Convert the image to PhotoImage for display in Tkinter
        image_tk = ImageTk.PhotoImage(warm_img)
        drawing_layer = Image.new("RGBA", image.size, (0, 0, 0, 0))
        # Update the displayed image
        update_image_display(warm_img)


def apply_blur():
    global image, drawing_layer
    if image:
        # Apply gaussian blur to image
        combined_image = Image.alpha_composite(image.convert('RGBA'), drawing_layer)
        blured_img = combined_image.filter(ImageFilter.GaussianBlur(radius=3))
        image = blured_img.convert('RGBA')
        drawing_layer = Image.new("RGBA", image.size, (0, 0, 0, 0))
        update_image_display(blured_img)


def apply_sepia():
    global image
    if image:
        if image.mode != "RGB":
            image = image.convert("RGB")
        # Apply sepia filter
        sepia_filter = ImageEnhance.Color(image).enhance(0.5)
        sepia_image = ImageEnhance.Brightness(sepia_filter).enhance(0.9)
        image = sepia_image

        update_image_display(sepia_image)


def apply_sharpen():
    global image
    if image:
        if image.mode != 'RGB':
            image = image.convert("RGB")

        # apply Sharpen filter
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

def apply_vintage_filter():
    global image
    if image:
        if image.mode != "RGB":
            image = image.convert("RGB")

        # Step 1: Desaturate the image (reduce saturation)
        desaturated_image = ImageEnhance.Color(image).enhance(0.6)  # Reduce saturation by 70%

        # Step 2: Add a warm color overlay
        warm_overlay = Image.new("RGB", desaturated_image.size, (240, 200, 160))  # Warm tone
        warm_image = Image.blend(desaturated_image, warm_overlay, alpha=0.15)  # Blend overlay

        # Step 3: Add vignette effect
        vignette = Image.new("L", warm_image.size, 255)  # Black mask for vignette
        x, y = warm_image.size
        for i in range(x):
            for j in range(y):
                # Calculate radial gradient for vignette
                distance = ((i - x / 2) ** 2 + (j - y / 2) ** 2) ** 0.5
                max_distance = ((x / 2) ** 2 + (y / 2) ** 2) ** 0.5
                vignette_value = int(255 * (1 - 0.7 * (distance / max_distance)))  # Adjust strength (0.7)
                vignette.putpixel((i, j), max(0, vignette_value))

        vignette_image = ImageOps.colorize(vignette, black="black", white="white")  # Black to white vignette
        vignette_applied = Image.blend(warm_image, vignette_image, alpha=0.25)  # Light vignette application

        # Step 4: Slightly brighten the image to counterbalance dark effects
        vintage_image = ImageEnhance.Brightness(vignette_applied).enhance(1.1)  # Brighten by 10%

        # Update the global image and display the result
        image = vintage_image
        update_image_display(vintage_image)


def apply_cartoon_filter():
    global image
    if image:
        if image.mode != "RGB":
            image = image.convert("RGB")

        # Step 1: Apply edge detection (using edge enhancement filter)
        edge_enhanced_image = image.filter(ImageFilter.FIND_EDGES)

        # Step 2: Reduce colors by using a simple color quantization method
        # Convert image to NumPy array for easy manipulation
        np_image = np.array(image)
        # Apply quantization by reducing color depth
        quantized_image = np_image // 32 * 32  # Reduce colors to steps of 32

        # Convert back to PIL image
        quantized_image_pil = Image.fromarray(quantized_image)

        # Step 3: Combine the quantized image with the edge-detected image
        # Convert edge-enhanced image to grayscale
        edge_enhanced_gray = edge_enhanced_image.convert("L")
        edge_enhanced_gray = edge_enhanced_gray.point(lambda p: p * 3)  # Enhance edges

        # Convert grayscale edge image back to RGB
        edge_enhanced_rgb = ImageOps.grayscale(edge_enhanced_gray).convert("RGB")

        # Blend the quantized image with the edge-detected image
        cartoon_image = Image.blend(quantized_image_pil, edge_enhanced_rgb, alpha=0.5)

        # Step 4: Optional - Enhance the brightness to make it pop more (cartoonish effect)
        cartoon_image = ImageEnhance.Brightness(cartoon_image).enhance(1.1)  # Brighten by 10%

        # Update the global image and display the result
        image = cartoon_image
        update_image_display(cartoon_image)

# Sidebar and Canvas for filter
def show_filter_sidebar():
    deactivate_tools()
    global canvas_width
    # Show the sidebar with filter buttons
    sidebar_canvas.pack(side=tk.LEFT, fill=tk.Y, padx=10)
    canvas_width = 1170  # Adjust the canvas width to accommodate the sidebar
    canvas.config(width=canvas_width)
    update_image_display(image)
    # Mouse events for cropping
    canvas.bind("<ButtonPress-1>", on_press)  # Left mouse button press to start cropping
    canvas.bind("<B1-Motion>", on_drag)  # Dragging the mouse while holding the left button
    canvas.bind("<ButtonRelease-1>", on_release)  # Left mouse button release to finalize cropping
    canvas.bind("<Configure>", lambda event: update_image_display(image) if image else None)


def hide_filter_sidebar():
    deactivate_tools()
    global canvas_width
    # Hide the sidebar
    sidebar_canvas.pack_forget()
    canvas_width = 1450  # Reset canvas width when sidebar is hidden
    canvas.config(width=canvas_width)
    update_image_display(image)


# sidebar for adjustment
def show_adjust_sidebar():
    deactivate_tools()
    global canvas_width
    adjustment_sidebar_canvas.pack(side=tk.LEFT, fill=tk.Y, padx=10)
    canvas_width = 1150
    canvas.config(width=canvas_width)
    update_image_display(image)
    # Mouse events for cropping
    canvas.bind("<ButtonPress-1>", on_press)  # Left mouse button press to start cropping
    canvas.bind("<B1-Motion>", on_drag)  # Dragging the mouse while holding the left button
    canvas.bind("<ButtonRelease-1>", on_release)  # Left mouse button release to finalize cropping
    canvas.bind("<Configure>", lambda event: update_image_display(image) if image else None)


def hide_adjust_sidebar():
    deactivate_tools()
    global canvas_width
    # Hide the adjustment sidebar
    adjustment_sidebar_canvas.pack_forget()
    canvas_width = 1450
    canvas.config(width=canvas_width)
    update_image_display(image)


def show_draw_sidebar():
    deactivate_tools()
    global canvas_width
    draw_sidebar_canvas.pack(side=tk.LEFT, fill=tk.Y, padx=10)
    canvas_width = 1150
    canvas.config(width=canvas_width)
    update_image_display(image)
    # Mouse events for cropping
    canvas.bind("<ButtonPress-1>", on_press)  # Left mouse button press to start cropping
    canvas.bind("<B1-Motion>", on_drag)  # Dragging the mouse while holding the left button
    canvas.bind("<ButtonRelease-1>", on_release)  # Left mouse button release to finalize cropping
    canvas.bind("<Configure>", lambda event: update_image_display(image) if image else None)


def hide_draw_sidebar():
    deactivate_tools()
    global canvas_width
    # hide the sidebar of draw
    draw_sidebar_canvas.pack_forget()
    canvas_width = 1450
    canvas.config(width=canvas_width)
    update_image_display(image)


def show_sticker_sidebar():
    deactivate_tools()
    global canvas_width
    sticker_sidebar_canvas.pack(side=tk.LEFT, fill=tk.Y, padx=10)
    canvas_width = 1150
    canvas.config(width=canvas_width)
    update_image_display(image)


def hide_sticker_sidebar():
    deactivate_tools()
    global canvas_width
    sticker_sidebar_canvas.pack_forget()
    canvas_width = 1450
    canvas.config(width=canvas_width)
    update_image_display(image)

def show_text_sidebar():
    #deactivate_tools()
    global canvas_width
    text_sidebar_canvas.pack(side=tk.LEFT, fill=tk.Y, padx=10)
    canvas_width = 1150
    canvas.config(width=canvas_width)
    update_image_display(image)

def hide_text_sidebar():
    #deactivate_tools()
    global canvas_width
    text_sidebar_canvas.pack_forget()
    canvas_width = 1450
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
    deactivate_tools()
    global image, original_image
    if original_image:
        image = original_image.copy()  # Reset to the original state
        update_image_display(image)

        # Reset the slider to the default (1.0 for no change)
        brightness_slider.set(1.0)  # Reset slider position to no change


# Function to apply contrast adjustment
def apply_contrast(value):
    deactivate_tools()
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


def create_adjustment_option(parent, name, command):
    frame = Frame(parent, bg="#292828", width=120, height=50, highlightbackground="white", highlightthickness=0)
    frame.pack_propagate(False)
    frame.pack(pady=10, padx=10)

    # add the adjustment label
    text_label = Label(frame, text=name, bg="black", fg="white", font=('Arial', 10))
    text_label.pack()

    # bind click event to button
    button = Button(frame, text="Apply", command=command)
    button.pack()

    return frame


def on_mouse_wheel(event, canvas):
    canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")


def on_hover(event):
    event.widget.config(bg="#282828")  # Lighter shade on hover


def on_leave(event):
    event.widget.config(bg=button_color)  # Reset to original color


# Adjustment Slider
# Function to create a slider for adjustment (brightness, contrast, etc.)

def create_adjustment_slider_option(parent, label_text, command, from_=0.5, to=2.0):
    # Create a custom style for the slider
    style = ttk.Style()
    style.theme_use('default')
    style.configure(
        "Custom.Horizontal.TScale",
        troughcolor='white',  # Color of the trough
        background='#0096FF',  # Color of the slider button
    )

    frame = tk.Frame(parent, bg=frame_bg)
    frame.pack(fill=tk.X, pady=5, padx=15)

    label = tk.Label(frame, text=label_text, bg=frame_bg, fg=font_fg)
    label.pack(side=tk.TOP, anchor="w")

    slider = ttk.Scale(
        frame,
        from_=from_,
        to=to,
        orient=tk.HORIZONTAL,
        command=command,  # This will pass the current slider value to the command function
        # bg=frame_bg,
        # fg=font_fg,
        # troughcolor='white',
        # highlightthickness=0
        style="Custom.Horizontal.TScale"
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
        # Adjust the starting point for scaling and offsets
        current_x, current_y = event.x, event.y
        prev_x = (current_x - x_offset) / scale_factor
        prev_y = (current_y - y_offset) / scale_factor


def draw_on_image(event):
    """Draw on the canvas or erase based on the current mode."""
    global prev_x, prev_y, draw, drawing_layer
    if is_drawing and drawing_layer is not None:
        current_x, current_y = event.x, event.y

        # Adjust for scaling and offsets

        adjusted_x = (current_x - x_offset) / scale_factor
        adjusted_y = (current_y - y_offset) / scale_factor
        draw_obj = ImageDraw.Draw(drawing_layer)


        if is_erasing:
            erase_area = [adjusted_x - eraser_size, adjusted_y - eraser_size, adjusted_x + eraser_size,
                          adjusted_y + eraser_size]
            # draw_obj.rectangle(erase_area, fill=(0, 0, 0, 0))  # Erase with transparency
            draw_obj.ellipse(erase_area, fill=(0, 0, 0, 0))

        else:
            if prev_x is not None and prev_y is not None:
                draw_obj.line([prev_x, prev_y, adjusted_x, adjusted_y], fill=drawing_color, width=line_width,
                              joint="curve")
                # Add circles at endpoints for rounded edges
                radius = line_width /2
                draw_obj.ellipse(
                    [
                        adjusted_x - radius,
                        adjusted_y - radius,
                        adjusted_x + radius,
                        adjusted_y + radius,
                    ],
                    fill=drawing_color,
                )
                draw_obj.ellipse(
                    [
                        prev_x - radius,
                        prev_y - radius,
                        prev_x + radius,
                        prev_y + radius,
                    ],
                    fill=drawing_color,
                )
        prev_x, prev_y = adjusted_x, adjusted_y
        update_image_display(image)


def activate_draw():
    """Activate drawing mode."""
    global is_drawing, is_erasing
    is_drawing = True
    is_erasing = False
    canvas.focus_set()
    # Set cursor type
    canvas.config(cursor="cross")
    canvas.bind("<ButtonPress-1>", start_drawing)  # Start drawing
    canvas.bind("<B1-Motion>", draw_on_image)  # Draw while moving the mouse
    canvas.bind("<ButtonRelease-1>", stop_drawing)  # Stop drawing


def activate_eraser():
    """Activate eraser mode."""
    global is_drawing, is_erasing
    is_drawing = False
    is_erasing = True
    canvas.focus_set()
    # Set cursor type
    canvas.config(cursor="cross")
    canvas.bind("<ButtonPress-1>", start_drawing)  # Start drawing
    canvas.bind("<B1-Motion>", draw_on_image)  # Draw while moving the mouse
    canvas.bind("<ButtonRelease-1>", stop_drawing)  # Stop drawing


def deactivate_tools():
    global is_drawing, is_erasing, canvas,prev_x, prev_y
    is_erasing = False
    is_drawing = False
    if canvas is not None:
        canvas.config(cursor="arrow")
        canvas.unbind("<ButtonPress-1>")
        canvas.unbind("<B1-Motion>")
        canvas.unbind("<ButtonRelease-1>")


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


# Function to change the line width using slider
def change_line_width(value):
    global line_width
    line_width = max(2, int(float(value)))


# def eraser_line_width(value):
#     global eraser_line
#     eraser_line = max(2, round(float(value)))

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

    button = tk.Button(frame, text=label_text, command=command, bg=frame_bg, fg=font_fg)
    button.pack(side=tk.TOP, fill=tk.X, pady=20, padx=20)

    return frame


def create_sticker_option(parent, label_text, sticker_tk, callback):
    frame = tk.Frame(parent, bg=frame_bg)
    frame.pack(fill=tk.X, pady=5, padx=10)

    button = Button(frame, image=sticker_tk, bg=frame_bg, relief="flat", command=callback)
    button.pack(side=tk.TOP, fill=tk.X, pady=20, padx=20)

    return frame

def create_text_option(parent, label_text, command):
    frame = tk.Frame(parent, bg=frame_bg)
    frame.pack(fill=tk.X, pady=5, padx=10)

    button = tk.Button(frame, text=label_text, command=command, bg=frame_bg, fg=font_fg)
    button.pack(side=tk.TOP, fill=tk.X, pady=10, padx=10)

    return frame

#stickers function
def add_sticker_to_canvas(sticker_image, original_image):

    global image_on_canvas
    # Default position (center of the canvas)
    x = canvas_width // 2
    y = canvas_height // 2
    sticker_id = canvas.create_image(x, y, image=sticker_image, anchor="center", tags="sticker")

    handle_size = 2
    handle_x = x + 25
    handle_y = y + 25
    handle_id = canvas.create_rectangle(handle_x, handle_y, handle_x + handle_size, handle_y + handle_size, fill='white', tags='resize_handle')

    # Store the image reference to prevent garbage collection
    if not hasattr(canvas, 'stickers'):
        canvas.stickers = {}
    canvas.stickers[sticker_id] = (original_image, (x, y),  handle_id)
    print(f"Sticker Image Type: {type(original_image)}")

    if not hasattr(canvas, 'image_refs'):
        canvas.image_refs = {}
    canvas.image_refs[sticker_id] = sticker_image

    # Bind events for dragging
    canvas.tag_bind(sticker_id, "<ButtonPress-1>", on_sticker_press)
    canvas.tag_bind(sticker_id, "<B1-Motion>", on_sticker_move)
    canvas.tag_bind(sticker_id, "<ButtonRelease-1>", on_sticker_release)

    # Bind events for resizing
    canvas.tag_bind(handle_id, "<ButtonPress-1>", on_handle_press)
    canvas.tag_bind(handle_id, "<B1-Motion>", on_handle_move)
    canvas.tag_bind(handle_id, "<ButtonRelease-1>", on_handle_release)

current_sticker = None
current_handle = None
start_x = 0
start_y = 0

def on_handle_press(event):
    global current_handle
    current_handle = event.widget.find_withtag("current")[0]

def on_handle_move(event):
    global current_handle
    if current_handle:
        sticker_id = get_sticker_id_from_handle(current_handle)
        if sticker_id:
            original_image, position, handle_id = canvas.stickers[sticker_id]

            # Calculate the new size based on the handle's movement
            current_coords = canvas.coords(current_handle)
            new_size = int(event.y - position[1] + 50)

            # Calculate new size based on handle movement
            new_size = int(event.y - position[1] + 50)
            if new_size > 10:
                resized_image = original_image.resize((new_size, new_size), Image.LANCZOS)
                resized_image_tk = ImageTk.PhotoImage(resized_image)

                # Update the sticker on the canvas
                canvas.itemconfig(sticker_id, image=resized_image_tk)
                canvas.stickers[sticker_id] = (original_image, position, handle_id)  # Update the stored image

                # Update the position of the handle
                handle_x = position[0] + new_size // 2
                handle_y = position[1] + new_size // 2
                canvas.coords(handle_id, handle_x, handle_y, handle_x + 2, handle_y + 2)
                # Keep a reference to avoid garbage collection
                canvas.image_refs[sticker_id] = resized_image_tk



def on_handle_release(event):
    global current_handle
    current_handle = None

# def get_sticker_id_from_handle(handle_id):
#     for sticker_id, (sticker_image, position, h_id) in canvas.stickers.items():
#         if h_id == handle_id:
#             return sticker_id
#     return None

def get_sticker_id_from_handle(handle_id):
    """Find the sticker associated with a resizing handle."""
    for sticker_id, (sticker_image, position, h_id) in canvas.stickers.items():
        if h_id == handle_id:
            return sticker_id
    return None


def on_sticker_press(event):
    global current_sticker, start_x, start_y
    # Find the sticker under the cursor
    items = canvas.find_overlapping(event.x, event.y, event.x, event.y)
    for item in items:
        if "sticker" in canvas.gettags(item):
            current_sticker = item
            start_x = event.x
            start_y = event.y
            break


def on_sticker_move(event):
    global current_sticker, start_x, start_y
    if current_sticker:
        dx = (event.x - start_x) * 0.5  # Scale down movement
        dy = (event.y - start_y) * 0.5

        # Get current position of the sticker
        current_coords = canvas.coords(current_sticker)  # Returns [x, y]
        new_x = current_coords[0] + dx
        new_y = current_coords[1] + dy

        # Canvas boundaries
        canvas_width = canvas.winfo_width()
        canvas_height = canvas.winfo_height()

        # Check boundaries before moving
        if 0 < new_x < canvas_width and 0 < new_y < canvas_height:
            canvas.move(current_sticker, dx, dy)

            # Update the sticker position in the dictionary
            sticker_image, position, handle_id = canvas.stickers[current_sticker]
            new_position = (position[0] + dx, position[1] + dy)
            canvas.stickers[current_sticker] = (sticker_image, new_position, handle_id)

            # Move the handle
            canvas.move(handle_id, dx, dy)

            start_x = event.x
            start_y = event.y

def on_sticker_release(event):
    """Handle the mouse button release after dragging a sticker."""
    global current_sticker
    if current_sticker:
        current_sticker = None

def select_sticker(sticker_tk, sticker_image):
    add_sticker_to_canvas(sticker_tk, sticker_image)

def create_sticker_options_grid(parent_frame, stickers, columns=2):
    photo_image_references = []  # Prevent garbage collection of images

    for idx, sticker in enumerate(stickers):
        # Calculate row and column for each sticker
        row = idx // columns
        col = idx % columns

        # Dynamically create the callback for selecting a sticker
        callback = partial(select_sticker, sticker["tk_image"], sticker["image"])

        # Create a button for the sticker
        button = tk.Button(
            parent_frame,
            image=sticker["tk_image"],
            compound="top",
            command=callback,
            bg=frame_bg
        )
        button.grid(row=row, column=col, padx=10, pady=5)  # Place the button in the grid

        # Store the image reference to prevent garbage collection
        photo_image_references.append(sticker["tk_image"])

def show_context_menu(event):
    """Display a context menu on right-click."""
    global selected_sticker
    # Find the sticker under the cursor
    items = canvas.find_overlapping(event.x, event.y, event.x, event.y)
    for item in items:
        if "sticker" in canvas.gettags(item):  # Check if it's a sticker
            selected_sticker = item
            context_menu.post(event.x_root, event.y_root)  # Show the menu
            break

def delete_selected_sticker():
    """Delete the currently selected sticker."""
    global selected_sticker
    if selected_sticker and selected_sticker in canvas.stickers:
        # Get the sticker data
        _, _, handle_id = canvas.stickers[selected_sticker]

        # Delete the sticker and its handle
        canvas.delete(selected_sticker)
        canvas.delete(handle_id)

        # Remove the sticker from the dictionary
        del canvas.stickers[selected_sticker]
        del canvas.image_refs[selected_sticker]

        print(f"Sticker {selected_sticker} deleted.")
        selected_sticker = None

# Undo and redo functionality
#
# def save_state():
#     """Save the current state of the canvas to the undo stack."""
#     state = {
#         'stickers': canvas.stickers.copy(),
#         'image': image.copy(),
#         'drawing_layer': drawing_layer.copy()
#     }
#     undo_stack.append(state)
#     redo_stack.clear()
#
# def undo():
#     global image, drawing_layer
#     if undo_stack:
#         state = undo_stack.pop()
#         redo_stack.append(
#             {
#                 'stickers': canvas.stickers.copy(),
#                 'image': image.copy(),
#                 'drawing_layer': drawing_layer.copy()
#             }
#         )
#         canvas.stickers = state['stickers']
#         image = state['image']
#         drawing_layer = state['drawing_layer']
#         update_image_display(image)
#         redraw_canvas_stickers()
#
# def redo():
#     global image, drawing_layer
#     if redo_stack:
#         state = redo_stack.pop()
#         undo_stack.append(
#             {
#                 'stickers': canvas.stickers.copy(),
#                 'image': image.copy(),
#                 'drawing_layer': drawing_layer.copy()
#             }
#         )
#         canvas.stickers = state['stickers']
#         image = state['image']
#         drawing_layer = state['drawing_layer']
#         update_image_display(image)
#         redraw_canvas_stickers()

# def redraw_canvas_stickers():
#     """Redraw all stickers on the canvas."""
#     canvas.delete("sticker")  # Clear existing stickers
#     for sticker_id, (original_image, position, current_size, handle_ids) in canvas.stickers.items():
#         sticker_image_tk = ImageTk.PhotoImage(original_image.resize(current_size, Image.LANCZOS))
#         canvas.create_image(position[0], position[1], image=sticker_image_tk, anchor="center", tags="sticker")
#         canvas.image_refs[sticker_id] = sticker_image_tk  # Keep a reference to avoid garbage collection

# def create_undo_redo_buttons(parent_frame):
#     undo_button = Button(parent_frame, text="Undo", command=undo, bg=frame_bg, fg=font_fg)
#     undo_button.pack(side=tk.RIGHT, padx=5, pady=5)
#     redo_button = Button(parent_frame, text="Redo", command=redo, bg=frame_bg, fg=font_fg)
#     redo_button.pack(side=tk.RIGHT, padx=5, pady=5)

#----------------------Text Tool---------------------------------
# Store text IDs globally
text_ids = []

select_text_id = None
text_styles = {"Normal": ("Arial", 20, "normal"),  # Default styles
               "Bold": (r"E:\daily_bubble\DailyBubble.ttf", 20, "bold"),
               "Italic": ("Arial", 20, "italic"),
               "Bold Italic": ("Arial", 20, "bold italic"),
               "Underlined": ("Verdana", 20, "underline"),
               "Script": ("Lucida Handwriting", 24, "normal"),
               }

def add_textbox():
    # Create a text box at the center of the canvas
    global selected_text_id, text_ids
    text_id = canvas.create_text(canvas_width // 2, canvas_height // 2, text="Your Text Here",
                                 font=("Arial", 15), fill="black", tags="text")
    text_ids.append(text_id)  # Store the text ID

    # Create a rectangle around the text for resizing
    bbox = canvas.bbox(text_id)
    rect_id = canvas.create_rectangle(bbox, outline="blue", width=2, tags="resize_handle")

    # Set the newly added text as selected
    selected_text_id = text_id

    # Bind events for moving, resizing, and editing text
    canvas.tag_bind(text_id, "<B1-Motion>", lambda event, tid=text_id, rid=rect_id: move_text(event, tid, rid))
    canvas.tag_bind(text_id, "<Button-1>", lambda event, tid=text_id: select_text(tid))  # Select text on click
    canvas.tag_bind(text_id, "<Double-1>", lambda event, tid=text_id, rid=rect_id: edit_text(event, tid, rid))
    canvas.tag_bind(rect_id, "<B1-Motion>", lambda event, tid=text_id, rid=rect_id: resize_text(event, tid, rid))

def move_text(event, text_id, rect_id):
    # Move the text and the rectangle
    canvas.coords(text_id, event.x, event.y)
    update_rectangle(text_id, rect_id)

# def resize_text(event, text_id, rect_id):
#     current_font = canvas.itemcget(text_id, "font")
#     # Resize the text by dragging the rectangle
#     font_family, font_size, *font_styles = current_font.split()
#     new_size = int(abs(event.y - canvas.coords(rect_id)[1]))  # Calculate font size based on drag distance
#     if new_size > 5:  # Minimum font size
#         # Rebuild the font configuration with the new size
#         new_font = (font_family, new_size, " ".join(font_styles))
#         canvas.itemconfig(text_id, font=new_font)
#         update_rectangle(text_id, rect_id)

def resize_text(event, text_id, rect_id):
    # Always get the current font properties dynamically
    current_font = canvas.itemcget(text_id, "font")

    # Parse the font family, size, and style safely
    font_parts = current_font.split()
    font_family = font_parts[0] if len(font_parts) > 0 else "Arial"  # Default to Arial if missing
    font_size = int(font_parts[1])if len(font_parts) > 1 else 20  # Default to size 20 if missing


    # Calculate the new font size
    new_size = int(abs(event.y - canvas.coords(rect_id)[1]))  # Based on drag distance
    if new_size > 5:  # Minimum font size
        # Rebuild the font configuration dynamically
        new_font = (font_family, new_size)
        canvas.itemconfig(text_id, font=new_font)
        update_rectangle(text_id, rect_id)


def update_rectangle(text_id, rect_id):
    # Update the rectangle position around the text
    bbox = canvas.bbox(text_id)
    canvas.coords(rect_id, bbox)

def edit_text(event, text_id, rect_id):
    # Open an entry box to edit the text
    def save_text(event=None):
        new_text = entry.get()
        canvas.itemconfig(text_id, text=new_text)
        entry.destroy()
        update_rectangle(text_id, rect_id)

    x, y = canvas.coords(text_id)
    current_text = canvas.itemcget(text_id, "text")
    entry = tk.Entry(root, font=("Arial", 20))
    entry.insert(0, current_text)
    entry.place(x=x, y=y, anchor="center")
    entry.bind("<Return>", save_text)
    entry.focus()

def change_text_color():
    # Open a color picker dialog to change the text color of the selected text
    global selected_text_id
    if selected_text_id:
        color = colorchooser.askcolor(title="Choose Text Color")[1]
        if color:
            canvas.itemconfig(selected_text_id, fill=color)

def select_text(text_id):
    # Mark the clicked text as selected
    global selected_text_id
    selected_text_id = text_id

def add_new_style():
    # Add a new text style dynamically
    def save_style():
        style_name = style_name_entry.get()
        font_family = font_family_entry.get()
        font_size = int(font_size_entry.get())
        font_weight = "bold" if bold_var.get() else "normal"
        font_slant = "italic" if italic_var.get() else "roman"
        new_style = (font_family, font_size, f"{font_weight} {font_slant}".strip())
        text_styles[style_name] = new_style
        style_dropdown['values'] = list(text_styles.keys())
        add_style_window.destroy()

    add_style_window = tk.Toplevel(root)
    add_style_window.title("Add New Style")

    tk.Label(add_style_window, text="Style Name:").grid(row=0, column=0, padx=5, pady=5)
    style_name_entry = tk.Entry(add_style_window)
    style_name_entry.grid(row=0, column=1, padx=5, pady=5)

    tk.Label(add_style_window, text="Font Family:").grid(row=1, column=0, padx=5, pady=5)
    font_family_entry = tk.Entry(add_style_window)
    font_family_entry.grid(row=1, column=1, padx=5, pady=5)

    tk.Label(add_style_window, text="Font Size:").grid(row=2, column=0, padx=5, pady=5)
    font_size_entry = tk.Entry(add_style_window)
    font_size_entry.grid(row=2, column=1, padx=5, pady=5)

    bold_var = tk.BooleanVar()
    tk.Checkbutton(add_style_window, text="Bold", variable=bold_var).grid(row=3, column=0, padx=5, pady=5)
    italic_var = tk.BooleanVar()
    tk.Checkbutton(add_style_window, text="Italic", variable=italic_var).grid(row=3, column=1, padx=5, pady=5)

    save_button = tk.Button(add_style_window, text="Save Style", command=save_style)
    save_button.grid(row=4, column=0, columnspan=2, pady=10)

def apply_text_style(style_name):
    # Apply the selected text style to the currently selected text
    global selected_text_id
    if selected_text_id and style_name in text_styles:
        canvas.itemconfig(selected_text_id, font=text_styles[style_name])

def apply_font_style(font_name):
    # Apply the selected font style to the currently selected text
    global selected_text_id
    if selected_text_id:
        # Use the selected font with a default size of 20
        canvas.itemconfig(selected_text_id, font=(font_name, 20))


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

sidebar_canvas = Canvas(root, width=150, height=840, bg="lightgrey")
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
bw_image_path = r"C:\Users\HP\OneDrive\Pictures\b&w.jpeg"  # Replace with your image path
bw_filter = create_filter_option(sidebar_frame, bw_image_path, "B&W", apply_bw)

warmer_image_path = r"C:\Users\HP\OneDrive\Pictures\warm-contrast.jpeg"
warmer_filter = create_filter_option(sidebar_frame, warmer_image_path, "Warm Contrast", apply_warmer)

blur_image_path = r"C:\Users\HP\OneDrive\Pictures\blur.jpeg"
blur_filter = create_filter_option(sidebar_frame, blur_image_path, "Blur", apply_blur)

# golden_image_path =r"C:\Users\HP\OneDrive\Pictures\golden.jpeg"
# golden_filter = create_filter_option(sidebar_frame, golden_image_path, "Golden")

sharpen_film_path = r"C:\Users\HP\OneDrive\Pictures\sharpen.jpeg"
sharpen_filter = create_filter_option(sidebar_frame, sharpen_film_path, "Sharpen", apply_sharpen)

sepia_image_path = r"C:\Users\HP\OneDrive\Pictures\sepia2.jpg"
sepia_filter = create_filter_option(sidebar_frame, sepia_image_path, "Sepia", apply_sepia)

smooth_image_path = r"C:\Users\HP\OneDrive\Pictures\golden.jpeg"
smooth_filter = create_filter_option(sidebar_frame, smooth_image_path, "Smooth", apply_smoothen_filter)

vintage_image_path = r"C:\Users\HP\OneDrive\Pictures\vintage.jpg"
vintage_filter = create_filter_option(sidebar_frame, vintage_image_path, "Vintage", apply_vintage_filter)

cartoon_image_path = r"C:\Users\HP\OneDrive\Pictures\vintage.jpg"
cartoon_filter = create_filter_option(sidebar_frame, cartoon_image_path, "Cartoon", apply_cartoon_filter)


# Toggle Filter sidebar
def toggle_sidebar():
    if sidebar_canvas.winfo_ismapped():
        hide_filter_sidebar()
    else:
        if adjustment_sidebar_canvas.winfo_ismapped():
            hide_adjust_sidebar()
        elif draw_sidebar_canvas.winfo_ismapped():
            hide_draw_sidebar()
        elif sticker_sidebar_canvas.winfo_ismapped():
            hide_sticker_sidebar()
        elif text_sidebar_canvas.winfo_ismapped():
            hide_text_sidebar()
        show_filter_sidebar()


# Main Frame container
frame_bg = "#252525"
button_color = "#292929"
font_fg = "#FFFFFF"

main_frame = tk.Frame(root, background=frame_bg)
main_frame.pack(fill=tk.Y, side=tk.LEFT)

# Resize frame
resize_frame = tk.Frame(main_frame, background=frame_bg)
resize_frame.pack(side=tk.TOP, fill=tk.X, pady=5)

# Load icon Path
resize_icon_path = r"E:/PyCharm Community Edition 2024.2.1/PythonProjects/photo_customize/assests/Transform.png"
filter_icon_path = r"E:/PyCharm Community Edition 2024.2.1/PythonProjects/photo_customize/assests/Color Swatch 01.png"
adjust_icon_path = r"E:/PyCharm Community Edition 2024.2.1/PythonProjects/photo_customize/assests/Filters 1.png"
draw_icon_path = r"E:/PyCharm Community Edition 2024.2.1/PythonProjects/photo_customize/assests/Color Picker.png"
sticker_icon_path = r"E:/PyCharm Community Edition 2024.2.1/PythonProjects/photo_customize/assests/Sticker.png"
text_icon_path = r"E:/PyCharm Community Edition 2024.2.1/PythonProjects/photo_customize/assests/Type 01.png"

# Load and resize images for buttons
resize_icon = Image.open(resize_icon_path).resize((30, 30))
filter_icon = Image.open(filter_icon_path).resize((30, 30))
adjust_icon = Image.open(adjust_icon_path).resize((30, 30))
draw_icon = Image.open(draw_icon_path).resize((30, 30))
sticker_icon = Image.open(sticker_icon_path).resize((30, 30))
text_icon = Image.open(text_icon_path).resize((30,30))

# convert to Tkinter-compatible images
resize_icon_tk = ImageTk.PhotoImage(resize_icon)
filter_icon_tk = ImageTk.PhotoImage(filter_icon)
adjust_icon_tk = ImageTk.PhotoImage(adjust_icon)
draw_icon_tk = ImageTk.PhotoImage(draw_icon)
sticker_icon_tk = ImageTk.PhotoImage(sticker_icon)
text_icon_tk = ImageTk.PhotoImage(text_icon)

# Filter Frame
filter_frame = tk.Frame(main_frame, background=frame_bg)
filter_frame.pack(side=tk.TOP, fill=tk.X,pady=5)


# ---------------------Adjustment-------------------
# toggler of adjust
def toggle_adjust_sidebar():
    if adjustment_sidebar_canvas.winfo_ismapped():
        hide_adjust_sidebar()
    else:
        if sidebar_canvas.winfo_ismapped():
            hide_filter_sidebar()
        elif draw_sidebar_canvas.winfo_ismapped():
            hide_draw_sidebar()
        elif sticker_sidebar_canvas.winfo_ismapped():
            hide_sticker_sidebar()
        elif text_sidebar_canvas.winfo_ismapped():
            hide_text_sidebar()
        show_adjust_sidebar()
        is_draw_tool_active = False
        is_erasing = False


# adjustment sidebar
adjustment_sidebar_canvas = Canvas(root, width=150, height=canvas_height, background=frame_bg)
adjustment_sidebar_frame = Frame(adjustment_sidebar_canvas, background=frame_bg)

adjustment_sidebar_canvas.create_window((0, 0), window=adjustment_sidebar_frame, anchor="nw")

# Adjustment effects
adjust_frame = tk.Frame(main_frame, background=frame_bg)
adjust_frame.pack(side=tk.TOP, fill=tk.X, pady=5)

# Create slider for adjustments
brightness_slider = create_adjustment_slider_option(adjustment_sidebar_frame, "Brightness", apply_brightness)
contrast_slider = create_adjustment_slider_option(adjustment_sidebar_frame, "Contrast", apply_contrast)
saturation_slider = create_adjustment_slider_option(adjustment_sidebar_frame, "Saturation", apply_saturation)
sharpness_slider = create_adjustment_slider_option(adjustment_sidebar_frame, "Sharpness", apply_sharpness)
temperature_slider = create_adjustment_slider_option(adjustment_sidebar_frame, "Temperature", apply_temperature)

# --------------Drawing tools--------------
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
        elif sticker_sidebar_canvas.winfo_ismapped():
            hide_sticker_sidebar()
        elif text_sidebar_canvas.winfo_ismapped():
            hide_text_sidebar()
        show_draw_sidebar()
        is_draw_tool_active = True


is_drawing = False
drawing_color = "black"
line_width = 2

# Frame for Draw Sidebar

draw_sidebar_canvas = Canvas(root, width=150, height=canvas_height, background=frame_bg)
draw_sidebar_frame = Frame(draw_sidebar_canvas, background=frame_bg)

# Create the drawing sidebar
draw_sidebar_canvas.create_window((0, 0), window=draw_sidebar_frame, anchor="nw")

# Frame for Draw Sidebar
draw_frame = tk.Frame(main_frame, background=frame_bg)
draw_frame.pack(side=tk.TOP, fill=tk.X, pady=5)

color_button = create_draw_option(draw_sidebar_frame, "Change Color", change_pen_color)
# Add Line Width Slider
line_width_slider = create_adjustment_slider_option(
    draw_sidebar_frame,  # Parent frame
    "Line Width",  # Label text
    change_line_width,  # Command function
    from_=1,  # Minimum line width
    to=30  # Maximum line width
)

draw_button = create_draw_option(draw_sidebar_frame, "Draw", activate_draw)

eraser_button = create_draw_option(draw_sidebar_frame, "Eraser", activate_eraser)

# ----------------------sticker------------------
# paths of stickers images
# sticker1_path = r"E:/PyCharm Community Edition 2024.2.1/PythonProjects/photo_customize/assests/cute_emoji_heart_icon.png"
# sticker2_path = r"E:/PyCharm Community Edition 2024.2.1/PythonProjects/photo_customize/assests/couple_heart_love_icon.png"

sticker_paths = [
    {"title": "sticker 1", "path": r"E:/PyCharm Community Edition 2024.2.1/PythonProjects/photo_customize/assests/cute_emoji_heart_icon.png"},
    {"title": "sticker 2", "path": r"E:/PyCharm Community Edition 2024.2.1/PythonProjects/photo_customize/assests/couple_heart_love_icon.png"},
    {"title": "sticker 3", "path": r"E:/PyCharm Community Edition 2024.2.1/PythonProjects/photo_customize/assests/3D Sparkling Sticker by Emoji.gif"},
    {"title": "sticker 4", "path": r"E:/PyCharm Community Edition 2024.2.1/PythonProjects/photo_customize/assests/90S 80S Sticker by Ethan Barnowsky.gif"},
    {"title": "sticker 5", "path": r"E:/PyCharm Community Edition 2024.2.1/PythonProjects/photo_customize/assests/Army Jin Sticker.gif"},
    {"title": "sticker 6", "path": r"E:/PyCharm Community Edition 2024.2.1/PythonProjects/photo_customize/assests/arrow_heart_love_icon.png"},
    {"title": "sticker 7", "path": r"E:/PyCharm Community Edition 2024.2.1/PythonProjects/photo_customize/assests/Awkward Wide Eyed Sticker by Emoji.gif"},
    {"title": "sticker 8", "path": r"E:/PyCharm Community Edition 2024.2.1/PythonProjects/photo_customize/assests/be-creative.png"},
    {"title": "sticker 9", "path": r"E:/PyCharm Community Edition 2024.2.1/PythonProjects/photo_customize/assests/Doodle Lines Sticker by Claudia Guariglia (Enyoudraws).gif"},
    {"title": "sticker 10", "path": r"E:/PyCharm Community Edition 2024.2.1/PythonProjects/photo_customize/assests/Best Friend Prints Sticker.gif"},
    {"title": "sticker 11", "path": r"E:/PyCharm Community Edition 2024.2.1/PythonProjects/photo_customize/assests/Boho Background Sticker.gif"},
    {"title": "sticker 12", "path": r"E:/PyCharm Community Edition 2024.2.1/PythonProjects/photo_customize/assests/cassette-tape.png"},
    {"title": "sticker 13", "path": r"E:/PyCharm Community Edition 2024.2.1/PythonProjects/photo_customize/assests/celebration.png"},
    {"title": "sticker 14", "path": r"E:/PyCharm Community Edition 2024.2.1/PythonProjects/photo_customize/assests/Colors Monday Sticker.gif"},
    {"title": "sticker 15", "path": r"E:/PyCharm Community Edition 2024.2.1/PythonProjects/photo_customize/assests/Crown Sticker by imoji.gif"},
    {"title": "sticker 16", "path": r"E:/PyCharm Community Edition 2024.2.1/PythonProjects/photo_customize/assests/cute_emoji_heart_icon.png"},
    {"title": "sticker 17", "path": r"E:/PyCharm Community Edition 2024.2.1/PythonProjects/photo_customize/assests/Finde Good Vibes Sticker.gif"},
    {"title": "sticker 18", "path": r"E:/PyCharm Community Edition 2024.2.1/PythonProjects/photo_customize/assests/Flower Hearts Sticker by Beyond Boss(1).gif"},
    {"title": "sticker 19", "path": r"E:/PyCharm Community Edition 2024.2.1/PythonProjects/photo_customize/assests/Pink Arrow Sticker.gif"},
    {"title": "sticker 20", "path": r"E:/PyCharm Community Edition 2024.2.1/PythonProjects/photo_customize/assests/Pink Love Sticker by Wildflower Cases.gif"},
    {"title": "sticker 21", "path": r"E:/PyCharm Community Edition 2024.2.1/PythonProjects/photo_customize/assests/rainbow.png"},
    {"title": "sticker 22", "path": r"E:/PyCharm Community Edition 2024.2.1/PythonProjects/photo_customize/assests/Pink Stars Sticker.gif"},
    {"title": "sticker 23", "path": r"E:/PyCharm Community Edition 2024.2.1/PythonProjects/photo_customize/assests/reading.png"},
    {"title": "sticker 24", "path": r"E:/PyCharm Community Edition 2024.2.1/PythonProjects/photo_customize/assests/Stars Doodle Sticker.gif"},

]

sticker_size = (50, 50)
# Function to dynamically load and resize stickers
def load_stickers(sticker_data):
    stickers = []
    for sticker in sticker_data:
        try:
            sticker_image = Image.open(sticker["path"]).resize(sticker_size, Image.LANCZOS)
            sticker_tk = ImageTk.PhotoImage(sticker_image)
            stickers.append({"title": sticker["title"], "tk_image": sticker_tk, "image": sticker_image})
        except Exception as e:
            print(f"Error loading sticker {sticker['title']}: {e}")
    return stickers

def toggle_sticker_sidebar():
    if sticker_sidebar_canvas.winfo_ismapped():
        hide_sticker_sidebar()
    else:
        if sidebar_canvas.winfo_ismapped():
            hide_filter_sidebar()
        elif adjustment_sidebar_canvas.winfo_ismapped():
            hide_adjust_sidebar()
        elif draw_sidebar_canvas.winfo_ismapped():
            hide_draw_sidebar()
        elif text_sidebar_canvas.winfo_ismapped():
            hide_text_sidebar()
        show_sticker_sidebar()


sticker_sidebar_canvas = Canvas(root, width=150, height=canvas_height, background=frame_bg)
sticker_sidebar_frame = Frame(sticker_sidebar_canvas, background=frame_bg)

# create window
sticker_sidebar_canvas.create_window((0, 0), window=sticker_sidebar_frame, anchor="nw")

# Frame for sticker Sidebar
sticker_frame = tk.Frame(main_frame, background=frame_bg)
sticker_frame.pack(side=tk.TOP, fill=tk.X, pady=5)

# Load stickers and dynamically create options
loaded_stickers = load_stickers(sticker_paths)
photo_image_references = []  # Prevent garbage collection of images

# Create a grid layout for the stickers (2 columns)
# create_sticker_options_grid(sticker_sidebar_frame, loaded_stickers, columns=2)
# for sticker in loaded_stickers:
#     # Create dynamic selection functions using `partial`
#     callback = partial(select_sticker, sticker["tk_image"], sticker["image"])
#     create_sticker_option(sticker_sidebar_frame, sticker["title"], sticker["tk_image"], callback)
#     photo_image_references.append(sticker["tk_image"])  # Prevent garbage collection of images

# Load stickers and create a grid of sticker options

create_sticker_options_grid(sticker_sidebar_frame, loaded_stickers, columns=2)

# Create a context menu
context_menu = tk.Menu(root, tearoff=0)
context_menu.add_command(label="Delete", command=delete_selected_sticker)

#-------------------Text Tool----------------------------------------------

def toggle_text_sidebar():
    if text_sidebar_canvas.winfo_ismapped():
        hide_text_sidebar()
    else:
        if sidebar_canvas.winfo_ismapped():
            hide_filter_sidebar()
        elif adjustment_sidebar_canvas.winfo_ismapped():
            hide_adjust_sidebar()
        elif draw_sidebar_canvas.winfo_ismapped():
            hide_draw_sidebar()
        elif sticker_sidebar_canvas.winfo_ismapped():
            hide_sticker_sidebar()
        show_text_sidebar()
        canvas.update_idletasks()

# Get all available font families on the system
available_fonts = list(font.families())

text_sidebar_canvas = Canvas(root,width=150, height=canvas_height, background=frame_bg)
text_sidebar_frame = Frame(text_sidebar_canvas, background=frame_bg)

text_sidebar_canvas.create_window((0,0), window=text_sidebar_frame, anchor='nw')

#frame for text
text_frame = tk.Frame(main_frame, background=frame_bg)
text_frame.pack(side=tk.TOP, fill=tk.X,pady=5)

create_text_option(text_sidebar_frame, "𝚃 Add a text box", add_textbox)
create_text_option(text_sidebar_frame, "Change Text Color", change_text_color)


# Dropdown menu for text styles
style_dropdown = ttk.Combobox(text_sidebar_frame, values=list(text_styles.keys()), state="readonly", width=17)
style_dropdown.set("Normal")
style_dropdown.pack(padx=10)

# Apply text style button
apply_style_button = tk.Button(text_sidebar_frame, text="Apply Style", command=lambda: apply_text_style(style_dropdown.get()), bg=frame_bg, fg=font_fg)
apply_style_button.pack(pady=10)

# Button to add new styles
add_style_button = tk.Button(text_sidebar_frame, text="Add New Style", command=add_new_style, bg=frame_bg, fg=font_fg)
add_style_button.pack(pady=10)

# Dropdown menu for font styles
font_dropdown = ttk.Combobox(text_sidebar_frame, values=available_fonts, state="readonly", width=17)
font_dropdown.set("Select Font Style")
font_dropdown.pack(pady=10, padx=10)

# Apply font style button
apply_font_button = tk.Button(text_sidebar_frame, text="Apply Font", command=lambda: apply_font_style(font_dropdown.get()),bg=frame_bg, fg=font_fg)
apply_font_button.pack(pady=10, padx=5)

# -------------------------------------------------------------------

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
    label.pack(side="top", pady=3)  # Add label below the icon

    button_frame.pack(side="left", padx=20, pady=5)  # Pack the frame with button and label


# Modern Buttons with Icons and Text
create_icon_button(resize_frame, resize_icon_tk, "Resize", open_new_window)
create_icon_button(filter_frame, filter_icon_tk, "Filter", toggle_sidebar)
create_icon_button(adjust_frame, adjust_icon_tk, "Adjust", toggle_adjust_sidebar)
create_icon_button(draw_frame, draw_icon_tk, "Draw", toggle_draw_sidebar)
create_icon_button(sticker_frame, sticker_icon_tk, "Sticker", toggle_sticker_sidebar)
create_icon_button(text_frame, text_icon_tk, "Text", toggle_text_sidebar)

# ---------------Canvas----------------
# Canvas for image display (Expands to the right of the sidebar)
canvas = Canvas(root, bg="#101010", width=canvas_width, height=canvas_height, relief="solid", borderwidth=2)
canvas.pack(fill=tk.BOTH, expand=True, side=tk.LEFT)

# Initialize a dictionary to store image references
canvas.image_refs = {}

# Mouse events for cropping
canvas.bind("<ButtonPress-1>", on_press)  # Left mouse button press to start cropping
canvas.bind("<B1-Motion>", on_drag)  # Dragging the mouse while holding the left button
canvas.bind("<ButtonRelease-1>", on_release)  # Left mouse button release to finalize cropping
canvas.bind("<Configure>", lambda event: update_image_display(image) if image else None)
# Bind right-click to show the context menu
canvas.bind("<Button-3>", show_context_menu)
#create_undo_redo_buttons(menu_bar_frame)

root.mainloop()

