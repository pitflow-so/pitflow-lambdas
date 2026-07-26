import json
import urllib.error
import urllib.request
from enum import Enum

from pitflow_shared.secret_manager_service import get_secret_value


class DecisionResult(Enum):
    SUCCESS = "SUCCESS"
    CONFLICT = "CONFLICT"
    ERROR = "ERROR"


def process_decision(
    token: str,
    reason: str | None = None,
) -> DecisionResult:
    """Registra a decisão e preserva o resultado HTTP relevante."""
    base_url = _get_api_url()
    url = f"{base_url}/operation/external/events/service-orders/decision"
    payload = json.dumps({"token": token, "reason": reason}).encode("utf-8")

    request = urllib.request.Request(
        url,
        data=payload,
        method="POST",
        headers={"Content-Type": "application/json"},
    )

    try:
        with urllib.request.urlopen(request, timeout=10) as response:
            if response.status in (200, 204):
                return DecisionResult.SUCCESS
            return DecisionResult.ERROR
    except urllib.error.HTTPError as exception:
        print(
            "HTTP error ao chamar Spring Boot: "
            f"{exception.code} - {exception.reason}"
        )
        if exception.code == 409:
            return DecisionResult.CONFLICT
        return DecisionResult.ERROR
    except Exception as exception:
        print(f"Erro ao chamar Spring Boot: {exception}")
        return DecisionResult.ERROR


def _get_api_url() -> str:
    return get_secret_value("API_PUBLIC_URL")
