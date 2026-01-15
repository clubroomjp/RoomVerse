import subprocess
import os
import sys
import requests
import re
import time
import shutil
import threading
from pathlib import Path

# URL for Cloudflared Windows binary
CLOUDFLARED_URL = "https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-windows-amd64.exe"
CLOUDFLARED_BIN = "cloudflared.exe"

class CloudflaredTunnel:
    def __init__(self, bin_path: str = None):
        self.bin_path = bin_path or self._get_default_bin_path()
        self.process = None
        self.public_url = None
        self._stop_event = threading.Event()

    def _get_default_bin_path(self) -> str:
        # Check if running as PyInstaller OneFile
        if getattr(sys, 'frozen', False):
            # If bundled, it might be in sys._MEIPASS
            bundled_path = os.path.join(sys._MEIPASS, CLOUDFLARED_BIN)
            if os.path.exists(bundled_path):
                return bundled_path
            
        # Development environment or next to exe
        return os.path.join(os.getcwd(), CLOUDFLARED_BIN)

    def ensure_cloudflared(self):
        """Checks if cloudflared exists, downloads if not."""
        if os.path.exists(self.bin_path):
            return

        print(f"cloudflared not found at {self.bin_path}. Downloading...")
        try:
            response = requests.get(CLOUDFLARED_URL, stream=True)
            response.raise_for_status()
            with open(self.bin_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            print("Download complete.")
        except Exception as e:
            print(f"Failed to download cloudflared: {e}")
            raise

    def start(self, port: int) -> str:
        """Starts the cloudflared tunnel and returns the URL."""
        self.ensure_cloudflared()
        
        cmd = [self.bin_path, "tunnel", "--url", f"http://localhost:{port}"]
        
        # Windows: CREATE_NO_WINDOW to hide console
        startupinfo = None
        if os.name == 'nt':
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        
        self.process = subprocess.Popen(
            cmd, 
            stdout=subprocess.PIPE, 
            stderr=subprocess.STDOUT, 
            text=True, 
            encoding='utf-8',
            errors='replace',
            startupinfo=startupinfo,
            bufsize=1
        )

        # Parse output for URL in a separate thread to not block but we need to wait for URL first
        self.public_url = self._wait_for_url()
        
        # Start a thread to keep reading logs (prevent buffer fill)
        threading.Thread(target=self._read_logs, daemon=True).start()
        
        return self.public_url

    def _wait_for_url(self, timeout=30) -> str:
        """Reads process output until the TryCloudflare URL is found."""
        start_time = time.time()
        url_pattern = re.compile(r"https://[a-zA-Z0-9-]+\.trycloudflare\.com")
        
        while time.time() - start_time < timeout:
            line = self.process.stdout.readline()
            if not line:
                break
            
            # Print log for debugging
            # print(f"[cloudflared] {line.strip()}")
            
            match = url_pattern.search(line)
            if match:
                return match.group(0)
                
            if self.process.poll() is not None:
                raise RuntimeError("cloudflared process exited unexpectedly.")
                
        raise TimeoutError("Timed out waiting for Cloudflare Tunnel URL")

    def _read_logs(self):
        """Continuously reads logs to keep buffer clear."""
        while self.process and self.process.poll() is None:
            line = self.process.stdout.readline()
            if not line:
                break
            # potentially log to file if needed

    def stop(self):
        """Stops the cloudflared process."""
        if self.process:
            self.process.terminate()
            try:
                self.process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.process.kill()
            self.process = None

