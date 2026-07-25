import importlib.util
import sys
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest.mock import patch

import jwt


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
SHARED_LAYER = REPOSITORY_ROOT / "layers" / "shared" / "python"
sys.path.insert(0, str(SHARED_LAYER))

JWT_SERVICE_PATH = (
    SHARED_LAYER / "pitflow_shared" / "jwt_service.py"
)
SPEC = importlib.util.spec_from_file_location(
    "decision_jwt_service_under_test",
    JWT_SERVICE_PATH,
)
JWT_SERVICE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(JWT_SERVICE)


class DecisionTokenTest(unittest.TestCase):

    secret = "a-secure-test-secret-with-more-than-32-characters"

    @patch.object(JWT_SERVICE, "get_secret_value", return_value=secret)
    def test_decodes_valid_external_decision_token(self, _):
        token = self._token(status="APPROVED")

        claims = JWT_SERVICE.decode_decision_token(token)

        self.assertEqual("external-decision", claims["sub"])
        self.assertEqual("order-1", claims["serviceOrderId"])
        self.assertEqual("APPROVED", claims["status"])

    @patch.object(JWT_SERVICE, "get_secret_value", return_value=secret)
    def test_rejects_expired_token(self, _):
        token = self._token(
            status="APPROVED",
            expiration=datetime.now(timezone.utc) - timedelta(minutes=1),
        )

        with self.assertRaisesRegex(ValueError, "invalido ou expirado"):
            JWT_SERVICE.decode_decision_token(token)

    @patch.object(JWT_SERVICE, "get_secret_value", return_value=secret)
    def test_rejects_token_created_for_another_purpose(self, _):
        token = self._token(status="APPROVED", subject="customer")

        with self.assertRaisesRegex(ValueError, "finalidade"):
            JWT_SERVICE.decode_decision_token(token)

    @patch.object(JWT_SERVICE, "get_secret_value", return_value=secret)
    def test_rejects_unsupported_decision(self, _):
        token = self._token(status="CANCELLED")

        with self.assertRaisesRegex(ValueError, "decisao invalida"):
            JWT_SERVICE.decode_decision_token(token)

    def _token(
        self,
        status,
        subject="external-decision",
        expiration=None,
    ):
        return jwt.encode(
            {
                "sub": subject,
                "serviceOrderId": "order-1",
                "status": status,
                "exp": expiration
                or datetime.now(timezone.utc) + timedelta(minutes=5),
            },
            self.secret,
            algorithm="HS256",
        )


if __name__ == "__main__":
    unittest.main()
