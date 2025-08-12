from typing import List, Dict
import re
import wikipedia


def _slugify(title: str) -> str:
    return re.sub(r"[^a-z0-9-]", "", title.lower().replace(" ", "-"))


async def search_companies(query: str) -> List[Dict]:
    try:
        results = wikipedia.search(query, results=8, suggestion=False)
    except Exception:
        results = []

    candidates: List[Dict] = []
    for title in results:
        score = 1.0 if title.lower() == query.lower() else (0.9 if query.lower() in title.lower() else 0.6)
        url = f"https://en.wikipedia.org/wiki/{title.replace(' ', '_')}"
        candidates.append({
            "title": title,
            "description": "Wikipedia",
            "url": url,
            "score": score,
            "slug": _slugify(title),
        })

    # Deduplicate by title
    seen = set()
    uniq = []
    for c in candidates:
        if c["title"].lower() in seen:
            continue
        seen.add(c["title"].lower())
        uniq.append(c)

    return uniq