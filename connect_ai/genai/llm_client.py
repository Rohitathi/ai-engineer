import os


class LLMClient:
    """OpenAI-compatible LLM client with safe fallback when requests is unavailable."""

    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY", "").strip()
        self.base_url = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1").rstrip("/")
        self.model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

    def is_enabled(self):
        return bool(self.api_key)

    def chat(self, messages, temperature=0.2):
        if not self.is_enabled():
            return ""

        try:
            import requests
        except Exception:
            return ""

        url = f"{self.base_url}/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        payload = {"model": self.model, "messages": messages, "temperature": temperature}

        try:
            response = requests.post(url, headers=headers, json=payload, timeout=45)
            response.raise_for_status()
            data = response.json()
            return data["choices"][0]["message"]["content"].strip()
        except Exception:
            return ""
