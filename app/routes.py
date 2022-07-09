from app import app,db, spongebobify
from app.models import LogRequest
from flask import render_template,flash, redirect, url_for, json, request


@app.route("/")
def home():
    return render_template("home.html")

@app.route("/spongebobify/", methods=["POST"])
@app.route("/spongebobify/<textToSponge>", methods = ["GET", "POST"])
def spongebobify_there(textToSponge = None):
    content_type = request.headers.get('Content-Type')
    if (content_type == 'application/json'):
        imageOverride = "https://i.imgur.com/XbXj7M4.jpg"
        textXPos = 28
        textYPos = 280
        targetWidthRatio = 0.6
        spongeTheText = True
        data = json.loads(request.data)
        textToSponge = data['textToSponge']
        if(data['imageOverride']):
            imageOverride = data['imageOverride']
        if(data['textXPos']):
            textXPos = int(data['textXPos'])
        if(data['textYPos']):
            textYPos = int(data['textYPos'])
        if(data['targetWidthRatio']):
            targetWidthRatio = float(data['targetWidthRatio'])
        if(data["spongeTheText"]):
            spongeTheText = True
        else:
            spongeTheText = False
        encoded_image = spongebobify.create_image(textToSponge, "https://github.com/matthurtado/spongebabber/blob/main/app/static/impact.ttf?raw=true", imageOverride, textXPos, textYPos, targetWidthRatio, spongeTheText)
        log_request = LogRequest(text=textToSponge, text_x_pos=textXPos, text_y_pos=textYPos, target_width_ratio=targetWidthRatio, sponge_the_text=spongeTheText, ip_address=request.remote_addr)
        db.session.add(log_request)
        db.session.commit()
        return encoded_image.decode('utf-8')
    else:
        return 'Content-Type not supported!'