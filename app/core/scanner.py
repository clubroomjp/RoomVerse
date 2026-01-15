import aiohttp
import asyncio

class LocalLLMScanner:
    def __init__(self):
        self.timeout = 2  # seconds
    
    async def scan_all(self):
        results = []
        # Define tasks
        tasks = [
            self.check_ollama(),
            self.check_lm_studio(),
            self.check_llamacpp(),
            self.check_koboldcpp(),
            self.check_oobabooga()
        ]
        
        # Run all checks in parallel
        scan_results = await asyncio.gather(*tasks, return_exceptions=True)
        
        for res in scan_results:
            if isinstance(res, list):
                results.extend(res)
            elif isinstance(res, Exception):
                # print(f"Scan error: {res}")
                pass
                
        return results

    async def _fetch(self, url):
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=self.timeout) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    return None

    # --- Providers ---

    async def check_ollama(self):
        # Ollama: Port 11434
        # API: /api/tags
        url = "http://127.0.0.1:11434/api/tags"
        found = []
        try:
            data = await self._fetch(url)
            if data and "models" in data:
                base_url = "http://127.0.0.1:11434/v1"
                for m in data["models"]:
                    name = m.get("name")
                    found.append({
                        "label": f"Ollama: {name}",
                        "model_id": name,
                        "base_url": base_url
                    })
        except:
            pass
        return found

    async def check_lm_studio(self):
        # LM Studio: Port 1234
        # API: /v1/models
        base_url = "http://127.0.0.1:1234/v1"
        url = f"{base_url}/models"
        found = []
        try:
            data = await self._fetch(url)
            if data and "data" in data:
                for m in data["data"]:
                    name = m.get("id")
                    found.append({
                        "label": f"LM Studio: {name}",
                        "model_id": name,
                        "base_url": base_url
                    })
        except:
            pass
        return found

    async def check_llamacpp(self):
        # Llama.cpp Server: Port 8080
        # API: /v1/models (Recent versions support this)
        base_url = "http://127.0.0.1:8080/v1"
        url = f"{base_url}/models"
        found = []
        try:
            data = await self._fetch(url)
            if data and "data" in data:
                # Llama.cpp often returns just one model but in a list
                for m in data["data"]:
                    name = m.get("id", "default")
                    found.append({
                        "label": f"Llama.cpp: {name}",
                        "model_id": name,
                        "base_url": base_url
                    })
        except:
            pass
        return found
        
    async def check_koboldcpp(self):
        # KoboldCPP: Port 5001
        # API: /v1/models or /api/v1/model
        # Kobold's OpenAI compatible endpoint is usually at /v1
        base_url = "http://127.0.0.1:5001/v1"
        url = f"{base_url}/models"
        found = []
        try:
            data = await self._fetch(url)
            if data and "data" in data:
                for m in data["data"]:
                    name = m.get("id")
                    found.append({
                        "label": f"KoboldCPP: {name}",
                        "model_id": name,
                        "base_url": base_url
                    })
        except:
            pass
        return found
    
    async def check_oobabooga(self):
        # Oobabooga: Port 5000 (standard for API)
        # Needs --api flag. OpenAI extension is usually at /v1
        base_url = "http://127.0.0.1:5000/v1"
        url = f"{base_url}/models"
        found = []
        try:
            data = await self._fetch(url)
            if data and "data" in data:
                for m in data["data"]:
                    name = m.get("id")
                    found.append({
                        "label": f"Oobabooga: {name}",
                        "model_id": name,
                        "base_url": base_url
                    })
        except:
            pass
        return found

scanner = LocalLLMScanner()
