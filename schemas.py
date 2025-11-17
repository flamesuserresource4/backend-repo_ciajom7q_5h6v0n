"""
Database Schemas for the Niche Perfume Collection

Each Pydantic model corresponds to a MongoDB collection. The collection name is the lowercase of the class name.
"""
from typing import List, Optional
from pydantic import BaseModel, Field, HttpUrl


class Fragrance(BaseModel):
    """Fragrance (product) documents. Collection name: "fragrance"""
    name: str = Field(..., description="Display name of the fragrance")
    slug: str = Field(..., description="URL-friendly unique identifier")
    variant: Optional[str] = Field(None, description="Edition or special variant (e.g., Collector's Edition)")
    description: str = Field(..., description="Brand storytelling and mythology")
    mythology: Optional[str] = Field(None, description="Mythological background")
    top_notes: List[str] = Field(default_factory=list)
    heart_notes: List[str] = Field(default_factory=list)
    base_notes: List[str] = Field(default_factory=list)
    price: float = Field(..., ge=0)
    currency: str = Field("USD")
    volume_ml: int = Field(50, ge=1)
    color_hex: Optional[str] = Field(None, description="Primary color accent for UI (e.g., #A10808)")
    sku: Optional[str] = None
    images: List[str] = Field(default_factory=list, description="Image URLs")
    spline_url: Optional[HttpUrl] = Field(None, description="3D visualization scene URL (Spline)")
    in_stock: bool = Field(True)


class Testimonial(BaseModel):
    """Social proof quotes. Collection name: "testimonial"""
    author: str
    quote: str
    source: Optional[str] = None
    rating: Optional[float] = Field(None, ge=0, le=5)


class Subscriber(BaseModel):
    """Newsletter subscribers. Collection name: "subscriber"""
    email: str
    tagged_source: Optional[str] = Field(None, description="Where the signup came from")


class CartItem(BaseModel):
    slug: str
    quantity: int = Field(1, ge=1)


class Cart(BaseModel):
    """Shopping carts keyed by a session identifier. Collection name: "cart"""
    session_id: str
    items: List[CartItem] = Field(default_factory=list)
    currency: str = Field("USD")
