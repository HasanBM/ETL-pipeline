import pytest, logging, os, boto3
from moto import mock_aws
from extract_lambda.utils import get_secret, format_response, log_message


class TestGetSecret:
    def test_get_secret(self, secretsmanager_client):
        secretsmanager_client.create_secret(
            Name="aSecret",
            SecretString=str(
                """{
                        "username":"userId",
                        "password":"password"
                    }"""
            ),
        )
        response = get_secret(secret_name="aSecret", region_name="eu-west-2")
        assert response == {"username": "userId", "password": "password"}


class TestFormatResponse:
    @pytest.mark.skip
    def test_format_response(self):
        assert False


class TestLogMessage:
    def test_log_message(self, caplog):
        caplog.set_level(logging.INFO)
        result = log_message("function_name", 30, "This is a warning")
        expected = ["This is a warning"]
        assert caplog.messages == expected
        assert "WARNING" in caplog.text
