import base64
from io import BytesIO
from urllib.request import urlopen
from PIL import Image, ImageDraw, ImageFont, ImageSequence


def find_font_size(text, font, image, target_width_ratio):
    tested_font_size = 100
    tested_font = ImageFont.truetype(urlopen(font), tested_font_size)
    observed_width, observed_height = get_text_size(text, image, tested_font)
    estimated_font_size = (
        tested_font_size / (observed_width / image.width) * target_width_ratio
    )
    return round(estimated_font_size)


def get_text_size(text, image, font):
    im = Image.new("RGB", (image.width, image.height))
    draw = ImageDraw.Draw(im)
    return draw.textsize(text, font)


def spongebobify(text):
    res = ""
    for count, value in enumerate(text):
        if count % 2 == 0:
            res += value.upper()
        else:
            res += value.lower()
    return res


def create_image(
    text, font, image_path, text_x_pos, text_y_pos, target_width_ratio, sponge_the_text
):
    image = Image.open(urlopen(image_path))
    font_size = find_font_size(text, font, image, target_width_ratio)
    font = ImageFont.truetype(urlopen(font), font_size)
    text_on_image = spongebobify(text) if sponge_the_text else text
    img_io = BytesIO()
    if ".gif" in image_path:
        # A list of the frames to be outputted
        frames = []
        # Loop over each frame in the animated image
        for frame in ImageSequence.Iterator(image):
            # Draw the text on the frame
            d = ImageDraw.Draw(frame)
            d.text(
                (text_x_pos, text_y_pos),
                text_on_image,
                font=font,
                fill=(255, 255, 255),
                stroke_fill=(0, 0, 0),
                stroke_width=3,
            )
            del d

            # However, 'frame' is still the animated image with many frames
            # It has simply been seeked to a later frame
            # For our list of frames, we only want the current frame

            # Saving the image without 'save_all' will turn it into a single frame image, and we can then re-open it
            # To be efficient, we will save it to a stream, rather than to file
            b = BytesIO()
            frame.save(b, format="GIF")
            frame = Image.open(b)

            # Then append the single frame image to a list of frames
            frames.append(frame)

        # Save the frames as a new image
        frames[0].save(img_io, save_all=True, append_images=frames[1:], format="GIF")
        img_io.seek(0)
        # do gif work
        return base64.b64encode(img_io.getvalue())
    else:
        # # Call draw Method to add 2D graphics in an image
        I1 = ImageDraw.Draw(image)
        # # Add Text to an image
        I1.text(
            (text_x_pos, text_y_pos),
            text_on_image,
            font=font,
            fill=(255, 255, 255),
            stroke_fill=(0, 0, 0),
            stroke_width=3,
        )
        image.save(img_io, format="JPEG")
        img_io.seek(0)
        return base64.b64encode(img_io.getvalue())
