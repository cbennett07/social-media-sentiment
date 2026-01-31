from google.cloud import storage
from google.cloud.exceptions import NotFound
from processor.storage.base import ObjectStorage


class GCSObjectStorage(ObjectStorage):
    """
    Google Cloud Storage implementation.

    Uses Application Default Credentials when running on GCP.
    """

    def __init__(self, bucket: str):
        self.bucket_name = bucket
        self.client = storage.Client()
        self.bucket = self.client.bucket(bucket)

    def put(self, key: str, data: str | bytes) -> str:
        if isinstance(data, str):
            data = data.encode("utf-8")

        blob = self.bucket.blob(key)
        blob.upload_from_string(data, content_type="application/json")

        return f"gs://{self.bucket_name}/{key}"

    def get(self, key: str) -> bytes:
        blob = self.bucket.blob(key)
        return blob.download_as_bytes()

    def exists(self, key: str) -> bool:
        blob = self.bucket.blob(key)
        return blob.exists()

    def health_check(self) -> bool:
        try:
            self.bucket.reload()
            return True
        except Exception:
            return False
