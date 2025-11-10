thon
from __future__ import annotations

import hashlib
import urllib.parse
from typing import List, Optional

def _canon(s: Optional[str]) -> str:
    return (s or "").strip()

def build_search_urls(
    *,
    location: str,
    checkin: Optional[str] = None,
    checkout: Optional[str] = None,
    adults: int = 1,
    min_price: Optional[int] = None,
    max_price: Optional[int] = None,
    page_count: int = 1,
    currency: str = "USD",
) -> List[str]:
    """
    Create deterministic, non-networked Airbnb search URLs for reference.
    These are not fetched by this project; they are included in output metadata
    for reproducibility and audit trails.

    Args mirror common filter controls.
    """
    base = "https://www.airbnb.com/s"
    q_loc = urllib.parse.quote_plus(_canon(location))
    params = {
        "query": _canon(location),
        "adults": str(max(1, adults)),
        "price_min": str(min_price) if min_price is not None else None,
        "price_max": str(max_price) if max_price is not None else None,
        "checkin": checkin,
        "checkout": checkout,
        "display_currency": currency or "USD",
    }

    urls: List[str] = []
    for page in range(1, max(1, page_count) + 1):
        qp = {k: v for k, v in params.items() if v not in (None, "")}
        qp["page"] = str(page)
        qp_encoded = urllib.parse.urlencode(qp)
        url = f"{base}/{q_loc}/homes?{qp_encoded}"
        # Add a deterministic tracking fragment
        frag = hashlib.sha1(url.encode("utf-8")).hexdigest()[:8]
        urls.append(f"{url}#bb={frag}")
    return urls