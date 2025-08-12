from typing import Optional
import os
import textwrap
import httpx
from ..config import settings


async def summarize_recent_news(company_title: str) -> Optional[str]:
    if not settings.newsapi_key:
        return None
    url = "https://newsapi.org/v2/everything"
    params = {
        "q": company_title,
        "language": "en",
        "sortBy": "relevancy",
        "pageSize": 5,
        "apiKey": settings.newsapi_key,
    }
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get(url, params=params)
            resp.raise_for_status()
            data = resp.json()
    except Exception:
        return None

    articles = data.get("articles", [])
    if not articles:
        return None

    bullets = []
    for a in articles[:5]:
        title = a.get("title")
        source = a.get("source", {}).get("name", "")
        if title:
            bullets.append(f"- {title} ({source})")

    if not bullets:
        return None

    return "Recent news items may indicate near-term focus areas and risks:\n" + "\n".join(bullets)