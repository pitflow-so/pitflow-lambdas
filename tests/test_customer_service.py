import importlib
import sys
import unittest
from pathlib import Path
from unittest.mock import MagicMock, call, patch


SHARED_LAYER = Path(__file__).resolve().parents[1] / "layers" / "shared" / "python"
sys.path.insert(0, str(SHARED_LAYER))

customer_service = importlib.import_module("pitflow_shared.customer_service")


class CustomerServiceConnectionTest(unittest.TestCase):
    def setUp(self):
        customer_service._connection = None

    def tearDown(self):
        customer_service._connection = None

    @patch.object(customer_service.psycopg2, "connect")
    @patch.object(customer_service, "get_secret_value")
    def test_connect_uses_registry_database_secret_keys(
        self, get_secret_value, connect
    ):
        get_secret_value.side_effect = [
            "registry-host",
            "5432",
            "registry-db",
            "registry-user",
            "registry-password",
        ]
        connection = MagicMock()
        connection.closed = False
        connect.return_value = connection

        result = customer_service._connect()

        self.assertIs(result, connection)
        self.assertEqual(
            get_secret_value.call_args_list,
            [
                call("PITFLOW_REGISTRY_DB_HOST"),
                call("PITFLOW_REGISTRY_DB_PORT", "5432"),
                call("PITFLOW_REGISTRY_DB_NAME"),
                call("PITFLOW_REGISTRY_DB_USERNAME"),
                call("PITFLOW_REGISTRY_DB_PASSWORD"),
            ],
        )
        connect.assert_called_once_with(
            host="registry-host",
            port="5432",
            dbname="registry-db",
            user="registry-user",
            password="registry-password",
            cursor_factory=customer_service.RealDictCursor,
            connect_timeout=5,
        )


if __name__ == "__main__":
    unittest.main()
