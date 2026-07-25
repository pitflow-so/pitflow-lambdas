import json
from urllib.parse import parse_qs

from pitflow_shared.cpf_validator import validate_cpf
from pitflow_shared.customer_service import find_customer
from pitflow_shared.jwt_service import generate_token
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
    service_order_id = query_params.get("serviceOrderId")
    action = query_params.get("action")

    if not _is_valid_decision_request(service_order_id, action):
        return _html_response(400, render_error("Link invalido ou expirado"))

    return _html_response(200, render_form(service_order_id, action))


def _handle_post(body):
    cpf = (body.get("cpf") or "").strip()
    service_order_id = body.get("serviceOrderId")
    action = body.get("action")

    if not cpf:
        return _html_response(400, render_error("CPF e obrigatorio"))

    if not validate_cpf(cpf):
        return _html_response(400, render_error("CPF invalido"))

    if not _is_valid_decision_request(service_order_id, action):
        return _html_response(400, render_error("Link invalido ou expirado"))

    customer = find_customer(cpf)
    if not customer:
        return _html_response(404, render_error("Cliente nao encontrado"))

    if customer["status"] != "ACTIVE":
        return _html_response(403, render_error("Cliente inativo"))

    token = generate_token(customer)

    success = process_decision(service_order_id, action, token)
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


def _is_valid_decision_request(service_order_id, action):
    return bool(service_order_id) and action in ("APPROVED", "REJECTED")


def _html_response(status_code, html):
    return {
        "statusCode": status_code,
        "headers": {"Content-Type": "text/html; charset=utf-8"},
        "body": html,
    }
