import importlib.util
import json
import sys
import types
import unittest
from pathlib import Path
from unittest.mock import MagicMock, Mock, patch
from urllib.error import HTTPError


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
DECISION_SERVICE_PATH = (
    REPOSITORY_ROOT
    / "lambdas"
    / "budget_form"
    / "src"
    / "services"
    / "decision_service.py"
)


class DecisionServiceTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        secret_module = types.ModuleType(
            "pitflow_shared.secret_manager_service"
        )
        cls.get_secret_value = Mock(return_value="https://api.example")
        secret_module.get_secret_value = cls.get_secret_value

        sys.modules["pitflow_shared"] = types.ModuleType("pitflow_shared")
        sys.modules[
            "pitflow_shared.secret_manager_service"
        ] = secret_module

        spec = importlib.util.spec_from_file_location(
            "budget_form_decision_service",
            DECISION_SERVICE_PATH,
        )
        cls.service = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(cls.service)

    def setUp(self):
        self.get_secret_value.reset_mock()
        self.get_secret_value.return_value = "https://api.example"

    @patch("urllib.request.urlopen")
    def test_posts_decision_token_and_reason_to_operation(self, urlopen):
        response = MagicMock()
        response.__enter__.return_value.status = 204
        urlopen.return_value = response

        success = self.service.process_decision(
            "decision-jwt",
            "Valor acima do esperado",
        )

        self.assertTrue(success)
        self.get_secret_value.assert_called_with("API_PUBLIC_URL")
        request = urlopen.call_args.args[0]
        self.assertEqual(
            "https://api.example/external/events/service-orders/decision",
            request.full_url,
        )
        self.assertEqual("POST", request.method)
        self.assertNotIn("Authorization", request.headers)
        self.assertEqual(
            {
                "token": "decision-jwt",
                "reason": "Valor acima do esperado",
            },
            json.loads(request.data.decode("utf-8")),
        )

    @patch("urllib.request.urlopen")
    def test_returns_false_on_http_error(self, urlopen):
        urlopen.side_effect = HTTPError(
            "https://api.example",
            409,
            "Conflict",
            {},
            None,
        )

        self.assertFalse(
            self.service.process_decision("decision-jwt")
        )

    @patch("urllib.request.urlopen")
    def test_returns_false_on_network_error(self, urlopen):
        urlopen.side_effect = TimeoutError("timeout")

        self.assertFalse(
            self.service.process_decision("decision-jwt")
        )


if __name__ == "__main__":
    unittest.main()
