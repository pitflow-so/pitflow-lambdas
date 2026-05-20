import base64
import json
import os
from typing import Any

import boto3


SECRET_NAME = "secret_pitflow"
IS_LOCAL = os.getenv("IS_LOCAL", "false").lower() == "true"

_secret_cache: dict[str, Any] | None = None


def get_secret_value(name: str, default: str | None = None) -> str:
    if IS_LOCAL:
        value = os.getenv(name, default)
    else:
        value = _get_secret_payload().get(name, default)

    if value is None:
        source = f"environment variable '{name}'" if IS_LOCAL else f"secret '{SECRET_NAME}'"
        raise ValueError(f"{name} is not set in {source}")

    return str(value)


def _get_secret_payload() -> dict[str, Any]:
    global _secret_cache

    if _secret_cache is None:
        _secret_cache = _load_secret()

    return _secret_cache


def _load_secret() -> dict[str, Any]:
    client = boto3.client("secretsmanager")
    response = client.get_secret_value(SecretId=SECRET_NAME)

    secret_content = response.get("SecretString")
    if secret_content is None:
        secret_binary = response.get("SecretBinary")
        if secret_binary is None:
            raise ValueError(f"{SECRET_NAME} does not contain SecretString or SecretBinary")
        secret_content = base64.b64decode(secret_binary).decode("utf-8")

    secret_payload = json.loads(secret_content)
    if not isinstance(secret_payload, dict):
        raise ValueError(f"{SECRET_NAME} must contain a JSON object")

    return secret_payload
