import urllib.request
import urllib.error
import json

from pitflow_shared.secret_manager_service import get_secret_value


def process_decision(service_order_id: str, action: str, token: str) -> bool:
    """
    Chama a API Spring Boot para registrar a decisão do cliente.
    Retorna True se sucesso, False caso contrário.
    """
    base_url = _get_api_url()
    url = f"{base_url}/operation/service-orders/v2/{service_order_id}/budget-decision"

    payload = json.dumps({"decision": action}).encode("utf-8")

    req = urllib.request.Request(
        url,
        data=payload,
        method="PATCH",
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}",
        },
    )

    try:
        with urllib.request.urlopen(req, timeout=10) as response:
            return response.status in (200, 204)
    except urllib.error.HTTPError as e:
        print(f"HTTP error ao chamar Spring Boot: {e.code} - {e.reason}")
        return False
    except Exception as e:
        print(f"Erro ao chamar Spring Boot: {e}")
        return False

def _get_api_url() -> str:
    return get_secret_value("SPRING_API_URL")
