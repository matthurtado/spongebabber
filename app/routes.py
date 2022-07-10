from datetime import datetime
from app import app, db, spongebobify, limiter, oauth
from app.models import LogRequest, User
from flask import jsonify, render_template, redirect, url_for, json, request, session
from config import env

USR_REQ_PER_DAY = 10
NUM_INITIAL_REQUESTS = 50
PAGE_DEFAULT = 10
GOOGLE_CONF_URL = "https://accounts.google.com/.well-known/openid-configuration"
FONT_URL = "https://github.com/matthurtado/spongebabber/blob/main/app/static/impact.ttf?raw=true"
MEME_VARS = {
    "text_to_sponge": "textToSponge",
    "image": "imageOverride",
    "text_x_pos": "textXPos",
    "text_y_pos": "textYPos",
    "target_width_ratio": "targetWidthRatio",
    "sponge_the_text": "spongeTheText",
}
MEME_DEFAULTS = {
    "text_to_sponge": None,
    "image": "https://i.imgur.com/XbXj7M4.jpg",
    "text_x_pos": 28,
    "text_y_pos": 280,
    "target_width_ratio": 0.6,
    "sponge_the_text": False,
}

# Database helpers
def get_or_create(session, model, **kwargs):
    instance = session.query(model).filter_by(**kwargs).first()
    if instance:
        return instance

    instance = model(**kwargs)
    session.add(instance)
    return instance


def get_user_rate_limit():
    return (
        f"{USR_REQ_PER_DAY}/day"
        if not session.get("id", None)
        else User.query.filter_by(id=session["id"]).first().requests_per_day
    )


def get_number_of_requests_today(user_id=None):
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


# Routes
@app.route("/")
def home():
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
@app.route("/spongebobify/<text_to_sponge>", methods=["GET", "POST"])
@limiter.limit(get_user_rate_limit)
def spongebobify_there(text_to_sponge=None):
    content_type = request.headers.get("Content-Type")
    if content_type != "application/json":
        return "Content-Type not supported!"

    # Initialize image settings
    my_meme = MEME_DEFAULTS.copy()

    # Load json data
    data = json.loads(request.data)
    for key in MEME_VARS:
        my_meme[key] = data.get(MEME_VARS[key], my_meme[key])

    # Create the image to return
    text_to_sponge = my_meme.get("text_to_sponge") or text_to_sponge
    encoded_image = spongebobify.create_meme(
        text_to_sponge,
        FONT_URL,
        my_meme.get("image"),
        my_meme.get("text_x_pos"),
        my_meme.get("text_y_pos"),
        float(my_meme.get("target_width_ratio")),
        my_meme.get("sponge_the_text"),
    )
    if my_meme.get("sponge_the_text"):
        text_to_sponge = spongebobify.spongebobify(text_to_sponge)
    log_request = LogRequest(
        text=text_to_sponge,
        text_x_pos=my_meme.get("text_x_pos"),
        text_y_pos=my_meme.get("text_y_pos"),
        target_width_ratio=float(my_meme.get("target_width_ratio")),
        sponge_the_text=my_meme.get("sponge_the_text"),
        ip_address=request.remote_addr,
        timestamp=datetime.now(),
        user_id=session.get("id") or None,
    )
    db.session.add(log_request)
    db.session.commit()
    return encoded_image.decode("utf-8")


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
    return oauth.google.authorize_redirect(redirect_uri)


@app.route("/google/auth/")
def google_auth():
    token = oauth.google.authorize_access_token()
    user = token.get("userinfo")
    if user:
        session["user"] = user

        user_db = get_or_create(db.session, User, email=user["email"])
        if user_db.last_login is None:
            user_db.email, user_db.name = user["email"], user["name"]
            user_db.num_of_requests = NUM_INITIAL_REQUESTS
        user_db.last_login = datetime.now()
        db.session.commit()

        session["is_admin"] = user_db.is_admin or False
        session["id"] = user_db.id
        session["requests_per_day"] = user_db.requests_per_day

    return redirect("/")


@app.route("/logout/")
def logout():
    session.pop("user", None)
    return redirect("/")


@app.route("/account/")
def account():
    if "user" not in session:
        return redirect("/")

    user = session["user"]
    session["remaining_requests_per_day"] = get_number_of_requests_today(session["id"])
    return render_template("account.html", user=user)
