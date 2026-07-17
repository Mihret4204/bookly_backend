import os
import uuid
from pathlib import Path
from urllib.parse import quote, unquote, urlparse

import httpx
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parents[1]
load_dotenv(BASE_DIR / ".env", override=False)


class SupabaseStorageClient:
    def __init__(self) -> None:
        self.base_url = (os.getenv("SUPABASE_URL") or "").rstrip("/")
        self.service_role_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY") or ""
        self.bucket = os.getenv("SUPABASE_STORAGE_BUCKET") or "book-covers"

    def _headers(self) -> dict[str, str]:
        return {
            "Authorization": f"Bearer {self.service_role_key}",
            "apikey": self.service_role_key,
            "x-upsert": "true",
        }

    def _build_public_url(self, object_path: str) -> str:
        encoded_path = quote(object_path, safe="/")
        return f"{self.base_url}/storage/v1/object/public/{self.bucket}/{encoded_path}"

    def _extract_object_path(self, public_url: str) -> str | None:
        if not public_url.startswith(self.base_url):
            return None

        parsed = urlparse(public_url)
        prefix = "/storage/v1/object/public/"
        if not parsed.path.startswith(prefix):
            return None

        remainder = parsed.path[len(prefix):]
        bucket, sep, object_path = remainder.partition("/")
        if not sep or bucket != self.bucket:
            return None
        return unquote(object_path)

    async def upload_file(self, file_bytes: bytes, filename: str, content_type: str, book_uid: uuid.UUID) -> str:
        if not self.base_url or not self.service_role_key:
            raise RuntimeError("Supabase storage is not configured")

        extension = Path(filename).suffix.lower() or ".jpg"
        object_path = f"books/{book_uid}/{uuid.uuid4().hex}{extension}"

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{self.base_url}/storage/v1/object/{self.bucket}/{object_path}",
                headers={**self._headers(), "Content-Type": content_type},
                content=file_bytes,
            )

        if response.status_code not in {200, 201}:
            raise RuntimeError(f"Supabase upload failed: {response.status_code} {response.text}")

        return self._build_public_url(object_path)

    async def delete_file(self, public_url: str) -> None:
        if not public_url:
            return

        object_path = self._extract_object_path(public_url)
        if not object_path:
            return

        async with httpx.AsyncClient(timeout=30.0) as client:
            await client.delete(
                f"{self.base_url}/storage/v1/object/{self.bucket}/{quote(object_path, safe='/')}",
                headers=self._headers(),
            )


supabase_storage_client = SupabaseStorageClient()
