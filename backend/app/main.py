from fastapi import Depends, FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
import requests

from app.auth import get_current_user
from app.chatwoot import chatwoot
from app.core.config import settings
from app.schemas import AssignmentInput, LabelInput, LabelsInput, LoginInput, MessageInput, NewConversationInput, StatusInput


app = FastAPI(title="Central Nhora", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[item.strip() for item in settings.CORS_ORIGINS.split(",") if item.strip()],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health():
    return {"status": "ok", "service": "central-nhora"}


@app.post("/auth/login")
def login(data: LoginInput):
    try:
        response = requests.post(
            f"{settings.NHORA_API_URL.rstrip('/')}/auth/login",
            json={"email": data.email, "password": data.password},
            timeout=settings.REQUEST_TIMEOUT_SECONDS,
        )
    except requests.RequestException as exc:
        raise HTTPException(status_code=503, detail="Plataforma Nhora indisponível") from exc
    if response.status_code != 200:
        raise HTTPException(status_code=401, detail="E-mail ou senha inválidos")
    payload = response.json()
    if not payload.get("user", {}).get("is_platform_admin"):
        raise HTTPException(status_code=403, detail="Acesso exclusivo da equipe Nhora")
    return payload


@app.get("/auth/me")
def me(user: dict = Depends(get_current_user)):
    return user


@app.get("/inboxes")
def inboxes(_: dict = Depends(get_current_user)):
    return chatwoot.inboxes()


@app.get("/agents")
def agents(_: dict = Depends(get_current_user)):
    return chatwoot.agents()


@app.get("/labels")
def labels(_: dict = Depends(get_current_user)):
    return chatwoot.labels()


@app.post("/labels")
def create_label(data: LabelInput, _: dict = Depends(get_current_user)):
    return chatwoot.create_label(data.title.strip(), data.color, data.description.strip())


@app.patch("/labels/{label_id}")
def update_label(label_id: int, data: LabelInput, _: dict = Depends(get_current_user)):
    return chatwoot.update_label(label_id, data.title.strip(), data.color, data.description.strip())


@app.delete("/labels/{label_id}")
def delete_label(label_id: int, _: dict = Depends(get_current_user)):
    return chatwoot.delete_label(label_id)


@app.get("/conversations")
def conversations(status: str = "open", inbox_id: int | None = None, page: int = 1, _: dict = Depends(get_current_user)):
    return chatwoot.conversations(status, inbox_id, page)


@app.get("/conversations/{conversation_id}")
def conversation(conversation_id: int, _: dict = Depends(get_current_user)):
    return chatwoot.conversation(conversation_id)


@app.get("/conversations/{conversation_id}/messages")
def messages(conversation_id: int, _: dict = Depends(get_current_user)):
    return chatwoot.messages(conversation_id)


@app.get("/conversations/{conversation_id}/labels")
def conversation_labels(conversation_id: int, _: dict = Depends(get_current_user)):
    return chatwoot.conversation_labels(conversation_id)


@app.post("/conversations/{conversation_id}/labels")
def update_conversation_labels(conversation_id: int, data: LabelsInput, _: dict = Depends(get_current_user)):
    return chatwoot.update_conversation_labels(conversation_id, data.labels)


@app.post("/conversations/{conversation_id}/messages")
def send_message(conversation_id: int, data: MessageInput, _: dict = Depends(get_current_user)):
    return chatwoot.send_message(conversation_id, data.content, data.private)


@app.post("/conversations/{conversation_id}/attachments")
async def send_attachment(conversation_id: int, attachment: UploadFile = File(...), caption: str = Form(""), _: dict = Depends(get_current_user)):
    content = await attachment.read()
    if len(content) > 25 * 1024 * 1024:
        raise HTTPException(status_code=413, detail="Arquivo maior que 25 MB")
    return chatwoot.send_attachment(
        conversation_id,
        attachment.filename or "arquivo",
        content,
        attachment.content_type or "application/octet-stream",
        caption,
    )


@app.post("/conversations/{conversation_id}/status")
def update_status(conversation_id: int, data: StatusInput, _: dict = Depends(get_current_user)):
    if data.status not in {"open", "resolved", "pending", "snoozed"}:
        raise HTTPException(status_code=400, detail="Status inválido")
    return chatwoot.update_status(conversation_id, data.status)


@app.post("/conversations/{conversation_id}/assignment")
def assign(conversation_id: int, data: AssignmentInput, _: dict = Depends(get_current_user)):
    return chatwoot.assign(conversation_id, data.assignee_id)


@app.post("/conversations/new")
def new_conversation(data: NewConversationInput, _: dict = Depends(get_current_user)):
    inbox_names = {
        settings.CHATWOOT_INBOX_LEADS_ID: "WhatsApp - Leads",
        settings.CHATWOOT_INBOX_CAMPANHAS_INTERNAS_ID: "WhatsApp - Campanhas internas",
        settings.CHATWOOT_INBOX_SUPORTE_ID: "WhatsApp - Suporte",
        settings.CHATWOOT_INBOX_TRANSACIONAL_ID: "WhatsApp - Transacional",
    }
    inbox_name = inbox_names.get(data.inbox_id)
    if inbox_name is None:
        raise HTTPException(status_code=400, detail="Caixa de saída inválida")

    phone = "".join(character for character in data.phone_number if character.isdigit())
    if len(phone) < 10 or len(phone) > 13:
        raise HTTPException(status_code=400, detail="Informe um telefone válido com DDD")

    try:
        response = requests.post(
            settings.N8N_ACTIVE_SEND_URL,
            files={
                "field-0": (None, data.name.strip()),
                "field-1": (None, phone),
                "field-2": (None, inbox_name),
                "field-3": (None, data.message.strip()),
            },
            headers={"Accept": "application/json"},
            timeout=120,
        )
    except requests.RequestException as exc:
        raise HTTPException(status_code=503, detail="Automação de envio indisponível") from exc

    if response.status_code >= 400:
        detail = "A automação não conseguiu enviar a mensagem"
        try:
            body = response.json()
            detail = body.get("message") or body.get("error") or body.get("detail") or detail
        except ValueError:
            pass
        raise HTTPException(status_code=response.status_code, detail=detail)

    try:
        result = response.json()
    except ValueError:
        result = {"sucesso": True, "mensagem": "Solicitação de envio processada."}

    if isinstance(result, list) and result:
        result = result[0]
    return result
