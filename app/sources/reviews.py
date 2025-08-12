from typing import Optional
from duckduckgo_search import DDGS
import trafilatura


async def summarize_public_reviews(company_title: str) -> Optional[str]:
    query = f"{company_title} Glassdoor reviews"
    try:
        with DDGS() as ddgs:
            results = list(ddgs.text(query, max_results=3))
    except Exception:
        results = []

    snippets = []
    for r in results:
        url = r.get("link")
        if not url:
            continue
        try:
            downloaded = trafilatura.fetch_url(url)
            if not downloaded:
                continue
            text = trafilatura.extract(downloaded, include_comments=False, include_formatting=False)
            if text:
                snippets.append(text[:600])
        except Exception:
            continue

    if not snippets:
        return None

    combined = "\n\n".join(snippets)
    return ("Public reviews (e.g., Glassdoor/Indeed) highlight themes; treat as indicative, not definitive.\n" + combined[:1500]).strip()