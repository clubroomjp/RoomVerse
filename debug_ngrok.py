from app.core.tunnel import start_tunnel
from pyngrok import ngrok

def debug_ngrok():
    print("Testing ngrok connection via app logic...")
    
    url = start_tunnel(8001)
    
    if url:
        print(f"Success! URL: {url}")
        ngrok.disconnect(url)
    else:
        print("Failed to start tunnel.")

if __name__ == "__main__":
    debug_ngrok()
