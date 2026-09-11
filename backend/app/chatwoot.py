from typing import Any
from urllib.parse import quote
import requests
from fastapi import HTTPException

from app.core.config import settings


class ChatwootClient:
    def __init__(self) -> None:
        base = settings.CHATWOOT_BASE_URL.rstrip("/")
        self.account_url = f"{base}/api/v1/accounts/{settings.CHATWOOT_ACCOUNT_ID}"
        self.headers = {
            "api_access_token": settings.CHATWOOT_API_TOKEN,
            "Accept": "application/json",
        }

    def request(self, method: str, path: str, **kwargs: Any) -> Any:
        try:
            response = requests.request(
                method,
                f"{self.account_url}{path}",
                headers={**self.headers, **kwargs.pop("headers", {})},
                timeout=settings.REQUEST_TIMEOUT_SECONDS,
                **kwargs,
            )
        except requests.RequestException as exc:
            raise HTTPException(status_code=503, detail="Chatwoot indisponível") from exc

        if response.status_code >= 400:
            detail = "Falha na comunicação com o Chatwoot"
            try:
                body = response.json()
                detail = body.get("message") or body.get("error") or body.get("detail") or detail
            except ValueError:
                pass
            raise HTTPException(status_code=response.status_code, detail=detail)
        return response.json() if response.content else {}

    def inboxes(self) -> Any:
        departments = {
            settings.CHATWOOT_INBOX_LEADS_ID: ("leads", "Leads de campanhas"),
            settings.CHATWOOT_INBOX_CAMPANHAS_INTERNAS_ID: ("campanhas_internas", "Campanhas internas"),
            settings.CHATWOOT_INBOX_SUPORTE_ID: ("suporte", "Suporte"),
            settings.CHATWOOT_INBOX_TRANSACIONAL_ID: ("transacional", "Ativação e recuperação"),
        }
        data = self.request("GET", "/inboxes")
        payload = data.get("payload", data) if isinstance(data, dict) else data
        result = []
        for item in payload:
            if item.get("id") not in departments:
                continue
            key, display_name = departments[item["id"]]
            result.append({**item, "department": key, "display_name": display_name})
        return result

    def conversations(self, status: str, inbox_id: int | None, page: int) -> Any:
        params: dict[str, Any] = {"status": status, "page": page}
        if inbox_id:
            params["inbox_id"] = inbox_id
        return self.request("GET", "/conversations", params=params)

    def conversation(self, conversation_id: int) -> Any:
        return self.request("GET", f"/conversations/{conversation_id}")

    def messages(self, conversation_id: int) -> Any:
        return self.request("GET", f"/conversations/{conversation_id}/messages")

    def send_message(self, conversation_id: int, content: str, private: bool = False) -> Any:
        return self.request(
            "POST",
            f"/conversations/{conversation_id}/messages",
            json={"content": content, "message_type": "outgoing", "private": private},
        )

    def send_attachment(self, conversation_id: int, filename: str, content: bytes, content_type: str, caption: str = "") -> Any:
        data = {"message_type": "outgoing", "private": "false"}
        if caption.strip():
            data["content"] = caption.strip()
        return self.request(
            "POST",
            f"/conversations/{conversation_id}/messages",
            data=data,
            files={"attachments[]": (filename, content, content_type)},
        )

    def update_status(self, conversation_id: int, status: str) -> Any:
        return self.request(
            "POST",
            f"/conversations/{conversation_id}/toggle_status",
            json={"status": status},
        )

    def assign(self, conversation_id: int, assignee_id: int | None) -> Any:
        return self.request(
            "POST",
            f"/conversations/{conversation_id}/assignments",
            json={"assignee_id": assignee_id},
        )

    def agents(self) -> Any:
        return self.request("GET", "/agents")

    def labels(self) -> Any:
        return self.request("GET", "/labels")

    def conversation_labels(self, conversation_id: int) -> Any:
        return self.request("GET", f"/conversations/{conversation_id}/labels")

    def update_conversation_labels(self, conversation_id: int, labels: list[str]) -> Any:
        return self.request(
            "POST",
            f"/conversations/{conversation_id}/labels",
            json={"labels": labels},
        )

    def create_label(self, title: str, color: str, description: str = "") -> Any:
        return self.request(
            "POST",
            "/labels",
            json={"title": title, "color": color, "description": description, "show_on_sidebar": True},
        )

    def update_label(self, label_id: int, title: str, color: str, description: str = "") -> Any:
        return self.request(
            "PATCH",
            f"/labels/{label_id}",
            json={"title": title, "color": color, "description": description, "show_on_sidebar": True},
        )

    def delete_label(self, label_id: int) -> Any:
        return self.request("DELETE", f"/labels/{label_id}")

    def search_contacts(self, query: str) -> Any:
        return self.request("GET", "/contacts/search", params={"q": query})

    def create_contact(self, name: str, phone: str, inbox_id: int) -> Any:
        identifier = f"{phone.lstrip('+')}@s.whatsapp.net"
        return self.request(
            "POST",
            "/contacts",
            json={
                "name": name,
                "phone_number": phone,
                "identifier": identifier,
                "inbox_id": inbox_id,
            },
        )

    def create_conversation(self, contact_id: int, source_id: str, inbox_id: int) -> Any:
        return self.request(
            "POST",
            "/conversations",
            json={
                "contact_id": contact_id,
                "source_id": source_id,
                "inbox_id": inbox_id,
                "status": "open",
            },
        )


chatwoot = ChatwootClient()
