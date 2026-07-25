import importlib
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

        cls.validate_cpf = Mock()
        cls.find_customer = Mock()
        cls.generate_token = Mock()
        cls.process_decision = Mock()

        sys.modules["pitflow_shared"] = _module("pitflow_shared")
        sys.modules["pitflow_shared.cpf_validator"] = _module(
            "pitflow_shared.cpf_validator",
            validate_cpf=cls.validate_cpf,
        )
        sys.modules["pitflow_shared.customer_service"] = _module(
            "pitflow_shared.customer_service",
            find_customer=cls.find_customer,
        )
        sys.modules["pitflow_shared.jwt_service"] = _module(
            "pitflow_shared.jwt_service",
            generate_token=cls.generate_token,
        )
        sys.modules["services.decision_service"] = _module(
            "services.decision_service",
            process_decision=cls.process_decision,
        )

        sys.modules.pop("handler", None)
        cls.handler = importlib.import_module("handler")

    def setUp(self):
        self.validate_cpf.reset_mock()
        self.validate_cpf.return_value = True
        self.find_customer.reset_mock()
        self.find_customer.return_value = {
            "id": "customer-1",
            "status": "ACTIVE",
        }
        self.generate_token.reset_mock()
        self.generate_token.return_value = "customer-jwt"
        self.process_decision.reset_mock()
        self.process_decision.return_value = True

    def test_api_gateway_v2_get_renders_confirmation_form(self):
        response = self.handler.lambda_handler(
            {
                "requestContext": {
                    "http": {
                        "method": "GET",
                    },
                },
                "queryStringParameters": {
                    "serviceOrderId": "order-1",
                    "action": "APPROVED",
                },
            },
            None,
        )

        self.assertEqual(200, response["statusCode"])
        self.assertIn('method="POST"', response["body"])
        self.assertIn(
            'action="/customer/budget/confirm"',
            response["body"],
        )
        self.assertIn('value="order-1"', response["body"])
        self.assertIn('value="APPROVED"', response["body"])
        self.process_decision.assert_not_called()

    def test_get_rejects_missing_or_invalid_action(self):
        for query in (
            {},
            {"serviceOrderId": "order-1"},
            {"serviceOrderId": "order-1", "action": "UNKNOWN"},
        ):
            with self.subTest(query=query):
                response = self.handler.lambda_handler(
                    {"httpMethod": "GET", "queryStringParameters": query},
                    None,
                )
                self.assertEqual(400, response["statusCode"])

    def test_post_form_processes_approved_decision(self):
        response = self.handler.lambda_handler(
            {
                "requestContext": {
                    "http": {
                        "method": "POST",
                    },
                },
                "headers": {
                    "Content-Type": "application/x-www-form-urlencoded",
                },
                "body": (
                    "cpf=529.982.247-25"
                    "&serviceOrderId=order-1"
                    "&action=APPROVED"
                ),
            },
            None,
        )

        self.assertEqual(200, response["statusCode"])
        self.validate_cpf.assert_called_once_with("529.982.247-25")
        self.find_customer.assert_called_once_with("529.982.247-25")
        self.generate_token.assert_called_once()
        self.process_decision.assert_called_once_with(
            "order-1",
            "APPROVED",
            "customer-jwt",
        )

    def test_post_json_processes_rejected_decision(self):
        response = self.handler.lambda_handler(
            {
                "httpMethod": "POST",
                "headers": {"content-type": "application/json"},
                "body": json.dumps(
                    {
                        "cpf": "52998224725",
                        "serviceOrderId": "order-1",
                        "action": "REJECTED",
                    }
                ),
            },
            None,
        )

        self.assertEqual(200, response["statusCode"])
        self.process_decision.assert_called_once_with(
            "order-1",
            "REJECTED",
            "customer-jwt",
        )

    def test_post_rejects_missing_or_invalid_cpf(self):
        cases = (
            ("", True),
            ("111.111.111-11", False),
        )

        for cpf, is_valid in cases:
            with self.subTest(cpf=cpf):
                self.validate_cpf.reset_mock()
                self.validate_cpf.return_value = is_valid
                response = self.handler.lambda_handler(
                    {
                        "httpMethod": "POST",
                        "headers": {},
                        "body": (
                            f"cpf={cpf}"
                            "&serviceOrderId=order-1"
                            "&action=APPROVED"
                        ),
                    },
                    None,
                )
                self.assertEqual(400, response["statusCode"])

        self.process_decision.assert_not_called()

    def test_post_rejects_customer_not_found_or_inactive(self):
        customers = (None, {"id": "customer-1", "status": "INACTIVE"})

        for customer in customers:
            with self.subTest(customer=customer):
                self.find_customer.reset_mock()
                self.find_customer.return_value = customer
                response = self.handler.lambda_handler(
                    {
                        "httpMethod": "POST",
                        "headers": {},
                        "body": (
                            "cpf=52998224725"
                            "&serviceOrderId=order-1"
                            "&action=APPROVED"
                        ),
                    },
                    None,
                )
                self.assertIn(response["statusCode"], (403, 404))

        self.process_decision.assert_not_called()

    def test_post_returns_error_when_operation_rejects_decision(self):
        self.process_decision.return_value = False

        response = self.handler.lambda_handler(
            {
                "httpMethod": "POST",
                "headers": {},
                "body": (
                    "cpf=52998224725"
                    "&serviceOrderId=order-1"
                    "&action=APPROVED"
                ),
            },
            None,
        )

        self.assertEqual(500, response["statusCode"])

    def test_unsupported_method_is_rejected(self):
        response = self.handler.lambda_handler(
            {"httpMethod": "DELETE"},
            None,
        )

        self.assertEqual(400, response["statusCode"])


if __name__ == "__main__":
    unittest.main()
