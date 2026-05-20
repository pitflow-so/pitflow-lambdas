import json

from pitflow_shared.cpf_validator import validate_cpf
from pitflow_shared.customer_service import find_customer
from pitflow_shared.jwt_service import generate_token


def lambda_handler(event, context):
    try:
        body = json.loads(event.get("body") or "{}")
        cpf = body.get("cpf", "").strip()

        if not cpf:
            return _response(400, {"error": "CPF e obrigatorio"})

        if not validate_cpf(cpf):
            return _response(400, {"error": "CPF invalido"})

        customer = find_customer(cpf)
        if not customer:
            return _response(404, {"error": "Cliente nao encontrado"})

        if customer["status"] != "ACTIVE":
            return _response(403, {"error": "Cliente inativo"})

        print(f"Cliente encontrado: {customer['name']} (CPF: {customer['document']})")
        token = generate_token(customer)

        return _response(200, {"token": token})

    except Exception as e:
        print(f"Erro inesperado: {e}")
        return _response(500, {"error": "Erro interno"})


def _response(status_code, body):
    return {
        "statusCode": status_code,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps(body),
    }


if __name__ == "__main__":
    test_event = {
        "body": json.dumps({"cpf": "78177454048"})
    }
    result = lambda_handler(test_event, None)
    print(result)
