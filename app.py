from flask import Flask, request, json, render_template
from flask_bootstrap import Bootstrap
from PIL import Image
import spongebobify
from urllib.request import urlopen

def create_app():
  app = Flask(__name__, static_folder='static', static_url_path='')
  Bootstrap(app)

  return app

app = create_app()

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
        data = json.loads(request.data)
        textToSponge = data['textToSponge']
        if(data['imageOverride']):
            imageOverride = data['imageOverride']
        if(data['textXPos']):
            textXPos = int(data['textXPos'])
        if(data['textYPos']):
            textYPos = int(data['textYPos'])
        encoded_image = spongebobify.create_image(textToSponge, "https://github.com/matthurtado/spongebabber/blob/main/static/impact.ttf?raw=true", imageOverride, textXPos, textYPos)
        return encoded_image.decode('utf-8')
    else:
        return 'Content-Type not supported!'

if __name__ == '__main__':
    # Threaded option to enable multiple instances for multiple user access support
    app.run(threaded=True, port=5000)