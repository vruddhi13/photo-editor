from main import update_image_display
from PIL import Image, ImageTk, ImageOps, ImageEnhance, ImageFilter, ImageDraw
from tkinter import *

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

        # Convert the image to PhotoImage for display in Tkinte
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