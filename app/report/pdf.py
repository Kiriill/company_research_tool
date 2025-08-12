from jinja2 import Environment, FileSystemLoader, select_autoescape
from weasyprint import HTML, CSS
from ..models import ReportData
import os


def _env() -> Environment:
    return Environment(
        loader=FileSystemLoader("app/report/templates"),
        autoescape=select_autoescape(["html", "xml"]),
        trim_blocks=True,
        lstrip_blocks=True,
    )


def render_report_html(report: ReportData) -> str:
    env = _env()
    template = env.get_template("report.html.j2")
    with open("app/report/styles/report.css", "r", encoding="utf-8") as f:
        css_text = f.read()
    return template.render(report=report, css_inline=css_text)


async def html_to_pdf(html: str) -> bytes:
    pdf = HTML(string=html, base_url=os.getcwd()).write_pdf(stylesheets=[CSS(string="")])
    return pdf