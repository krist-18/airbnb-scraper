thon
from __future__ import annotations

import json
import os
import sys
from typing import Any, Dict, List, Optional

# Make sure we can import extractor modules without packages
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
EXTRACTORS_DIR = os.path.join(CURRENT_DIR, "extractors")
if CURRENT_DIR not in sys.path:
    sys.path.insert(0, CURRENT_DIR)
if EXTRACTORS_DIR not in sys.path:
    sys.path.insert(0, EXTRACTORS_DIR)

from bs4 import BeautifulSoup  # type: ignore
from pydantic import BaseModel, Field, field_validator

# local extractor helpers
from amenities import extract_amenities  # type: ignore
from host import extract_host  # type: ignore
from reviews import extract_reviews  # type: ignore

class Geo(BaseModel):
    lat: Optional[float] = None
    lng: Optional[float] = None

class Rate(BaseModel):
    amount: Optional[int] = None
    is_micros_accuracy: bool = False

class Pricing(BaseModel):
    rate: Rate = Field(default_factory=Rate)

class Author(BaseModel):
    firstName: Optional[str] = None
    id: Optional[str] = None

class Review(BaseModel):
    author: Optional[Author] = None
    comments: Optional[str] = None
    createdAt: Optional[str] = None
    rating: Optional[float] = None

class HostProfile(BaseModel):
    name: Optional[str] = None
    badges: List[str] = Field(default_factory=list)
    languages: List[str] = Field(default_factory=list)
    joined: Optional[str] = None
    is_superhost: Optional[bool] = None

class Listing(BaseModel):
    url: Optional[str] = None
    airbnbId: Optional[int] = None
    name: Optional[str] = None
    numberOfGuests: Optional[int] = None
    address: Optional[str] = None
    roomType: Optional[str] = None
    location: Geo = Field(default_factory=Geo)
    reviews: List[Review] = Field(default_factory=list)
    pricing: Pricing = Field(default_factory=Pricing)
    photos: List[str] = Field(default_factory=list)
    amenities: List[str] = Field(default_factory=list)
    city: Optional[str] = None
    country: Optional[str] = None
    bedrooms: Optional[str] = None
    bathroomLabel: Optional[str] = None
    bedLabel: Optional[str] = None
    bedroomLabel: Optional[str] = None
    license: Optional[str] = None
    listingRooms: Optional[Dict[str, Any]] = None
    primaryHost: Optional[HostProfile] = None
    roomTypeCategory: Optional[str] = None
    sectionedDescription: Optional[Dict[str, Any]] = None
    guestControls: Optional[Dict[str, Any]] = None
    minNights: Optional[int] = None
    maxNights: Optional[int] = None
    currency: Optional[str] = None
    monthChecked: Optional[int] = None
    yearChecked: Optional[int] = None
    meta: Optional[Dict[str, Any]] = None

    @field_validator("airbnbId", mode="before")
    @classmethod
    def _to_int(cls, v):
        try:
            return int(v) if v is not None else None
        except Exception:
            return None

    @field_validator("numberOfGuests", "minNights", "maxNights", mode="before")
    @classmethod
    def _to_int_opt(cls, v):
        try:
            return int(v) if v not in (None, "") else None
        except Exception:
            return None

def _text(el) -> Optional[str]:
    return el.get_text(strip=True) if el else None

def parse_listing_detail_html(html: str) -> Listing:
    """
    Parse a (fixture) Airbnb listing detail HTML into the unified schema.
    The parser expects semantic data attributes present in the fixture:
      - data-airbnb-id, data-lat, data-lng
      - data-currency on price container, price in cents via data-amount
    """
    soup = BeautifulSoup(html, "lxml")

    root = soup.select_one("[data-airbnb-id]")
    airbnb_id = int(root["data-airbnb-id"]) if root and root.has_attr("data-airbnb-id") else None

    # URL and title
    url = root["data-url"] if root and root.has_attr("data-url") else None
    title = _text(soup.select_one("h1.listing-title")) or _text(soup.select_one("meta[property='og:title']"))

    # Guests and labels
    guests_txt = _text(soup.select_one("[data-guests]"))
    number_of_guests = int(soup.select_one("[data-guests]")["data-guests"]) if soup.select_one("[data-guests]") else None

    address = _text(soup.select_one(".listing-address"))
    room_type = _text(soup.select_one("[data-room-type]"))

    # Geo
    lat = float(root["data-lat"]) if root and root.has_attr("data-lat") else None
    lng = float(root["data-lng"]) if root and root.has_attr("data-lng") else None

    # Pricing
    price_box = soup.select_one("[data-price]")
    amount = int(price_box["data-amount"]) if price_box and price_box.has_attr("data-amount") else None
    currency = price_box["data-currency"] if price_box and price_box.has_attr("data-currency") else None

    # City / Country (split address heuristic)
    city = soup.select_one("[data-city]")["data-city"] if soup.select_one("[data-city]") else None
    country = soup.select_one("[data-country]")["data-country"] if soup.select_one("[data-country]") else None

    # Basic labels
    bathroom_label = _text(soup.select_one("[data-bathrooms]"))
    bed_label = _text(soup.select_one("[data-beds]"))
    bedroom_label = _text(soup.select_one("[data-bedrooms]"))
    bedrooms_value = soup.select_one("[data-bedrooms]")
    bedrooms = bedrooms_value["data-bedrooms"] if bedrooms_value and bedrooms_value.has_attr("data-bedrooms") else None

    # Photos
    photos = [img["src"] for img in soup.select(".photo-gallery img[src]")]

    # Amenities / Host / Reviews via helpers
    amenities = extract_amenities(soup)
    host = extract_host(soup)
    reviews = extract_reviews(soup)

    # Optional structured blobs
    section_json = soup.select_one("script[type='application/json'][data-sectioned-description]")
    sectioned_description = None
    if section_json and section_json.string:
        try:
            sectioned_description = json.loads(section_json.string)
        except Exception:
            sectioned_description = None

    guest_controls_json = soup.select_one("script[type='application/json'][data-guest-controls]")
    guest_controls = None
    if guest_controls_json and guest_controls_json.string:
        try:
            guest_controls = json.loads(guest_controls_json.string)
        except Exception:
            guest_controls = None

    listing = Listing(
        url=url,
        airbnbId=airbnb_id,
        name=title,
        numberOfGuests=number_of_guests,
        address=address,
        roomType=room_type,
        location={"lat": lat, "lng": lng},
        reviews=[Review(**r) for r in reviews],
        pricing={"rate": {"amount": amount, "is_micros_accuracy": False}},
        photos=photos,
        amenities=amenities,
        city=city,
        country=country,
        bedrooms=bedrooms,
        bathroomLabel=bathroom_label,
        bedLabel=bed_label,
        bedroomLabel=bedroom_label,
        primaryHost=HostProfile(**host) if host else None,
        sectionedDescription=sectioned_description,
        guestControls=guest_controls,
        currency=currency,
    )

    return listing