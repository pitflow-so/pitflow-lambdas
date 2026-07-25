import json
from urllib.parse import parse_qs

from pitflow_shared.jwt_service import decode_decision_token
from services.decision_service import process_decision
from templates.budget_page import render_error, render_form, render_success


def lambda_handler(event, context):
    http_method = _get_http_method(event)
    query_params = event.get("queryStringParameters") or {}

    if http_method == "GET":
        return _handle_get(query_params)

    if http_method == "POST":
        body = _parse_body(event)
        return _handle_post(body)

    return _html_response(400, render_error("Requisicao invalida"))


def _get_http_method(event):
    request_context = event.get("requestContext") or {}
    http_context = request_context.get("http") or {}
    return event.get("httpMethod") or http_context.get("method", "")


def _handle_get(query_params):
    token = query_params.get("token")
    claims = _decode_token(token)
    if claims is None:
        return _html_response(400, render_error("Link invalido ou expirado"))

    return _html_response(200, render_form(token, claims["status"]))


def _handle_post(body):
    token = body.get("token")
    reason = (body.get("reason") or "").strip()
    claims = _decode_token(token)
    if claims is None:
        return _html_response(400, render_error("Link invalido ou expirado"))

    action = claims["status"]
    if action == "REJECTED" and not reason:
        return _html_response(
            400,
            render_error("O motivo da recusa e obrigatorio"),
        )

    success = process_decision(token, reason or None)
    if not success:
        return _html_response(500, render_error("Erro ao processar decisao. Tente novamente."))

    label = "aprovado" if action == "APPROVED" else "recusado"
    return _html_response(200, render_success(label))


def _parse_body(event):
    body = event.get("body") or ""
    content_type = _get_header(event.get("headers") or {}, "content-type")

    if "application/json" in content_type:
        return json.loads(body or "{}")

    parsed = parse_qs(body, keep_blank_values=True)
    return {key: values[0] if values else "" for key, values in parsed.items()}


def _get_header(headers, name):
    for key, value in headers.items():
        if key.lower() == name:
            return value.lower()
    return ""


def _decode_token(token):
    try:
        return decode_decision_token(token)
    except ValueError:
        return None


def _html_response(status_code, html):
    return {
        "statusCode": status_code,
        "headers": {
            "Content-Type": "text/html; charset=utf-8",
            "Cache-Control": "no-store",
        },
        "body": html,
    }
