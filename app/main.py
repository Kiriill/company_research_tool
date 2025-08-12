from fastapi import FastAPI, Request, Form, HTTPException
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from typing import List, Optional
from .config import settings
from .services.resolve_company import search_companies
from .services.assemble_report import assemble_company_report
from .report.pdf import render_report_html, html_to_pdf
import io

app = FastAPI(title="Company Research Report Generator")

templates = Jinja2Templates(directory="app/report/templates")
app.mount("/static", StaticFiles(directory="app/report/styles"), name="static")


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("form.html.j2", {"request": request, "step": "input"})


@app.post("/resolve", response_class=HTMLResponse)
async def resolve(request: Request,
                  company_name: str = Form(...),
                  expected_pages: int = Form(4),
                  interests: Optional[str] = Form(""),
                  reference_urls: Optional[str] = Form("")):
    candidates = await search_companies(company_name)
    if not candidates:
        return templates.TemplateResponse(
            "form.html.j2",
            {"request": request, "step": "input", "error": "No matches found. Try a different name.",
             "company_name": company_name, "expected_pages": expected_pages,
             "interests": interests, "reference_urls": reference_urls}
        )

    # If single high-confidence match, proceed directly
    if len(candidates) == 1 and candidates[0]["score"] >= 0.9:
        selection = candidates[0]
        report_data = await assemble_company_report(
            company_title=selection["title"],
            expected_pages=expected_pages,
            interests=interests,
            reference_urls=[u.strip() for u in (reference_urls or "").splitlines() if u.strip()],
        )
        html = render_report_html(report_data)
        pdf_bytes = await html_to_pdf(html)
        return StreamingResponse(io.BytesIO(pdf_bytes), media_type="application/pdf",
                                 headers={"Content-Disposition": f"attachment; filename={selection['slug']}.pdf"})

    # Otherwise show disambiguation choices
    return templates.TemplateResponse(
        "form.html.j2",
        {
            "request": request,
            "step": "disambiguate",
            "candidates": candidates,
            "company_name": company_name,
            "expected_pages": expected_pages,
            "interests": interests,
            "reference_urls": reference_urls,
        }
    )


@app.post("/generate")
async def generate(request: Request,
                   selected_title: str = Form(...),
                   expected_pages: int = Form(4),
                   interests: Optional[str] = Form(""),
                   reference_urls: Optional[str] = Form("")):
    report_data = await assemble_company_report(
        company_title=selected_title,
        expected_pages=expected_pages,
        interests=interests,
        reference_urls=[u.strip() for u in (reference_urls or "").splitlines() if u.strip()],
    )
    html = render_report_html(report_data)
    pdf_bytes = await html_to_pdf(html)
    safe_slug = report_data.slug or selected_title.lower().replace(" ", "-")
    return StreamingResponse(io.BytesIO(pdf_bytes), media_type="application/pdf",
                             headers={"Content-Disposition": f"attachment; filename={safe_slug}.pdf"})