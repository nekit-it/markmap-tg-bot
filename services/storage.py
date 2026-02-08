# services/storage.py
from typing import Dict, List, Optional
from uuid import uuid4
from config import YC_ACCESS_KEY_ID, YC_SECRET_ACCESS_KEY, YC_BUCKET_NAME, YC_S3_ENDPOINT, YC_WEBSITE_HOST
import boto3

MAP_STORAGE: Dict[int, List[dict]] = {}


def save_map(
    user_id: int,
    title: str,
    depth: str,
    structure: list,
    markmap: str,
    url: Optional[str] = None,
) -> str:
    map_id = str(uuid4())

    MAP_STORAGE.setdefault(user_id, []).append(
        {
            "id": map_id,
            "title": title,
            "depth": depth,
            "structure": structure,
            "markmap": markmap,
            "url": url,
        }
    )

    return map_id

def upload_to_s3(md_content: str, filename: str) -> str:
    """Uploads Markdown to S3 and returns path for Mini App"""
    session = boto3.session.Session(
        aws_access_key_id=YC_ACCESS_KEY_ID,
        aws_secret_access_key=YC_SECRET_ACCESS_KEY,
        region_name="ru-central1"
    )
    s3 = session.client(service_name="s3", endpoint_url=YC_S3_ENDPOINT)
    
    s3_key = f"generated_maps/{filename}"
    
    s3.put_object(
        Bucket=YC_BUCKET_NAME,
        Key=s3_key,
        Body=md_content.encode('utf-8'),
        ContentType='text/markdown; charset=utf-8'
    )
    
    return f"http://{YC_WEBSITE_HOST}/index.html?file={s3_key}"

def get_user_maps(user_id: int) -> List[dict]:
    return MAP_STORAGE.get(user_id, [])


def get_last_map(user_id: int) -> Optional[dict]:
    maps = MAP_STORAGE.get(user_id) or []
    return maps[-1] if maps else None


