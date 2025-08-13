# Company Research Report Generator

A FastAPI-based web service that automates company research and generates a consulting-style formatted PDF report. Users provide a company name, confirm the specific company in a follow-up step, optionally set desired length (pages), topics of interest, and reference URLs (e.g., company site, job posting). The service compiles a concise history, leadership, key products and revenue streams, expected revenue (when available), strategy and outlook, peers and competitive differentiation, company values, and a summary of public reviews (e.g., Glassdoor) into a polished PDF.

## Features
- Two-step input flow: company name → disambiguation/confirmation → generate
- Modular research sources:
  - Wikipedia and Wikidata for baseline facts and structure
  - Optional crawling of provided URLs for values, leadership, and product info
  - Optional APIs when keys present (e.g., News, LLM summarization)
- Clean HTML + CSS report styled for a consulting look, exported to PDF via WeasyPrint
- Designed for easy deployment on Render (Docker)

## Tech Stack
- FastAPI + Jinja2
- HTTPX for async HTTP
- WeasyPrint for PDF generation from HTML/CSS
- Optional: OpenAI for enhanced synthesis (if `OPENAI_API_KEY` provided)

## Local Development

### Prerequisites
- Docker and Docker Compose

### Run locally
```bash
# From the repository root
docker build -t company-research:dev .
docker run --rm -it -p 8000:8000 \
  -e OPENAI_API_KEY=your_key_if_any \
  -e NEWSAPI_KEY=optional_news_api_key \
  company-research:dev
```

Then open `http://localhost:8000`.

## Environment Variables
- `OPENAI_API_KEY` (optional): Enables LLM-based synthesis for higher-quality narrative sections.
- `NEWSAPI_KEY` (optional): Enables recent news highlights.

The app works without these keys using public sources and heuristic summarization.

## Deploy to Render

This repository includes a `render.yaml` for one-click deployment using a Docker web service. In Render:
- Create a new Web Service
- Connect your repo
- Render will detect `render.yaml`
- Set environment variables as needed

Once deployed, open the service URL and use the form to generate PDFs.

## Project Structure
```
app/
  main.py                # FastAPI app and routes
  config.py              # Settings (env vars)
  models.py              # Pydantic models for inputs and report data
  utils/http.py          # Robust async HTTP client with retries
  services/
    resolve_company.py   # Disambiguation via Wikipedia search
    assemble_report.py   # Orchestrates data collection and shaping
  sources/
    wikipedia.py         # Wikipedia summaries and pages
    wikidata.py          # Wikidata SPARQL for structured fields
    website.py           # Lightweight site crawling and extraction
    finance.py           # Optional finance signals (e.g., revenue)
    news.py              # Optional news (requires key)
    reviews.py           # Public reviews (best-effort)
  report/
    pdf.py               # HTML→PDF conversion (WeasyPrint)
    templates/
      form.html.j2       # Initial form and disambiguation
      report.html.j2     # Final report template
    styles/
      report.css         # Consulting-style visual design
Dockerfile
render.yaml
requirements.txt
README.md
```

## Notes
- The output aims for factual accuracy but depends on public sources and may vary by company.
- Some sites block scraping. The app degrades gracefully and cites sources used.
- Public/private companies vary in data availability. Financials are best-effort.
