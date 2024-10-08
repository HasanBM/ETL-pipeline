import pytest
from decimal import Decimal
from datetime import datetime
from extract_utils import get_secret, format_response


class TestGetSecret:
    def test_get_secret(self, secretsmanager_client):
        secretsmanager_client.create_secret(
            Name="aSecret",
            SecretString=str("""{"username": "userId", "password": "password"}"""),
        )
        response = get_secret(secret_name="aSecret", region_name="eu-west-2")
        assert response == {"username": "userId", "password": "password"}


class TestFormatResponse:
    @pytest.mark.parametrize(
        "columns, response, expected, should_raise",
        [
            (["A", "B"], [[1, 2], [3, 4]], [{"A": 1, "B": 2}, {"A": 3, "B": 4}], False),
            (
                ["A", "B"],
                [[1, 2], [Decimal("1.21"), 2]],
                [{"A": 1, "B": 2}, {"A": 1.21, "B": 2}],
                False,
            ),
            (
                ["Date", "Value"],
                [[datetime(2024, 8, 18, 12, 0, 0), 1.23]],
                [{"Date": "2024-08-18 12:00:00", "Value": 1.23}],
                False,
            ),
            (["A", "B"], [[1, 2], [3]], None, True),
            (["A"], [[1, 2]], None, True),
        ],
        ids=[
            "Simple integer values",
            "Decimal to float conversion",
            "Datetime formatting",
            "More columns than values in row",
            "Fewer columns than values in row",
        ],
    )
    def test_format_response(self, columns, response, expected, should_raise):
        if should_raise:
            with pytest.raises(
                ValueError, match="Mismatch between number of columns and row length"
            ):
                format_response(columns, response)
        else:
            result = format_response(columns, response)
            assert result == expected
