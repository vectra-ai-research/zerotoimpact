import os
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock, patch


API_DIRECTORY = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(API_DIRECTORY))

from lambda_privesc.create import CreateLambdaPriEsc
from lib.aws_region import resolve_aws_region
from lib.instance_repo import add_to_disk
from policy_ransom_exploit.create import Create as PolicyRansomCreate
from policy_ransom_exploit.s3_ransomware import s3Ransomware
from snapshot_exfil.attack import get_snapshot_recipient_account_id, redact_snapshot_recipient
from snapshot_exfil.create import Create as SnapshotExfilCreate


class FakeS3Client:
    def __init__(self):
        self.create_bucket_calls = []
        self.put_bucket_encryption_calls = []

    def create_bucket(self, **kwargs):
        self.create_bucket_calls.append(kwargs)
        return {"Location": "/example"}

    def put_object(self, **kwargs):
        return {}

    def put_bucket_encryption(self, **kwargs):
        self.put_bucket_encryption_calls.append(kwargs)
        return {}


class FakeRansomwareS3Client:
    def __init__(self):
        self.copy_object_calls = []
        self.put_object_calls = []

    def list_objects_v2(self, **kwargs):
        return {
            "Contents": [
                {"Key": "first.txt"},
                {"Key": "second.txt"},
                {"Key": "third.txt"},
            ]
        }

    def copy_object(self, **kwargs):
        self.copy_object_calls.append(kwargs)
        return {}

    def put_object(self, **kwargs):
        self.put_object_calls.append(kwargs)
        return {}


class FakeRdsClient:
    def __init__(self):
        self.create_db_instance_calls = []
        self.waiter = Mock()

    def create_db_instance(self, **kwargs):
        self.create_db_instance_calls.append(kwargs)
        return {"DBInstance": {"DBInstanceIdentifier": kwargs["DBInstanceIdentifier"]}}

    def get_waiter(self, name):
        if name != "db_instance_available":
            raise AssertionError(f"Unexpected waiter: {name}")
        return self.waiter


class RegionSupportTests(unittest.TestCase):
    def test_environment_region_takes_precedence_over_profile(self):
        with patch.dict(os.environ, {"AWS_DEFAULT_REGION": "eu-west-1"}, clear=True):
            self.assertEqual(resolve_aws_region("example"), "eu-west-1")

    @patch("lib.aws_region.boto3.Session")
    def test_profile_region_is_used_when_environment_is_unset(self, mock_session):
        mock_session.return_value.region_name = "ap-southeast-2"

        with patch.dict(os.environ, {}, clear=True):
            self.assertEqual(resolve_aws_region("example"), "ap-southeast-2")

        mock_session.assert_called_once_with(profile_name="example")

    @patch("lib.aws_region.boto3.Session")
    def test_missing_region_is_rejected(self, mock_session):
        mock_session.return_value.region_name = None

        with patch.dict(os.environ, {}, clear=True):
            with self.assertRaisesRegex(RuntimeError, "No AWS Region is configured"):
                resolve_aws_region("example")

    @patch("lambda_privesc.create.create_client_profile")
    def test_lambda_scenario_uses_the_requested_region(self, mock_create_client):
        client = Mock()
        mock_create_client.return_value = client

        CreateLambdaPriEsc("case-1", "example", "eu-west-1", tempfile.gettempdir())

        mock_create_client.assert_called_once_with("iam", "eu-west-1", "example")

    @patch("policy_ransom_exploit.create.create_client_profile")
    def test_s3_bucket_uses_location_constraint_outside_us_east_1(self, mock_create_client):
        s3_client = FakeS3Client()
        mock_create_client.return_value = s3_client
        scenario = PolicyRansomCreate("case-1", "example", "eu-west-1", tempfile.gettempdir())

        scenario._create_bucket_and_put_files()

        self.assertEqual(
            s3_client.create_bucket_calls,
            [{
                "Bucket": "zti-bucket-to-ransomware-case-1",
                "CreateBucketConfiguration": {"LocationConstraint": "eu-west-1"},
            }],
        )
        self.assertEqual(
            s3_client.put_bucket_encryption_calls,
            [{
                "Bucket": "zti-bucket-to-ransomware-case-1",
                "ServerSideEncryptionConfiguration": {
                    "Rules": [{
                        "ApplyServerSideEncryptionByDefault": {"SSEAlgorithm": "AES256"},
                        "BlockedEncryptionTypes": {"EncryptionType": ["NONE"]},
                    }]
                },
            }],
        )

    @patch("policy_ransom_exploit.create.create_client_profile")
    def test_s3_bucket_omits_location_constraint_in_us_east_1(self, mock_create_client):
        s3_client = FakeS3Client()
        mock_create_client.return_value = s3_client
        scenario = PolicyRansomCreate("case-1", "example", "us-east-1", tempfile.gettempdir())

        scenario._create_bucket_and_put_files()

        self.assertEqual(s3_client.create_bucket_calls, [{"Bucket": "zti-bucket-to-ransomware-case-1"}])
        self.assertEqual(
            s3_client.put_bucket_encryption_calls[0]["Bucket"],
            "zti-bucket-to-ransomware-case-1",
        )

    @patch("snapshot_exfil.create.create_client_profile")
    def test_snapshot_scenario_resolves_an_ami_in_the_requested_region(self, mock_create_client):
        ssm_client = Mock()
        ssm_client.get_parameter.return_value = {"Parameter": {"Value": "ami-regional"}}
        mock_create_client.return_value = ssm_client
        scenario = SnapshotExfilCreate("case-1", "example", "eu-west-1", tempfile.gettempdir())

        self.assertEqual(scenario.get_latest_amazon_linux_ami(), "ami-regional")

        mock_create_client.assert_called_once_with("ssm", "eu-west-1", "example")

    def test_snapshot_recipient_must_be_a_12_digit_environment_value(self):
        with patch.dict(os.environ, {}, clear=True):
            with self.assertRaisesRegex(RuntimeError, "ZTI_SNAPSHOT_RECIPIENT_ACCOUNT_ID"):
                get_snapshot_recipient_account_id()

        with patch.dict(os.environ, {"ZTI_SNAPSHOT_RECIPIENT_ACCOUNT_ID": "not-an-account"}, clear=True):
            with self.assertRaisesRegex(ValueError, "12-digit"):
                get_snapshot_recipient_account_id()

        with patch.dict(os.environ, {"ZTI_SNAPSHOT_RECIPIENT_ACCOUNT_ID": "000000000000"}, clear=True):
            self.assertEqual(get_snapshot_recipient_account_id(), "000000000000")

    def test_snapshot_share_response_redacts_the_recipient(self):
        response = {
            "DBSnapshotAttributesResult": {
                "DBSnapshotIdentifier": "example-snapshot",
                "DBSnapshotAttributes": [
                    {"AttributeName": "restore", "AttributeValues": ["000000000000"]}
                ],
            }
        }

        redacted_response = redact_snapshot_recipient(response)

        self.assertEqual(
            redacted_response["DBSnapshotAttributesResult"]["DBSnapshotAttributes"][0]["AttributeValues"],
            ["<redacted>"],
        )
        self.assertEqual(
            response["DBSnapshotAttributesResult"]["DBSnapshotAttributes"][0]["AttributeValues"],
            ["000000000000"],
        )

    @patch("snapshot_exfil.create.create_client_profile")
    def test_snapshot_instance_is_persisted_before_waiting_for_availability(self, mock_create_client):
        rds_client = FakeRdsClient()
        mock_create_client.return_value = rds_client

        with tempfile.TemporaryDirectory() as directory:
            scenario = SnapshotExfilCreate("case-1", "example", "eu-west-1", directory)
            scenario.status = "create_started"
            scenario.step = 3
            scenario.create_rds_instance("zti-db-case-1", "db.t3.micro", "mysql", "admin", "password")

            with (Path(directory) / "case-1.json").open(encoding="utf-8") as instance_file:
                instance = json.load(instance_file)

        self.assertEqual(instance["resources"]["rds_instance"], "zti-db-case-1")
        self.assertEqual(instance["status"], "create_started")
        rds_client.waiter.wait.assert_called_once_with(DBInstanceIdentifier="zti-db-case-1")

    @patch("policy_ransom_exploit.s3_ransomware.boto3.client")
    def test_s3_ransomware_emits_sse_c_put_and_copy_activity(self, mock_s3_client):
        client = FakeRansomwareS3Client()
        mock_s3_client.return_value = client
        logs = []

        s3Ransomware("access-key", "secret-key", "example-bucket", "eu-west-1", logs, {})

        self.assertEqual(len(client.put_object_calls), 1)
        put_request = client.put_object_calls[0]
        self.assertEqual(put_request["Bucket"], "example-bucket")
        self.assertEqual(put_request["Key"], "first.txt")
        self.assertEqual(put_request["SSECustomerAlgorithm"], "AES256")
        self.assertEqual(len(put_request["SSECustomerKey"]), 32)
        self.assertNotIn("ServerSideEncryption", put_request)
        self.assertNotIn("SSEKMSKeyId", put_request)

        self.assertEqual(len(client.copy_object_calls), 2)
        for expected_key, copy_request in zip(("second.txt", "third.txt"), client.copy_object_calls):
            self.assertEqual(copy_request["Bucket"], "example-bucket")
            self.assertEqual(copy_request["Key"], expected_key)
            self.assertEqual(
                copy_request["CopySource"],
                {"Bucket": "example-bucket", "Key": expected_key},
            )
            self.assertEqual(copy_request["SSECustomerAlgorithm"], "AES256")
            self.assertEqual(copy_request["SSECustomerKey"], put_request["SSECustomerKey"])
            self.assertNotIn("ServerSideEncryption", copy_request)
            self.assertNotIn("SSEKMSKeyId", copy_request)

    def test_instance_records_its_target_region(self):
        with tempfile.TemporaryDirectory() as directory:
            filename = Path(directory) / 'case-1.json'
            add_to_disk(
                str(filename),
                'case-1',
                'create_complete',
                1,
                [],
                [],
                {},
                region='eu-west-1',
            )

            with filename.open(encoding='utf-8') as instance_file:
                instance = json.load(instance_file)

        self.assertEqual(instance['region'], 'eu-west-1')


if __name__ == "__main__":
    unittest.main()
