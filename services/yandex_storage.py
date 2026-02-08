import os
import boto3
from botocore.client import Config
from botocore.exceptions import NoCredentialsError

from config import (
    YC_ACCESS_KEY_ID,
    YC_SECRET_ACCESS_KEY,
    YC_BUCKET_NAME,
    YC_S3_ENDPOINT,
    YC_WEBSITE_HOST,
)

_session = boto3.session.Session(
    aws_access_key_id=YC_ACCESS_KEY_ID,
    aws_secret_access_key=YC_SECRET_ACCESS_KEY,
    region_name="ru-central1",
)

_s3 = _session.resource(
    service_name="s3",
    endpoint_url=YC_S3_ENDPOINT,
    config=Config(signature_version="s3v4"),
)

def upload_map_html(local_path: str, object_key: str) -> str:
    """
    Загружает HTML-файл в Object Storage и возвращает публичный URL
    """
    if not os.path.isfile(local_path):
        raise FileNotFoundError(f"Файл не найден: {local_path}")

    bucket = _s3.Bucket(YC_BUCKET_NAME)
    
    try:
        bucket.upload_file(
            local_path,
            object_key,
            ExtraArgs={
                "ACL": "public-read", 
                "ContentType": "text/html; charset=utf-8",
                "CacheControl": "max-age=0" 
            },
        )
    except Exception as e:
        print(f"Ошибка загрузки в S3: {e}")
        raise e

    return f"https://{YC_WEBSITE_HOST}/{object_key}"
