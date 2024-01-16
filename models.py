from dataclasses import dataclass


@dataclass
class GoogleAuthSettings:
    client_id: str
    client_secret: str
    redirect_uri: str
    scopes: list


@dataclass
class FacebookAuthSettings:
    app_id: str
    app_secret: str
    redirect_uri: str
    dialog_oauth_scope: str
    graph_api_scope: str
