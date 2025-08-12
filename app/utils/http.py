import httpx
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type


class HttpError(Exception):
    pass


@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=0.5, max=6),
       retry=retry_if_exception_type(HttpError))
async def fetch_text(url: str, timeout_seconds: float = 10.0, headers: dict | None = None) -> str:
    async with httpx.AsyncClient(timeout=timeout_seconds, follow_redirects=True, headers=headers) as client:
        resp = await client.get(url)
        if resp.status_code >= 400:
            raise HttpError(f"HTTP {resp.status_code} for {url}")
        return resp.text


async def fetch_json(url: str, timeout_seconds: float = 10.0, headers: dict | None = None) -> dict:
    async with httpx.AsyncClient(timeout=timeout_seconds, follow_redirects=True, headers=headers) as client:
        resp = await client.get(url)
        resp.raise_for_status()
        return resp.json()