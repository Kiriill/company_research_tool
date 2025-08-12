from dataclasses import dataclass, field
from typing import List
import re
import wikipedia
from bs4 import BeautifulSoup
from ..utils.http import fetch_text


@dataclass
class Overview:
    company_title: str
    slug: str | None = None
    summary: str | None = None
    history: str | None = None
    leaders: List[str] = field(default_factory=list)
    products: List[str] = field(default_factory=list)
    industry: str | None = None
    location: str | None = None
    founded: str | None = None
    employees: str | None = None
    website: str | None = None
    logo_url: str | None = None
    strategy: str | None = None
    peers: List[str] = field(default_factory=list)
    differentiation: str | None = None
    values: str | None = None
    sources: List[str] = field(default_factory=list)


def _slugify(title: str) -> str:
    return re.sub(r"[^a-z0-9-]", "", title.lower().replace(" ", "-"))


async def _fetch_infobox(title: str) -> dict:
    url = f"https://en.wikipedia.org/wiki/{title.replace(' ', '_')}"
    html = await fetch_text(url)
    soup = BeautifulSoup(html, "lxml")
    infobox = soup.select_one("table.infobox.vcard, table.infobox")
    data = {}
    if not infobox:
        return data
    for row in infobox.select("tr"):
        header = row.find("th")
        cell = row.find("td")
        if not header or not cell:
            continue
        key = header.get_text(strip=True).lower()
        val = cell.get_text(" ", strip=True)
        data[key] = val
        if key in {"website"}:
            link = cell.find("a")
            if link and link.get("href", "").startswith("http"):
                data["website_url"] = link.get("href")
        if key in {"logo"}:
            img = cell.find("img")
            if img and img.get("src"):
                data["logo_url"] = ("https:" + img.get("src")) if img.get("src").startswith("//") else img.get("src")
    return data


def _extract_list_from_section(text: str) -> List[str]:
    items = []
    for line in text.splitlines():
        if line.strip().startswith(('- ', '* ')):
            items.append(line.strip()[2:].strip())
    return items


async def get_company_overview(title: str) -> Overview:
    # Wikipedia summary
    try:
        page = wikipedia.page(title, auto_suggest=False)
    except Exception:
        try:
            # fallback with auto suggest
            page = wikipedia.page(title, auto_suggest=True)
        except Exception:
            page = None

    summary = page.summary if page and getattr(page, 'summary', None) else None
    url = page.url if page and getattr(page, 'url', None) else f"https://en.wikipedia.org/wiki/{title.replace(' ', '_')}"

    # Infobox parse
    infobox = await _fetch_infobox(title)

    # Heuristic sections from summary
    history = None
    strategy = None
    values = None
    leaders: List[str] = []
    products: List[str] = []

    # Attempt to parse leaders and products from infobox fields
    for key, field_names in {
        "leaders": ["key people", "founders", "founder", "owner"],
        "products": ["products", "services"],
    }.items():
        for fname in field_names:
            if fname in infobox:
                raw = infobox[fname]
                split = re.split(r"[,\n]", raw)
                values_list = [s.strip() for s in split if s.strip()]
                if key == "leaders":
                    leaders.extend(values_list)
                else:
                    products.extend(values_list)

    industry = None
    for fname in ["industry", "type", "genre"]:
        if fname in infobox:
            industry = infobox[fname]
            break

    location = None
    for fname in ["headquarters", "headquarters location", "based in", "located in"]:
        if fname in infobox:
            location = infobox[fname]
            break

    overview = Overview(
        company_title=page.title if page else title,
        slug=_slugify(page.title if page else title),
        summary=summary,
        history=history,
        leaders=list(dict.fromkeys(leaders))[:10],
        products=list(dict.fromkeys(products))[:12],
        industry=industry,
        location=location,
        founded=infobox.get("founded") if infobox else None,
        employees=infobox.get("number of employees") if infobox else None,
        website=infobox.get("website_url") or infobox.get("website"),
        logo_url=infobox.get("logo_url"),
        strategy=strategy,
        peers=[],
        differentiation=None,
        values=values,
        sources=[url],
    )

    return overview