from pyngrok import ngrok
import sys
from app.core.config import config

def start_tunnel(port: int) -> str:
    """
    Starts an ngrok tunnel to the specified port and returns the public URL.
    """
    if config.ngrok and config.ngrok.authtoken:
        ngrok.set_auth_token(config.ngrok.authtoken)

    # Basic Auth from config
    auth = None
    if config.security and config.security.ngrok_basic_auth:
        auth = config.security.ngrok_basic_auth

    try:
        # Start ngrok tunnel
        public_url = ngrok.connect(port, auth=auth).public_url
        print(f" * Public URL: {public_url}")
        return public_url
    except Exception as e:
        print(f"Error starting ngrok tunnel: {e}")
        return None
