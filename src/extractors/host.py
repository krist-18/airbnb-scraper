thon
from __future__ import annotations

from typing import Dict, List, Optional
from bs4 import BeautifulSoup  # type: ignore

def extract_host(soup: BeautifulSoup) -> Optional[Dict]:
    """
    Expect structure:

      <div class="host" data-superhost="true">
        <span class="host-name">Alice</span>
        <ul class="host-badges"><li>Superhost</li></ul>
        <ul class="host-languages"><li>English</li><li>Spanish</li></ul>
        <time class="host-joined" datetime="2020-05-01">Joined May 2020</time>
      </div>
    """
    root = soup.select_one(".host")
    if not root:
        return None

    name = (root.select_one(".host-name") or {}).get_text(strip=True) if root.select_one(".host-name") else None
    badges = [li.get_text(strip=True) for li in root.select(".host-badges li")]
    languages = [li.get_text(strip=True) for li in root.select(".host-languages li")]
    joined = root.select_one(".host-joined")["datetime"] if root.select_one(".host-joined") and root.select_one(".host-joined").has_attr("datetime") else None
    superhost = root.get("data-superhost", "false").lower() == "true"

    return {
        "name": name,
        "badges": [b for b in badges if b],
        "languages": [l for l in languages if l],
        "joined": joined,
        "is_superhost": superhost,
    }