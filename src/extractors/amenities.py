thon
from __future__ import annotations

from typing import List
from bs4 import BeautifulSoup  # type: ignore

def extract_amenities(soup: BeautifulSoup) -> List[str]:
    """
    Extract amenities from a simple list structure like:
      <ul class="amenities">
        <li>Wifi</li>
        <li>Kitchen</li>
      </ul>
    """
    items = []
    for li in soup.select(".amenities li"):
        text = li.get_text(strip=True)
        if text:
            items.append(text)
    # Fallback: data-amenity attributes
    if not items:
        items = [el["data-amenity"] for el in soup.select("[data-amenity]") if el.has_attr("data-amenity")]
    return items