from datetime import datetime, timedelta, timezone
from typing import Any

import jwt

from pitflow_shared.secret_manager_service import get_secret_value

DECISION_SUBJECT = "external-decision"
DECISION_STATUSES = ("APPROVED", "REJECTED")


def generate_token(customer: dict[str, Any]) -> str:
    now = datetime.now(timezone.utc)

    payload = {
        "sub": str(customer["id"]),
        "cpf": customer["document"],
        "role": "ROLE_CUSTOMER",
        "iat": now,
        "exp": now + timedelta(hours=3),
    }

    return jwt.encode(payload, get_secret_value("JWT_SECRET"), algorithm="HS256")


def decode_decision_token(token: str) -> dict[str, Any]:
    if not token:
        raise ValueError("Token de decisao ausente")

    try:
        payload = jwt.decode(
            token,
            get_secret_value("JWT_SECRET"),
            algorithms=["HS256"],
        )
    except jwt.PyJWTError as error:
        raise ValueError("Token de decisao invalido ou expirado") from error

    if payload.get("sub") != DECISION_SUBJECT:
        raise ValueError("Token com finalidade invalida")
    if not payload.get("serviceOrderId"):
        raise ValueError("Token sem ordem de servico")
    if payload.get("status") not in DECISION_STATUSES:
        raise ValueError("Token com decisao invalida")

    return payload
