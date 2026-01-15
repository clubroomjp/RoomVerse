from pyngrok import ngrok
import sys
import threading
from app.core.config import config
from app.core.cloudflared import CloudflaredTunnel
from app.core.discovery import get_discovery_client

# Global tunnel instance to keep it alive
_tunnel_instance = None

def start_tunnel(port: int) -> str:
    """
    Starts a tunnel (Cloudflare or ngrok) to the specified port.
    Returns the public URL.
    """
    global _tunnel_instance
    
    public_url = None

    # 1. Try Cloudflare Tunnel if enabled (Default)
    if config.cloudflare and config.cloudflare.enabled:
        try:
            print("[Tunnel] Starting Cloudflare Tunnel...")
            _tunnel_instance = CloudflaredTunnel(bin_path=config.cloudflare.binary_path)
            public_url = _tunnel_instance.start(port)
            print(f"[Tunnel] Cloudflare Tunnel established: {public_url}")
        except Exception as e:
            print(f"[Tunnel] Failed to start Cloudflare Tunnel: {e}")
            _tunnel_instance = None

    # 2. Fallback to ngrok if Cloudflare failed or disabled
    if not public_url and config.ngrok and config.ngrok.authtoken:
        try:
            print("[Tunnel] Starting ngrok Tunnel...")
            ngrok.set_auth_token(config.ngrok.authtoken)
            
            auth = None
            if config.security and config.security.ngrok_basic_auth:
                auth = config.security.ngrok_basic_auth
                
            public_url = ngrok.connect(port, auth=auth).public_url
            print(f"[Tunnel] ngrok Tunnel established: {public_url}")
        except Exception as e:
            print(f"[Tunnel] Failed to start ngrok tunnel: {e}")

    # 3. Announce to Discovery Service
    if public_url:
        _announce_async(public_url)
        
    return public_url

def _announce_async(url: str):
    """Announces the URL to the discovery service in a background thread."""
    def _run():
        client = get_discovery_client(config)
        metadata = {
            "name": config.room.name,
            "character": config.character.name,
            "max_visitors": config.room.max_visitors
        }
        # Use instance_id as the stable UUID
        client.announce(config.instance_id, url, metadata)
    
    threading.Thread(target=_run, daemon=True).start()

def stop_tunnel():
    """Stops the active tunnel."""
    global _tunnel_instance
    if isinstance(_tunnel_instance, CloudflaredTunnel):
        _tunnel_instance.stop()
    else:
        ngrok.kill()
