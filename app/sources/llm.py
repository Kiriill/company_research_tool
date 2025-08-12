from typing import List, Optional, Dict, Any
import json
from duckduckgo_search import DDGS
import trafilatura
from openai import OpenAI
from ..config import settings
from ..models import ReportData, ReportSection


def _search_urls(company_title: str) -> List[str]:
    queries = [
        company_title,
        f"{company_title} about",
        f"{company_title} leadership",
        f"{company_title} products",
        f"{company_title} revenue",
        f"{company_title} strategy",
        f"{company_title} values",
        f"{company_title} Glassdoor",
    ]
    urls: List[str] = []
    try:
        with DDGS() as ddgs:
            for q in queries:
                for r in ddgs.text(q, max_results=3):
                    link = r.get("link")
                    if link and link.startswith("http"):
                        urls.append(link)
    except Exception:
        pass
    # de-duplicate while preserving order
    seen = set()
    deduped = []
    for u in urls:
        if u in seen:
            continue
        seen.add(u)
        deduped.append(u)
    return deduped[:12]


def _load_pages(urls: List[str]) -> List[Dict[str, str]]:
    docs = []
    for u in urls:
        try:
            downloaded = trafilatura.fetch_url(u)
            if not downloaded:
                continue
            text = trafilatura.extract(downloaded, include_comments=False, include_formatting=False)
            if not text:
                continue
            docs.append({"url": u, "content": text[:6000]})
        except Exception:
            continue
    return docs


def _build_prompt(company_title: str, interests: Optional[str], expected_pages: int, docs: List[Dict[str, str]]) -> List[Dict[str, str]]:
    system = (
        "You are a senior consulting analyst. Synthesize concise, accurate company research in a clear, executive style. "
        "Be factual and cite which sources informed which sections by including a sources list."
    )
    user = {
        "company": company_title,
        "expected_pages": expected_pages,
        "interests": interests or "",
        "documents": docs[:10],
        "output_format": {
            "company_title": "string",
            "location": "string?",
            "industry": "string?",
            "founded": "string?",
            "employees": "string?",
            "website": "string?",
            "leaders": ["string"],
            "products": ["string"],
            "revenue": "string?",
            "sections": [
                {
                    "title": "string",
                    "content": "markdown string",
                    "sources": ["string"],
                }
            ],
            "peers": ["string"],
            "differentiation": "string?",
            "references": ["string"],
        },
        "section_guidance": [
            "Brief history",
            "Strategy and future outlook (growth areas)",
            "Key products and revenue streams",
            "Peers and competitive differentiation",
            "Values and culture",
            "Public reviews summary (e.g., Glassdoor)",
        ],
        "style": "Terse, structured, McKinsey-style; avoid fluff."
    }
    return [
        {"role": "system", "content": system},
        {"role": "user", "content": json.dumps(user)},
    ]


def _to_report_data(payload: Dict[str, Any]) -> ReportData:
    sections = [
        ReportSection(
            title=s.get("title", ""),
            content=s.get("content", ""),
            sources=s.get("sources", []) or [],
        )
        for s in payload.get("sections", [])
    ]
    return ReportData(
        company_title=payload.get("company_title") or payload.get("title") or "",
        slug=None,
        logo_url=None,
        location=payload.get("location"),
        industry=payload.get("industry"),
        founded=payload.get("founded"),
        employees=payload.get("employees"),
        website=payload.get("website"),
        leaders=payload.get("leaders", []) or [],
        products=payload.get("products", []) or [],
        revenue=payload.get("revenue"),
        sections=sections,
        peers=payload.get("peers", []) or [],
        differentiation=payload.get("differentiation"),
        references=payload.get("references", []) or [],
        meta={},
    )


async def build_report_with_llm(company_title: str,
                                expected_pages: int = 4,
                                interests: Optional[str] = None,
                                reference_urls: Optional[List[str]] = None) -> Optional[ReportData]:
    if not settings.openai_api_key:
        return None

    # gather URLs
    urls = []
    if reference_urls:
        urls.extend(reference_urls)
    urls.extend(_search_urls(company_title))
    # dedupe
    seen = set()
    unique_urls = []
    for u in urls:
        if u not in seen:
            seen.add(u)
            unique_urls.append(u)

    docs = _load_pages(unique_urls[:12])
    if not docs:
        return None

    client = OpenAI(api_key=settings.openai_api_key)
    messages = _build_prompt(company_title, interests, expected_pages, docs)

    try:
        completion = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            response_format={"type": "json_object"},
            temperature=0.2,
        )
        content = completion.choices[0].message.content or "{}"
        payload = json.loads(content)
    except Exception:
        return None

    try:
        return _to_report_data(payload)
    except Exception:
        return None