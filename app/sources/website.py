from typing import List, Dict
import trafilatura


async def extract_from_urls(urls: List[str]) -> Dict[str, str]:
    if not urls:
        return {}
    results: Dict[str, str] = {}
    for url in urls:
        try:
            downloaded = trafilatura.fetch_url(url)
            if not downloaded:
                continue
            text = trafilatura.extract(downloaded, include_comments=False, include_formatting=False)
            if not text:
                continue
            lower = text.lower()
            if "our values" in lower or "company values" in lower:
                results.setdefault("values", text[:2000])
            if "mission" in lower or "vision" in lower or "purpose" in lower:
                prev = results.get("values", "")
                combined = (prev + "\n\n" + text[:2000]).strip()
                results["values"] = combined
            if "history" in lower or "our story" in lower:
                results.setdefault("history", text[:2500])
        except Exception:
            continue
    return results