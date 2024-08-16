import pytest, json, boto3, os
from moto import mock_aws
from unittest.mock import patch
from datetime import datetime
from dotenv import load_dotenv
from extract_lambda.extract import extract


class MockedConnection:
    def __init__(
        self,
        user=os.getenv("Username"),
        password=os.getenv("Password"),
        database=os.getenv("Database"),
        host=os.getenv("Hostname"),
        port=os.getenv("Port"),
    ):
        self.user = user
        self.password = password
        self.database = database
        self.host = host
        self.port = port
        self.columns = [
            {"name": "data_id"},
            {"name": "meaningful_data"},
            {"name": "last_updated"},
        ]
        self.rows_data1 = [
            ["1", "old_data1", "1970-01-01 20:00:00"],
            ["2", "old_data2", "1970-01-01 20:00:00"],
        ]

        self.rows_data2 = [
            ["1", "new_data1", "1980-01-01 20:00:00"],
            ["2", "old_data2", "1970-01-01 20:00:00"],
        ]

    def run(self, query):
        if "WHERE" in query:
            return self.rows_data2
        return self.rows_data1

    def close(self):
        pass


class TestExtract:
    def test_extract_writes_all_tables_to_s3_as_directories(
        self, s3_client, s3_data_buckets, create_secrets
    ):

        extract("onyx-totesys-ingested-data-bucket", s3_client)
        result_list_bucket = s3_client.list_objects(
            Bucket="onyx-totesys-ingested-data-bucket"
        )["Contents"]
        result = [file_data["Key"] for file_data in result_list_bucket]
        expected = [
            "counterparty",
            "currency",
            "department",
            "design",
            "staff",
            "sales_order",
            "address",
            "payment",
            "purchase_order",
            "payment_type",
            "transaction",
            "last_extract",
        ]

        for table in expected:
            assert any([folder.startswith(table) for folder in result])

    def test_extract_writes_jsons_into_s3_with_correct_structure_from_db(
        self, s3_client, s3_data_buckets, create_secrets
    ):

        extract("onyx-totesys-ingested-data-bucket", s3_client)
        result_list_bucket = s3_client.list_objects(
            Bucket="onyx-totesys-ingested-data-bucket"
        )["Contents"]
        result = [bucket["Key"] for bucket in result_list_bucket]
        for key in result:
            if not key.endswith(".txt"):  # Filter out .txt files
                json_file = s3_client.get_object(
                    Bucket="onyx-totesys-ingested-data-bucket", Key=key
                )
                json_contents = json_file["Body"].read().decode("utf-8")
                content = json.loads(json_contents)
                for folder in content:
                    assert content[folder][0]["created_at"]

    def test_extract_writes_jsons_into_s3_with_correct_data_type_from_db(
        self, s3_client, s3_data_buckets, create_secrets
    ):

        extract("onyx-totesys-ingested-data-bucket", s3_client)
        result_list_bucket = s3_client.list_objects(
            Bucket="onyx-totesys-ingested-data-bucket"
        )["Contents"]
        result = [bucket["Key"] for bucket in result_list_bucket]
        for key in result:
            if ".txt" not in key:
                json_file = s3_client.get_object(
                    Bucket="onyx-totesys-ingested-data-bucket", Key=key
                )
                json_contents = json_file["Body"].read().decode("utf-8")
                content = json.loads(json_contents)
                for folder in content:
                    value = content[folder][0]["last_updated"]
                    date = datetime.strptime(value, "%Y-%m-%d %H:%M:%S")
                    assert isinstance(date, datetime)

    @patch("extract_lambda.extract.connect_to_db", return_value=MockedConnection())
    def test_mocked_connection_patch_working(self, patched_conn, s3_data_buckets):
        extract("onyx-totesys-ingested-data-bucket", s3_data_buckets)

        result_list_bucket = s3_data_buckets.list_objects(
            Bucket="onyx-totesys-ingested-data-bucket"
        )["Contents"]

        extract("onyx-totesys-ingested-data-bucket", s3_data_buckets)

        result_list_bucket = s3_data_buckets.list_objects(
            Bucket="onyx-totesys-ingested-data-bucket"
        )["Contents"]

        result = [bucket["Key"] for bucket in result_list_bucket]
        for key in result:
            if ".txt" not in key:
                json_file = s3_data_buckets.get_object(
                    Bucket="onyx-totesys-ingested-data-bucket", Key=key
                )
                json_contents = json_file["Body"].read().decode("utf-8")
                content = json.loads(json_contents)
                for folder in content:
                    print(content[folder][0])
                    assert content[folder][0]["meaningful_data"]
