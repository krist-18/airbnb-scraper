thon
from __future__ import annotations

from typing import Dict, List
from bs4 import BeautifulSoup  # type: ignore

def extract_reviews(soup: BeautifulSoup) -> List[Dict]:
    """
    Expect structure:

      <div class="reviews">
        <article class="review" data-rating="5" data-created-at="2022-07-16T11:48:15Z">
          <span class="author" data-id="159332062">Chris</span>
          <p class="content">Great stay!</p>
        </article>
      </div>
    """
    out: List[Dict] = []
    for art in soup.select(".reviews .review"):
        rating = None
        if art.has_attr("data-rating"):
            try:
                rating = float(art["data-rating"])
            except Exception:
                rating = None
        created_at = art.get("data-created-at")
        author_el = art.select_one(".author")
        author = {
            "firstName": author_el.get_text(strip=True) if author_el else None,
            "id": author_el["data-id"] if author_el and author_el.has_attr("data-id") else None,
        }
        text_el = art.select_one(".content")
        out.append(
            {
                "author": author,
                "comments": text_el.get_text(strip=True) if text_el else None,
                "createdAt": created_at,
                "rating": rating,
            }
        )
    return out