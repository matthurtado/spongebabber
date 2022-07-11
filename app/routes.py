from datetime import datetime

import requests
from app import app, db, spongebobify, limiter, oauth
from app.models import LogRequest, User
from flask import jsonify, render_template, redirect, url_for, json, request, session
from config import Config

# Database helpers
def get_or_create(session, model, **kwargs):
    instance = session.query(model).filter_by(**kwargs).first()
    if instance:
        return instance
    else:
        instance = model(**kwargs)
        session.add(instance)
        return instance


def get_user_rate_limit():
    if session["id"] is None:
        return "10/day"
    else:
        return User.query.filter_by(id=session["id"]).first().requests_per_day


def get_number_of_requests_today(user_id=None):
    if user_id is None:
        return 10
    else:
        todays_datetime = datetime(
            datetime.today().year, datetime.today().month, datetime.today().day
        )
        number_of_requests = User.query.filter_by(id=user_id).first().requests_per_day
        number_of_requests_today = (
            LogRequest.query.filter(LogRequest.timestamp >= todays_datetime)
            .filter_by(user_id=user_id)
            .count()
        )
        return number_of_requests - number_of_requests_today


def set_session_vars():
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


def upload_data_to_imgur(image_data):
    url = "https://api.imgur.com/3/image"
    payload = {"image": image_data}
    headers = {"Authorization": "Client-ID " + Config.IMGUR_CLIENT_ID}
    response = requests.request("POST", url, headers=headers, data=payload)
    return response.json()["data"]["link"]

def get_user_sponges(user_id):
    return LogRequest.query.filter_by(user_id=user_id).filter(LogRequest.imgur_link != None).all()

# Routes
@app.route("/")
def home():
    if session["id"] is None:
        session["is_admin"] = "false"
    print(session)
    return render_template("home.html")


@app.route("/recent")
def recent():
    sponges = LogRequest.query.order_by(LogRequest.timestamp.desc())
    return render_template("recent.html", title="Recent Sponges", sponges=sponges)


@app.route("/api/recent")
@app.route("/api/recent/<int:page>")
def api_recent(page=None):
    if page is None:
        page = 10
    sponges = LogRequest.query.order_by(LogRequest.timestamp.desc()).limit(page)
    return jsonify(sponges=LogRequest.serialize_list(sponges))


@app.route("/spongebobify/", methods=["POST"])
@app.route("/spongebobify/<textToSponge>", methods=["GET", "POST"])
@limiter.limit(get_user_rate_limit)
def spongebobify_there(textToSponge=None):
    content_type = request.headers.get("Content-Type")
    if content_type == "application/json":
        # Initialize image settings
        imageOverride = "https://i.imgur.com/XbXj7M4.jpg"
        textXPos = 28
        textYPos = 280
        targetWidthRatio = 0.6
        spongeTheText = True
        imgur_upload_link = None

        # Load json data
        data = json.loads(request.data)
        textToSponge = data["textToSponge"]

        if data["imageOverride"]:
            imageOverride = data["imageOverride"]
        if data["textXPos"]:
            textXPos = int(data["textXPos"])
        if data["textYPos"]:
            textYPos = int(data["textYPos"])
        if data["targetWidthRatio"]:
            targetWidthRatio = float(data["targetWidthRatio"])
        if data["spongeTheText"]:
            spongeTheText = True
        else:
            spongeTheText = False
        if data["upload_to_imgur"]:
            upload_image_to_imgur = True
        else:
            upload_image_to_imgur = False
        # Create the image to return
        encoded_image = spongebobify.create_image(
            textToSponge,
            "https://github.com/matthurtado/spongebabber/blob/main/app/static/impact.ttf?raw=true",
            imageOverride,
            textXPos,
            textYPos,
            targetWidthRatio,
            spongeTheText,
        )
        if spongeTheText:
            textToSponge = spongebobify.spongebobify(textToSponge)
        if upload_image_to_imgur:
            imgur_upload_link = upload_data_to_imgur(encoded_image.decode("utf-8"))
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
        db.session.add(log_request)
        db.session.commit()
        if imgur_upload_link is not None:
            ret_data = {
                "imgur_link": imgur_upload_link,
                "text": textToSponge,
            }
        else:
            ret_data = {
                "text": textToSponge,
                "encoded_image": encoded_image.decode("utf-8"),
            }
        return jsonify(ret_data)
    else:
        return "Content-Type not supported!"


@app.route("/google/")
def google():
    GOOGLE_CLIENT_ID = Config.GOOGLE_CLIENT_ID
    GOOGLE_CLIENT_SECRET = Config.GOOGLE_CLIENT_SECRET

    CONF_URL = "https://accounts.google.com/.well-known/openid-configuration"
    oauth.register(
        name="google",
        client_id=GOOGLE_CLIENT_ID,
        client_secret=GOOGLE_CLIENT_SECRET,
        server_metadata_url=CONF_URL,
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

        user_db = get_or_create(db.session, User, email=user["email"])
        if user_db.last_login is None:
            user_db.email = user["email"]
            user_db.name = user["name"]
            user_db.last_login = datetime.now()
            user_db.num_of_requests = 50
            db.session.commit()
        else:
            user_db.last_login = datetime.now()
            db.session.commit()
        session["id"] = user_db.id
        set_session_vars()
    return redirect("/")


@app.route("/logout/")
def logout():
    session.pop("user", None)
    session["id"] = None
    session["is_admin"] = False
    return redirect("/")


@app.route("/account/")
def account():
    if "user" in session:
        user = session["user"]
        session["remaining_requests_per_day"] = get_number_of_requests_today(
            session["id"]
        )
        user_sponges = get_user_sponges(session["id"])
        return_value = {
            "user": user,
            "user_sponges": user_sponges
        }
        return render_template("account.html", account=return_value)
    else:
        return redirect("/")
