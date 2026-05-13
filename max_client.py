from pathlib import Path
from max_api_client_python.API import GreenAPI


class MaxSender:
    def __init__(self, instance_id: str, api_token: str, api_url: str, media_url: str):
        self.api = GreenAPI(instance_id, api_token, host=api_url, media=media_url)
        self.api.raise_errors = True
        self._chat_id: str | None = None

    def check_state(self) -> dict:
        resp = self.api.account.getStateInstance()
        if hasattr(resp, "data"):
            return resp.data
        return {"error": str(resp)}

    def resolve_chat_id(self, phone: str) -> str:
        resp = self.api.serviceMethods.checkAccount(int(phone))
        if hasattr(resp, "data") and isinstance(resp.data, dict):
            if resp.data.get("exist") is True:
                self._chat_id = resp.data["chatId"]
                return self._chat_id
        self._chat_id = f"{phone}@c.us"
        return self._chat_id

    def send_file(self, file_path: str, caption: str = "") -> dict:
        p = Path(file_path)
        if not p.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        if not self._chat_id:
            raise RuntimeError("chat_id not resolved. Call resolve_chat_id() first")

        resp = self.api.sending.sendFileByUpload(self._chat_id, file_path, p.name, caption)

        if hasattr(resp, "data"):
            return resp.data
        elif hasattr(resp, "code") and hasattr(resp, "error"):
            raise RuntimeError(f"GREEN-API error (code={resp.code}): {resp.error}")
        else:
            raise RuntimeError(f"GREEN-API unexpected response: {resp}")
