from datetime import datetime, timedelta, timezone
from typing import Any

import jwt

from pitflow_shared.secret_manager_service import get_secret_value


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
