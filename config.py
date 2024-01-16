import os
import pathlib

from dotenv import load_dotenv

from models import FacebookAuthSettings, GoogleAuthSettings

load_dotenv("env.local")

os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"
FACEBOOK_AUTH_BASE_URL = "https://www.facebook.com/v18.0/dialog/oauth"
FACEBOOK_TOKEN_BASE_URL = "https://graph.facebook.com/oauth/access_token"
NGROK_ADDRESS = os.getenv("NGROK_ADDRESS")
client_secrets_file = os.path.join(
    pathlib.Path(__file__).parent, "google_client_secret.json"
)


GOOGLE_AUTH_SETTINGS = GoogleAuthSettings(
    client_id=os.getenv("GOOGLE_CLIENT_ID"),
    client_secret=os.getenv("GOOGLE_CLIENT_SECRET"),
    redirect_uri="http://127.0.0.1:5000/google_callback",
    scopes=[
        "https://www.googleapis.com/auth/userinfo.profile",
        "https://www.googleapis.com/auth/userinfo.email",
        "openid",
    ],
)

FACEBOOK_AUTH_SETTINGS = FacebookAuthSettings(
    app_id=os.getenv("FACEBOOK_APP_ID"),
    app_secret=os.getenv("FACEBOOK_APP_SECRET"),
    redirect_uri=f"{NGROK_ADDRESS}/facebook_callback",
    dialog_oauth_scope="email",
    graph_api_scope="id,name,email",
)
