import importlib
import base64
import json
import sys
import types
import unittest
from pathlib import Path
from unittest.mock import Mock


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
BUDGET_FORM_SRC = REPOSITORY_ROOT / "lambdas" / "budget_form" / "src"


def _module(name, **members):
    module = types.ModuleType(name)
    for member_name, value in members.items():
        setattr(module, member_name, value)
    return module


class BudgetFormHandlerTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        sys.path.insert(0, str(BUDGET_FORM_SRC))

        cls.decode_decision_token = Mock()
        cls.process_decision = Mock()

        sys.modules["pitflow_shared"] = _module("pitflow_shared")
        sys.modules["pitflow_shared.jwt_service"] = _module(
            "pitflow_shared.jwt_service",
            decode_decision_token=cls.decode_decision_token,
        )
        cls.DecisionResult = types.SimpleNamespace(
            SUCCESS="SUCCESS",
            CONFLICT="CONFLICT",
            ERROR="ERROR",
        )
        sys.modules["services.decision_service"] = _module(
            "services.decision_service",
            DecisionResult=cls.DecisionResult,
            process_decision=cls.process_decision,
        )

        sys.modules.pop("handler", None)
        cls.handler = importlib.import_module("handler")

    def setUp(self):
        self.decode_decision_token.reset_mock()
        self.decode_decision_token.side_effect = None
        self.decode_decision_token.return_value = {
            "serviceOrderId": "order-1",
            "status": "APPROVED",
            "amount": "450.00",
        }
        self.process_decision.reset_mock()
        self.process_decision.side_effect = None
        self.process_decision.return_value = self.DecisionResult.SUCCESS

    def test_api_gateway_v2_get_renders_confirmation_form(self):
        response = self.handler.lambda_handler(
            {
                "requestContext": {"http": {"method": "GET"}},
                "queryStringParameters": {"token": "decision-jwt"},
            },
            None,
        )

        self.assertEqual(200, response["statusCode"])
        self.assertEqual("no-store", response["headers"]["Cache-Control"])
        self.assertIn('method="POST"', response["body"])
        self.assertIn(
            'action="/customer/budget/confirm"',
            response["body"],
        )
        self.assertIn('name="token" value="decision-jwt"', response["body"])
        self.assertIn("R$ 450,00", response["body"])
        self.assertNotIn('name="cpf"', response["body"])
        self.process_decision.assert_not_called()

    def test_get_renders_required_reason_for_rejection(self):
        self.decode_decision_token.return_value = {
            "serviceOrderId": "order-1",
            "status": "REJECTED",
        }

        response = self.handler.lambda_handler(
            {
                "httpMethod": "GET",
                "queryStringParameters": {"token": "reject-jwt"},
            },
            None,
        )

        self.assertEqual(200, response["statusCode"])
        self.assertIn('name="reason"', response["body"])
        self.assertIn("required", response["body"])

    def test_get_rejects_missing_invalid_or_expired_token(self):
        self.decode_decision_token.side_effect = ValueError("invalid")

        response = self.handler.lambda_handler(
            {
                "httpMethod": "GET",
                "queryStringParameters": {"token": "invalid"},
            },
            None,
        )

        self.assertEqual(400, response["statusCode"])
        self.process_decision.assert_not_called()

    def test_api_gateway_v2_post_processes_approved_decision(self):
        response = self.handler.lambda_handler(
            {
                "requestContext": {"http": {"method": "POST"}},
                "headers": {
                    "Content-Type": "application/x-www-form-urlencoded",
                },
                "body": "token=decision-jwt",
            },
            None,
        )

        self.assertEqual(200, response["statusCode"])
        self.process_decision.assert_called_once_with(
            "decision-jwt",
            None,
        )

    def test_api_gateway_v2_post_decodes_base64_form_body(self):
        encoded_body = base64.b64encode(
            b"token=decision-jwt"
        ).decode("ascii")

        response = self.handler.lambda_handler(
            {
                "requestContext": {"http": {"method": "POST"}},
                "headers": {
                    "Content-Type": "application/x-www-form-urlencoded",
                },
                "body": encoded_body,
                "isBase64Encoded": True,
            },
            None,
        )

        self.assertEqual(200, response["statusCode"])
        self.process_decision.assert_called_once_with(
            "decision-jwt",
            None,
        )

    def test_post_json_processes_rejection_with_reason(self):
        self.decode_decision_token.return_value = {
            "serviceOrderId": "order-1",
            "status": "REJECTED",
        }

        response = self.handler.lambda_handler(
            {
                "httpMethod": "POST",
                "headers": {"content-type": "application/json"},
                "body": json.dumps(
                    {
                        "token": "reject-jwt",
                        "reason": "Valor acima do esperado",
                    }
                ),
            },
            None,
        )

        self.assertEqual(200, response["statusCode"])
        self.process_decision.assert_called_once_with(
            "reject-jwt",
            "Valor acima do esperado",
        )

    def test_post_rejects_rejection_without_reason(self):
        self.decode_decision_token.return_value = {
            "serviceOrderId": "order-1",
            "status": "REJECTED",
        }

        response = self.handler.lambda_handler(
            {
                "httpMethod": "POST",
                "headers": {},
                "body": "token=reject-jwt",
            },
            None,
        )

        self.assertEqual(400, response["statusCode"])
        self.process_decision.assert_not_called()

    def test_post_revalidates_token(self):
        self.decode_decision_token.side_effect = ValueError("expired")

        response = self.handler.lambda_handler(
            {
                "httpMethod": "POST",
                "headers": {},
                "body": "token=expired-jwt",
            },
            None,
        )

        self.assertEqual(400, response["statusCode"])
        self.process_decision.assert_not_called()

    def test_post_returns_error_when_operation_rejects_decision(self):
        self.process_decision.return_value = self.DecisionResult.ERROR

        response = self.handler.lambda_handler(
            {
                "httpMethod": "POST",
                "headers": {},
                "body": "token=decision-jwt",
            },
            None,
        )

        self.assertEqual(500, response["statusCode"])

    def test_post_explains_when_opposite_decision_was_already_recorded(self):
        self.process_decision.return_value = self.DecisionResult.CONFLICT

        response = self.handler.lambda_handler(
            {
                "httpMethod": "POST",
                "headers": {},
                "body": "token=decision-jwt",
            },
            None,
        )

        self.assertEqual(409, response["statusCode"])
        self.assertIn("ja foi registrada", response["body"])

    def test_unsupported_method_is_rejected(self):
        response = self.handler.lambda_handler(
            {"httpMethod": "DELETE"},
            None,
        )

        self.assertEqual(400, response["statusCode"])


if __name__ == "__main__":
    unittest.main()
