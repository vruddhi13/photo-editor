from PIL import Image, ImageTk, ImageOps, ImageEnhance, ImageFilter, ImageDraw
from main import update_image_display

#brightness adjustment
def apply_brightness():
    global image
    if image:
        enhancer = ImageEnhance.Brightness(image)
        enhanced_image = enhancer.enhance(1.2)
        update_image_display(enhanced_image)
        image = enhanced_image

def apply_contrast():
    global image
    if image:
        enhancer = ImageEnhance.Contrast(image)
        enhance_image = enhancer.enhance(1.5)
        update_image_display(enhance_image)
        image = enhance_image

def apply_saturation(value):
    global image
    if image:
        factor = float(value)
        enhancer = ImageEnhance.Color(image)
        enhance_image = enhancer.enhance(factor)
        image = enhance_image
        update_image_display(enhance_image)

def apply_sharpness(value):
    global image
    if image:
        factor = float(value)
        enhancer = ImageEnhance.Sharpness(image)
        enhance_image = enhancer.enhance(factor)
        image = enhance_image
        update_image_display(enhance_image)

def apply_temperature(value):
    global image
    if image:
        rgb_image = image.convert('RGB')
        r, g, b = rgb_image.split()

        factor = float(value)
        if factor>1.0:
            #warm effect: Increase red channel, decrease blue channel
            r = r.point(lambda i:min(255, i * factor))
            b = b.point(lambda i:max(0, i / factor))
        elif factor<1.0:
            # Cool effect: Decrease red channel, increase blue channel
            r = r.point(lambda i:max(0, i * factor))
            b = b.point(lambda i:min(255, i / factor))

        #merger channel back
        adjusted_image = Image.merge("RGB", (r, g, b))
        image = adjusted_image
        update_image_display(adjusted_image)
