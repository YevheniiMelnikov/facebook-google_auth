import secrets

import google.auth.transport.requests
import requests
from flask import Flask, abort, redirect, render_template, request, session
from google.oauth2 import id_token
from google_auth_oauthlib.flow import Flow
from pip._vendor import cachecontrol

from config import (
    FACEBOOK_AUTH_BASE_URL,
    FACEBOOK_AUTH_SETTINGS,
    GOOGLE_AUTH_SETTINGS,
    client_secrets_file,
)

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)


google_flow = Flow.from_client_secrets_file(
    client_secrets_file=client_secrets_file,
    scopes=[
        "https://www.googleapis.com/auth/userinfo.profile",
        "https://www.googleapis.com/auth/userinfo.email",
        "openid",
    ],
    redirect_uri="http://127.0.0.1:5000/google_callback",
)


def login_is_required(function):
    def wrapper(*args, **kwargs):
        if "google_id" not in session and "facebook_id" not in session:
            return abort(401)
        return function(*args, **kwargs)

    return wrapper


@app.route("/google_login")
def google_login():
    authorization_url, state = google_flow.authorization_url()
    session["state"] = state
    return redirect(authorization_url)


@app.route("/google_callback")
def google_callback():
    google_flow.fetch_token(authorization_response=request.url)

    credentials = google_flow.credentials
    request_session = requests.session()
    cached_session = cachecontrol.CacheControl(request_session)
    token_request = google.auth.transport.requests.Request(session=cached_session)

    id_info = id_token.verify_oauth2_token(
        id_token=credentials._id_token,
        request=token_request,
        audience=GOOGLE_AUTH_SETTINGS.client_id,
    )

    session["google_id"] = id_info.get("sub")
    session["name"] = id_info.get("name")
    return redirect("/protected_area")


@app.route("/facebook_login")
def facebook_login():
    facebook_auth_url = f"{FACEBOOK_AUTH_BASE_URL}?client_id={FACEBOOK_AUTH_SETTINGS.app_id}&redirect_uri={FACEBOOK_AUTH_SETTINGS.redirect_uri}&state=random_string&scope={FACEBOOK_AUTH_SETTINGS.dialog_oauth_scope}"
    return redirect(facebook_auth_url)


@app.route("/facebook_callback")
def facebook_callback():
    code = request.args.get("code")
    redirect_uri = FACEBOOK_AUTH_SETTINGS.redirect_uri
    facebook_token_url = f"https://graph.facebook.com/oauth/access_token?client_secret={FACEBOOK_AUTH_SETTINGS.app_secret}&client_id={FACEBOOK_AUTH_SETTINGS.app_id}&code={code}&redirect_uri={redirect_uri}"
    response = requests.get(facebook_token_url)
    data = response.json()
    access_token = data["access_token"]

    facebook_user_url = f"https://graph.facebook.com/v10.0/me?fields=id,name,email&access_token={access_token}"
    response = requests.get(facebook_user_url)
    facebook_user_data = response.json()

    session["facebook_id"] = facebook_user_data["id"]
    session["name"] = facebook_user_data["name"]
    return redirect("/protected_area")


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/protected_area")
@login_is_required
def protected_area():
    return render_template("protected.html")


if __name__ == "__main__":
    app.run(debug=True)
