from gui import sidebar_canvas, draw_sidebar_canvas, adjustment_sidebar_canvas,update_image_display,image,canvas,frame_bg, font_fg, button_color
from tkinter import *
import tkinter as tk
from PIL import ImageTk
from filters_file import apply_smoothen_filter, apply_sepia, apply_bw, apply_blur, apply_warmer, apply_sharpen

# Sidebar and Canvas for filter
def show_filter_sidebar():
    global canvas_width
    # Show the sidebar with filter buttons
    sidebar_canvas.pack(side=tk.LEFT, fill=tk.Y, padx=10)
    canvas_width = 1150  # Adjust the canvas width to accommodate the sidebar
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
    frame = Frame(parent, bg="#292828", width=120, height=50, highlightbackground="white", highlightthickness=1)
    frame.pack_propagate(False)
    frame.pack(pady=10, padx=10)

    #add the adjustment label
    text_label = Label(frame, text=name, bg="black", fg="white", font=('Arial',10))
    text_label.pack()

    #bind click event to button
    button = Button(frame, text="Apply", command=command)
    button.pack()

    return frame

#Adjustment Slider
def create_adjustment_slider_option(parent, label_text, command, from_=0.5, to=2.0):
    frame = tk.Frame(parent, bg=frame_bg)
    frame.pack(fill=tk.X, pady=5, padx=15)

    label = tk.Label(frame, text=label_text, bg=frame_bg, fg=font_fg)
    label.pack(side=tk.TOP, anchor="w")

    slider = tk.Scale(
        frame,
        from_= from_,
        to=to,
        resolution=0.1,
        orient=tk.HORIZONTAL,
        command=command,
        bg=frame_bg,
        fg=font_fg,
        troughcolor='white',
        highlightthickness=0
    )
    slider.pack(fill=tk.X, pady=5,padx=10)
    slider.set(1.0)
    return slider

def create_draw_option(parent, label_text, command):
    frame = tk.Frame(parent, bg=frame_bg)
    frame.pack(fill=tk.X, pady=5, padx=10)

    button = tk.Button(frame,text=label_text, command=command, bg=frame_bg, fg=font_fg)
    button.pack(side=tk.TOP, fill=tk.X, pady=20, padx=20)

    return frame

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
