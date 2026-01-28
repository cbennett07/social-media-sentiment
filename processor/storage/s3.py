import boto3
from botocore.exceptions import ClientError
from processor.storage.base import ObjectStorage


class S3ObjectStorage(ObjectStorage):
    """
    S3-compatible object storage.

    Works with AWS S3, GCS (in interoperability mode), MinIO, etc.
    """

    def __init__(
        self,
        bucket: str,
        endpoint_url: str | None = None,
        aws_access_key_id: str | None = None,
        aws_secret_access_key: str | None = None,
        region_name: str = "us-east-1"
    ):
        self.bucket = bucket
        self.endpoint_url = endpoint_url

        # Build client config
        client_kwargs = {"region_name": region_name}

        if endpoint_url:
            client_kwargs["endpoint_url"] = endpoint_url

        if aws_access_key_id and aws_secret_access_key:
            client_kwargs["aws_access_key_id"] = aws_access_key_id
            client_kwargs["aws_secret_access_key"] = aws_secret_access_key

        self.client = boto3.client("s3", **client_kwargs)

    def put(self, key: str, data: str | bytes) -> str:
        if isinstance(data, str):
            data = data.encode("utf-8")

        self.client.put_object(
            Bucket=self.bucket,
            Key=key,
            Body=data
        )

        if self.endpoint_url:
            return f"{self.endpoint_url}/{self.bucket}/{key}"
        return f"s3://{self.bucket}/{key}"

    def get(self, key: str) -> bytes:
        response = self.client.get_object(
            Bucket=self.bucket,
            Key=key
        )
        return response["Body"].read()

    def exists(self, key: str) -> bool:
        try:
            self.client.head_object(Bucket=self.bucket, Key=key)
            return True
        except ClientError as e:
            if e.response["Error"]["Code"] == "404":
                return False
            raise

    def health_check(self) -> bool:
        try:
            self.client.head_bucket(Bucket=self.bucket)
            return True
        except Exception:
            return False
