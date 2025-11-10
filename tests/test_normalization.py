thon
from __future__ import annotations

import json
import os
import sys

import pytest  # type: ignore

# Add src/ to path for imports
ROOT = os.path.dirname(os.path.dirname(__file__))
SRC = os.path.join(ROOT, "src")
if SRC not in sys.path:
    sys.path.insert(0, SRC)

from listing_parser import parse_listing_detail_html  # type: ignore

def read_fixture() -> str:
    path = os.path.join(ROOT, "tests", "fixtures", "listing_detail.html")
    with open(path, "r", encoding="utf-8") as f:
        return f.read()

def test_parse_listing_basic_fields():
    html = read_fixture()
    listing = parse_listing_detail_html(html)

    assert listing.airbnbId == 53169062
    assert listing.name == "PLAYA AMANECER"
    assert listing.numberOfGuests == 4
    assert listing.location.lat == pytest.approx(36.716, abs=1e-6)
    assert listing.location.lng == pytest.approx(-4.203, abs=1e-6)

    assert listing.pricing.rate.amount == 16216
    assert listing.currency == "USD"

    assert "Wifi" in listing.amenities
    assert listing.primaryHost is not None
    assert listing.primaryHost.name == "Chris Host"
    assert listing.primaryHost.is_superhost is True

    assert listing.reviews and listing.reviews[0].author.firstName == "Chris"
    assert listing.photos and listing.photos[0].startswith("https://")

def test_dump_json_roundtrip():
    html = read_fixture()
    listing = parse_listing_detail_html(html)
    dumped = listing.model_dump(by_alias=True, exclude_none=True)
    # Ensure JSON serializable
    json.dumps(dumped)
    # Sanity keys
    for k in ("url", "airbnbId", "name", "pricing", "amenities"):
        assert k in dumped