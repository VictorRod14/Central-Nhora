from fastapi import Header, HTTPException
import requests

from app.core.config import settings


def extract_token(authorization: str | None) -> str:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Sessão não informada")
    return authorization.removeprefix("Bearer ").strip()


def get_current_user(authorization: str | None = Header(default=None)) -> dict:
    token = extract_token(authorization)
    try:
        response = requests.get(
            f"{settings.NHORA_API_URL.rstrip('/')}/platform-admin/overview",
            headers={"Authorization": f"Bearer {token}"},
            timeout=settings.REQUEST_TIMEOUT_SECONDS,
        )
    except requests.RequestException as exc:
        raise HTTPException(status_code=503, detail="Plataforma Nhora indisponível") from exc

    if response.status_code != 200:
        raise HTTPException(status_code=401, detail="Sessão inválida ou expirada")

    if response.status_code == 403:
        raise HTTPException(status_code=403, detail="Acesso exclusivo da equipe Nhora")
    return {"name": "Equipe Nhora", "role": "platform_admin"}
