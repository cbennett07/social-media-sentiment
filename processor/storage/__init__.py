from processor.storage.base import ObjectStorage
from processor.storage.s3 import S3ObjectStorage
from processor.storage.gcs import GCSObjectStorage

__all__ = ["ObjectStorage", "S3ObjectStorage", "GCSObjectStorage"]
