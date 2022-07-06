import base64
from io import BytesIO
from urllib.request import urlopen
import uuid
from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont
from flask import send_file

def find_font_size(text, font, image, target_width_ratio):
    tested_font_size = 100
    tested_font = ImageFont.truetype(urlopen(font), tested_font_size)
    observed_width, observed_height = get_text_size(text, image, tested_font)
    estimated_font_size = tested_font_size / (observed_width / image.width) * target_width_ratio
    return round(estimated_font_size)

def get_text_size(text, image, font):
    im = Image.new('RGB', (image.width, image.height))
    draw = ImageDraw.Draw(im)
    return draw.textsize(text, font)

def spongebobify(text):
    res = ""
    for count, value in enumerate(text):
        if(count % 2 == 0):
            res += value.upper()
        else:
            res += value.lower()
    return res

def create_image(text, font, image_path, text_x_pos, text_y_pos):
    image = Image.open(urlopen(image_path))
    font_size = find_font_size(text, font, image, 0.6)
    font = ImageFont.truetype(urlopen(font), font_size)
    # # Call draw Method to add 2D graphics in an image
    I1 = ImageDraw.Draw(image)
    # # Add Text to an image
    I1.text((text_x_pos, text_y_pos), spongebobify(text), font=font, fill=(255, 255, 255))
    img_io = BytesIO()
    image.save(img_io, format='JPEG')
    img_io.seek(0)
    return base64.b64encode(img_io.getvalue())