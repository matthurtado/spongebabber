from datetime import datetime
from distutils.command.upload import upload

import requests
from app import app, db, spongebobify, limiter, oauth
from app.models import LogRequest, User
from flask import jsonify, render_template, redirect, url_for, json, request, session
from config import env

USR_REQ_PER_DAY = 10
NUM_INITIAL_REQUESTS = 50
PAGE_DEFAULT = 10
IMGUR_API_URL = "https://api.imgur.com/3/image"
GOOGLE_CONF_URL = "https://accounts.google.com/.well-known/openid-configuration"
FONT_URL = "https://github.com/matthurtado/spongebabber/blob/main/app/static/impact.ttf?raw=true"
MEME_DEFAULTS = {
    "text_to_sponge": None,
    "image": "https://i.imgur.com/XbXj7M4.jpg",
    "text_x_pos": 28,
    "text_y_pos": 280,
    "target_width_ratio": 0.6,
    "imgur_upload_link": None,
}

# Database helpers
def _get_or_create(session, model, **kwargs):
    instance = session.query(model).filter_by(**kwargs).first()
    if instance:
        return instance

    instance = model(**kwargs)
    session.add(instance)
    return instance


def _get_user_rate_limit():
    return (
        f"{USR_REQ_PER_DAY}/day"
        if not session.get("id", None)
        else User.query.filter_by(id=session["id"]).first().requests_per_day
    )


def _get_number_of_requests_today(user_id=None):
    if user_id is None:
        return USR_REQ_PER_DAY

    today = datetime.today()
    todays_datetime = datetime(today.year, today.month, today.day)
    number_of_requests = User.query.filter_by(id=user_id).first().requests_per_day
    number_of_requests_today = (
        LogRequest.query.filter(LogRequest.timestamp >= todays_datetime)
        .filter_by(user_id=user_id)
        .count()
    )
    return number_of_requests - number_of_requests_today


def _set_session_vars():
    if session["id"] is None:
        session["id"] = None
        session["name"] = None
        session["email"] = None
        session["is_admin"] = "false"
        session["last_login"] = None
        session["requests_per_day"] = None
    else:
        user = User.query.filter_by(id=session["id"]).first()
        session["name"] = user.name
        session["email"] = user.email
        session["is_admin"] = str(user.is_admin).lower()
        session["last_login"] = user.last_login
        session["requests_per_day"] = user.requests_per_day


def _upload_data_to_imgur(image_data):
    url = IMGUR_API_URL
    payload = {"image": image_data}
    headers = {"Authorization": "Client-ID " + env.IMGUR_CLIENT_ID}
    response = requests.request("POST", url, headers=headers, data=payload)
    return response.json()["data"]["link"]


def _get_user_sponges(user_id):
    return (
        LogRequest.query.filter_by(user_id=user_id)
        .filter(LogRequest.imgur_link != None)
        .all()
    )


# Routes
@app.route("/")
def home():
    if session.get("id", None) is None:
        session["is_admin"] = "false"
    print(session)
    return render_template("home.html")


@app.route("/recent")
def recent():
    sponges = LogRequest.query.order_by(LogRequest.timestamp.desc())
    return render_template("recent.html", title="Recent Sponges", sponges=sponges)


@app.route("/api/recent")
@app.route("/api/recent/<int:page>")
def api_recent(page=PAGE_DEFAULT):
    sponges = LogRequest.query.order_by(LogRequest.timestamp.desc()).limit(page)
    return jsonify(sponges=LogRequest.serialize_list(sponges))


@app.route("/spongebobify/", methods=["POST"])
@app.route("/spongebobify/<textToSponge>", methods=["GET", "POST"])
@limiter.limit(_get_user_rate_limit)
def spongebobify_there(textToSponge=None):
    content_type = request.headers.get("Content-Type")
    if content_type != "application/json":
        return "Content-Type not supported!"

    # Load json data
    data = json.loads(request.data)
    textToSponge = data["textToSponge"]

    imageOverride = data["imageOverride"] if data["imageOverride"] else MEME_DEFAULTS["image"]
    textXPos = data["textXPos"] if data["textXPos"] else MEME_DEFAULTS["text_x_pos"]
    textYPos = data["textYPos"] if data["textYPos"] else MEME_DEFAULTS["text_y_pos"]
    targetWidthRatio = float(data["targetWidthRatio"]) if data["targetWidthRatio"] else MEME_DEFAULTS["target_width_ratio"]
    spongeTheText = True if data["spongeTheText"] else False
    upload_image_to_imgur = True if data["upload_to_imgur"] else False
    imgur_upload_link = MEME_DEFAULTS["imgur_upload_link"]

    # Create the image to return
    encoded_image = spongebobify.create_meme(
        textToSponge,
        FONT_URL,
        imageOverride,
        textXPos,
        textYPos,
        targetWidthRatio,
        spongeTheText,
    )
    if spongeTheText:
        textToSponge = spongebobify.spongebobify(textToSponge)
    if upload_image_to_imgur:
        try:
            imgur_upload_link = _upload_data_to_imgur(encoded_image.decode("utf-8"))
        except:
            print("COULDN'T UPLOAD TO IMGUR")
    log_request = LogRequest(
        text=textToSponge,
        text_x_pos=textXPos,
        text_y_pos=textYPos,
        target_width_ratio=targetWidthRatio,
        sponge_the_text=spongeTheText,
        ip_address=request.remote_addr,
        timestamp=datetime.now(),
        imgur_link=imgur_upload_link or None,
        user_id=session.get("id") or None,
    )
    try:
        db.session.add(log_request)
        db.session.commit()
    except:
        print("COULDN'T SAVE TO DATABASE")

    ret_data = {"text": textToSponge}
    if imgur_upload_link is not None:
        ret_data["imgur_link"] = imgur_upload_link
    else:
        ret_data["encoded_image"] = encoded_image.decode("utf-8")
    return jsonify(ret_data)


@app.route("/google/")
def google():
    oauth.register(
        name="google",
        client_id=env.GOOGLE_CLIENT_ID,
        client_secret=env.GOOGLE_CLIENT_SECRET,
        server_metadata_url=GOOGLE_CONF_URL,
        client_kwargs={"scope": "openid email profile"},
    )

    # Redirect to google_auth function
    redirect_uri = url_for("google_auth", _external=True)
    print(redirect_uri)
    return oauth.google.authorize_redirect(redirect_uri)


@app.route("/google/auth/")
def google_auth():
    token = oauth.google.authorize_access_token()
    print(token)
    user = token.get("userinfo")
    if user:
        session["user"] = user

        user_db = _get_or_create(db.session, User, email=user["email"])
        if user_db.last_login is None:
            user_db.email = user["email"]
            user_db.name = user["name"]
            user_db.num_of_requests = NUM_INITIAL_REQUESTS

        user_db.last_login = datetime.now()
        db.session.commit()

        session["id"] = user_db.id
        _set_session_vars()

    return redirect("/")


@app.route("/logout/")
def logout():
    session.pop("user", None)
    session["id"] = None
    session["is_admin"] = False
    return redirect("/")


@app.route("/account/")
def account():
    if "user" not in session:
        return redirect("/")

    user = session["user"]
    session["remaining_requests_per_day"] = _get_number_of_requests_today(session["id"])
    user_sponges = _get_user_sponges(session["id"])
    return_value = {"user": user, "user_sponges": user_sponges}
    return render_template("account.html", account=return_value)
