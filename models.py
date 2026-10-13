import re
from pydantic import BaseModel, HttpUrl, field_validator


class BookRecord(BaseModel):
    """Schema for a clean, normalized book record."""
    title: str
    product_url: str
    price_text: str
    price_gbp: float
    availability_text: str
    rating_text: str
    description: str | None = None
    source_page: str
    fetched_at: str

    @field_validator("product_url", "source_page")
    @classmethod
    def validate_https_url(cls, v: str) -> str:
        if not v.startswith("https://") and not v.startswith("http://"):
            raise ValueError(f"URL must start with http:// or https://: {v}")
        return v

    @field_validator("price_gbp")
    @classmethod
    def validate_positive_price(cls, v: float) -> float:
        if v < 0:
            raise ValueError("Price must be a non-negative number")
        return v


def normalize_record(raw: dict) -> dict:
    """Normalize raw fields: parse price string to float, keeping raw text intact."""
    clean = dict(raw)
    price_match = re.search(r"[\d]+\.[\d]+", raw.get("price_text", ""))
    if price_match:
        clean["price_gbp"] = float(price_match.group(0))
    else:
        clean["price_gbp"] = 0.0

    return clean
