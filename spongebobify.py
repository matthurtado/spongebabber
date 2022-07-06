import base64
from io import BytesIO
from urllib.request import urlopen
from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont

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

def create_image(text, font, image_path, text_x_pos, text_y_pos, target_width_ratio, sponge_the_text):
    image = Image.open(urlopen(image_path))
    font_size = find_font_size(text, font, image, target_width_ratio)
    font = ImageFont.truetype(urlopen(font), font_size)
    text_on_image = spongebobify(text) if sponge_the_text else text
    # # Call draw Method to add 2D graphics in an image
    I1 = ImageDraw.Draw(image)
    # # Add Text to an image
    I1.text((text_x_pos, text_y_pos), text_on_image, font=font, fill=(255, 255, 255))
    img_io = BytesIO()
    image.save(img_io, format='JPEG')
    img_io.seek(0)
    return base64.b64encode(img_io.getvalue())