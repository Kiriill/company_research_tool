from typing import List, Optional
from ..models import ReportData, ReportSection
from ..config import settings
from ..sources.llm import build_report_with_llm
from ..sources.wikipedia import get_company_overview
from ..sources.website import extract_from_urls
from ..sources.finance import estimate_revenue
from ..sources.news import summarize_recent_news
from ..sources.reviews import summarize_public_reviews


async def assemble_company_report(company_title: str,
                                 expected_pages: int = 4,
                                 interests: Optional[str] = None,
                                 reference_urls: Optional[List[str]] = None) -> ReportData:
    # Prefer LLM synthesis when available
    if settings.openai_api_key:
        llm_report = await build_report_with_llm(company_title, expected_pages, interests, reference_urls)
        if llm_report:
            return llm_report

    # Fallback path using public sources without LLM
    overview = await get_company_overview(company_title)

    # Enrich from provided URLs
    url_insights = await extract_from_urls(reference_urls or [])

    # Finance signals
    revenue = await estimate_revenue(company_title, overview)

    # News and outlook
    outlook = await summarize_recent_news(company_title)

    # Reviews
    reviews = await summarize_public_reviews(company_title)

    sections: List[ReportSection] = []

    # Prefer overview summary as intro if present
    if overview.summary:
        sections.append(ReportSection(title="Executive Summary", content=overview.summary, sources=overview.sources))

    history_text = overview.history or url_insights.get("history", "")
    if history_text:
        sections.append(ReportSection(title="Brief History", content=history_text, sources=overview.sources))

    strategy_text = (overview.strategy or "")
    if outlook:
        strategy_text = (strategy_text + "\n\n" + outlook).strip()
    if strategy_text:
        sections.append(ReportSection(title="Strategy and Outlook", content=strategy_text, sources=overview.sources))

    products_text = "\n".join(f"- {p}" for p in overview.products)
    if products_text or revenue:
        content = (products_text + (f"\n\nEstimated revenue: {revenue}" if revenue else "")).strip()
        sections.append(ReportSection(title="Key Products and Revenue Streams", content=content, sources=overview.sources))

    peers_text = "\n".join(f"- {p}" for p in overview.peers)
    if peers_text or overview.differentiation:
        content = (peers_text + (f"\n\nDifferentiation: {overview.differentiation}" if overview.differentiation else "")).strip()
        sections.append(ReportSection(title="Peers and Competitive Positioning", content=content, sources=overview.sources))

    values_text = url_insights.get("values") or overview.values
    if values_text:
        sections.append(ReportSection(title="Values and Culture", content=values_text, sources=overview.sources))

    if reviews:
        sections.append(ReportSection(title="Employee Reviews (Public)", content=reviews, sources=overview.sources))

    if interests:
        sections.append(ReportSection(title="Topics of Interest (User)", content=interests.strip(), sources=[]))

    report = ReportData(
        company_title=overview.company_title,
        slug=overview.slug,
        logo_url=overview.logo_url,
        location=overview.location,
        industry=overview.industry,
        founded=overview.founded,
        employees=overview.employees,
        website=overview.website,
        leaders=overview.leaders,
        products=overview.products,
        revenue=revenue,
        sections=sections,
        peers=overview.peers,
        differentiation=overview.differentiation,
        references=overview.sources,
        meta={"expected_pages": expected_pages}
    )

    return report