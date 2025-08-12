from typing import Optional
import re
import yfinance as yf


async def estimate_revenue(company_title: str, overview) -> Optional[str]:
    # Try naive ticker inference: handle well-known suffixes like (company) or plain title symbol
    # This is intentionally conservative to avoid wrong matches
    possible = []
    cleaned = re.sub(r"[^A-Za-z0-9 ]", "", company_title)
    tokens = cleaned.split()
    if tokens and len(tokens) <= 3:
        sym = "".join(t[0] for t in tokens).upper()
        if 1 <= len(sym) <= 5:
            possible.append(sym)
    # Also try exact uppercase token
    if len(tokens) == 1 and 1 <= len(tokens[0]) <= 5:
        possible.append(tokens[0].upper())

    for ticker in possible:
        try:
            t = yf.Ticker(ticker)
            fin = t.financials
            if fin is not None and not fin.empty:
                if "Total Revenue" in fin.index:
                    revenue_series = fin.loc["Total Revenue"].dropna()
                else:
                    revenue_series = fin.iloc[0].dropna()
                if not revenue_series.empty:
                    latest = float(revenue_series.iloc[0])
                    if latest >= 1e9:
                        return f"~${latest/1e9:.1f}B (est.)"
                    elif latest >= 1e6:
                        return f"~${latest/1e6:.0f}M (est.)"
                    else:
                        return f"~${latest:,.0f} (est.)"
        except Exception:
            continue

    # fallback: unknown
    return None