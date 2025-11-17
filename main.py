import os
from typing import List, Optional
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from schemas import Fragrance, Subscriber, Testimonial, Cart, CartItem
from database import db, create_document, get_documents

app = FastAPI(title="Niche Perfume Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------- Utility & Startup Seed ----------------------

class SubscribeIn(BaseModel):
    email: str
    tagged_source: Optional[str] = None


class AddCartItemIn(BaseModel):
    quantity: int = 1


def seed_fragrances():
    if db is None:
        return
    col = db["fragrance"]
    if col.count_documents({}) > 0:
        return

    items: List[dict] = [
        {
            "name": "Wrath",
            "slug": "wrath",
            "description": "A blazing accord of peppered smoke and scorched resin. The heat of battle captured in amber and steel.",
            "mythology": "Forged in the furnace of Ares, tempered by thunderbolts.",
            "top_notes": ["Black Pepper", "Charred Citrus"],
            "heart_notes": ["Smoked Guaiac", "Incense"],
            "base_notes": ["Amber", "Gunmetal", "Birch Tar"],
            "price": 295.0,
            "currency": "USD",
            "volume_ml": 50,
            "color_hex": "#8B0000",
            "sku": "SIN-WR-50",
            "images": [],
            "spline_url": None,
            "in_stock": True,
        },
        {
            "name": "Envy",
            "slug": "envy",
            "description": "Verdant whispers of emerald ivy and green fig over cold marble.",
            "mythology": "A serpent's gaze beneath a laurel crown.",
            "top_notes": ["Green Fig", "Galbanum"],
            "heart_notes": ["Ivy", "Violet Leaf"],
            "base_notes": ["Moss", "Ambroxan"],
            "price": 285.0,
            "currency": "USD",
            "volume_ml": 50,
            "color_hex": "#046307",
            "sku": "SIN-EN-50",
            "images": [],
            "spline_url": None,
            "in_stock": True,
        },
        {
            "name": "Sloth",
            "slug": "sloth",
            "description": "A languid veil of chamomile, hay, and worn leather pages.",
            "mythology": "Dreams drifting through the Library of Hypnos.",
            "top_notes": ["Chamomile", "Bergamot"],
            "heart_notes": ["Hay", "Iris"],
            "base_notes": ["Suede", "Tonka"],
            "price": 260.0,
            "currency": "USD",
            "volume_ml": 50,
            "color_hex": "#5C4A3F",
            "sku": "SIN-SL-50",
            "images": [],
            "spline_url": None,
            "in_stock": True,
        },
        {
            "name": "Lust",
            "slug": "lust",
            "description": "Crimson rose steeped in saffron and skin-warm musk.",
            "mythology": "A hymn to Aphrodite sung behind velvet curtains.",
            "top_notes": ["Saffron", "Pink Pepper"],
            "heart_notes": ["Damask Rose", "Jasmine"],
            "base_notes": ["Musk", "Labdanum", "Sandalwood"],
            "price": 310.0,
            "currency": "USD",
            "volume_ml": 50,
            "color_hex": "#7A0A1A",
            "sku": "SIN-LU-50",
            "images": [],
            "spline_url": None,
            "in_stock": True,
        },
        {
            "name": "Gluttony",
            "slug": "gluttony",
            "description": "Decadent drips of dark cherry, rum-soaked cake, and molten cacao.",
            "mythology": "Offerings left at Dionysus' altar.",
            "top_notes": ["Black Cherry", "Boozy Accord"],
            "heart_notes": ["Cacao", "Cinnamon"],
            "base_notes": ["Vanilla", "Benzoin"],
            "price": 295.0,
            "currency": "USD",
            "volume_ml": 50,
            "color_hex": "#3B0B0B",
            "sku": "SIN-GL-50",
            "images": [],
            "spline_url": None,
            "in_stock": True,
        },
        {
            "name": "Pride",
            "slug": "pride",
            "description": "Gilded iris upon burnished leather and polished woods.",
            "mythology": "A king's fragrance for a mirror-bright throne.",
            "top_notes": ["Aldehydes", "Cardamom"],
            "heart_notes": ["Orris", "Cedar"],
            "base_notes": ["Leather", "Vetiver"],
            "price": 320.0,
            "currency": "USD",
            "volume_ml": 50,
            "color_hex": "#B8860B",
            "sku": "SIN-PR-50",
            "images": [],
            "spline_url": None,
            "in_stock": True,
        },
        {
            "name": "Greed",
            "slug": "greed",
            "description": "Liquid gold: saffron, oud, and a treasury of resins.",
            "mythology": "Midas' touch bottled.",
            "top_notes": ["Saffron", "Bitter Orange"],
            "heart_notes": ["Rose", "Oud"],
            "base_notes": ["Myrrh", "Patchouli", "Ambergris"] ,
            "price": 350.0,
            "currency": "USD",
            "volume_ml": 50,
            "color_hex": "#C5A047",
            "sku": "SIN-GR-50",
            "images": [],
            "spline_url": None,
            "in_stock": True,
        },
        {
            "name": "Oblivion (Collector's Edition)",
            "slug": "oblivion",
            "variant": "Collector's Edition",
            "description": "Ink-black iris drowned in abyssal musk and cold stone.",
            "mythology": "A perfume for crossing the Lethe.",
            "top_notes": ["Black Ink Accord", "Elemi"],
            "heart_notes": ["Iris", "Licorice"],
            "base_notes": ["Musk", "Slate", "Cedar"],
            "price": 420.0,
            "currency": "USD",
            "volume_ml": 50,
            "color_hex": "#0B0B0C",
            "sku": "COL-OB-50",
            "images": [],
            "spline_url": None,
            "in_stock": True,
        },
    ]

    col.insert_many(items)


@app.on_event("startup")
async def on_startup():
    try:
        seed_fragrances()
    except Exception:
        pass


# ---------------------- Routes ----------------------

@app.get("/")
def read_root():
    return {"message": "Niche Perfume Backend Running"}


@app.get("/api/fragrances", response_model=List[Fragrance])
def list_fragrances():
    if db is None:
        raise HTTPException(status_code=500, detail="Database not configured")
    docs = get_documents("fragrance")
    for d in docs:
        d.pop("_id", None)
    return docs


@app.get("/api/fragrances/{slug}", response_model=Fragrance)
def get_fragrance(slug: str):
    if db is None:
        raise HTTPException(status_code=500, detail="Database not configured")
    doc = db["fragrance"].find_one({"slug": slug})
    if not doc:
        raise HTTPException(status_code=404, detail="Fragrance not found")
    doc.pop("_id", None)
    return doc


@app.post("/api/subscribe")
def subscribe(payload: SubscribeIn):
    if db is None:
        raise HTTPException(status_code=500, detail="Database not configured")
    data = payload.model_dump()
    create_document("subscriber", data)
    return {"status": "ok"}


@app.get("/api/testimonials", response_model=List[Testimonial])
def testimonials():
    if db is None:
        return []
    docs = get_documents("testimonial")
    for d in docs:
        d.pop("_id", None)
    return docs


# Cart endpoints
@app.get("/api/cart/{session_id}", response_model=Cart)
def get_cart(session_id: str):
    if db is None:
        raise HTTPException(status_code=500, detail="Database not configured")
    doc = db["cart"].find_one({"session_id": session_id})
    if not doc:
        cart = Cart(session_id=session_id)
        create_document("cart", cart)
        return cart
    doc.pop("_id", None)
    # ensure items conform
    return Cart(**doc)


@app.post("/api/cart/{session_id}/items/{slug}")
def add_or_update_item(session_id: str, slug: str, payload: AddCartItemIn):
    if db is None:
        raise HTTPException(status_code=500, detail="Database not configured")
    cart = db["cart"].find_one({"session_id": session_id})
    if not cart:
        cart = Cart(session_id=session_id, items=[CartItem(slug=slug, quantity=payload.quantity)]).model_dump()
        db["cart"].insert_one(cart)
    else:
        found = False
        for it in cart.get("items", []):
            if it["slug"] == slug:
                it["quantity"] = payload.quantity
                found = True
        if not found:
            cart.setdefault("items", []).append({"slug": slug, "quantity": payload.quantity})
        db["cart"].update_one({"_id": cart["_id"]}, {"$set": {"items": cart["items"]}})
    return {"status": "ok"}


@app.delete("/api/cart/{session_id}/items/{slug}")
def remove_item(session_id: str, slug: str):
    if db is None:
        raise HTTPException(status_code=500, detail="Database not configured")
    cart = db["cart"].find_one({"session_id": session_id})
    if cart:
        new_items = [it for it in cart.get("items", []) if it.get("slug") != slug]
        db["cart"].update_one({"_id": cart["_id"]}, {"$set": {"items": new_items}})
    return {"status": "ok"}


@app.post("/api/checkout")
def checkout(session_id: str):
    # Placeholder checkout flow. In production, integrate Shopify/Woo.
    if db is None:
        raise HTTPException(status_code=500, detail="Database not configured")
    cart = db["cart"].find_one({"session_id": session_id})
    if not cart or not cart.get("items"):
        raise HTTPException(status_code=400, detail="Cart is empty")
    return {"status": "ready", "message": "Proceeding to secure checkout gateway."}


@app.get("/test")
def test_database():
    response = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": None,
        "database_name": None,
        "connection_status": "Not Connected",
        "collections": []
    }
    try:
        if db is not None:
            response["database"] = "✅ Available"
            response["database_url"] = "✅ Configured"
            response["database_name"] = db.name if hasattr(db, 'name') else "✅ Connected"
            response["connection_status"] = "Connected"
            try:
                collections = db.list_collection_names()
                response["collections"] = collections[:10]
                response["database"] = "✅ Connected & Working"
            except Exception as e:
                response["database"] = f"⚠️  Connected but Error: {str(e)[:50]}"
        else:
            response["database"] = "⚠️  Available but not initialized"
    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:50]}"

    import os as _os
    response["database_url"] = "✅ Set" if _os.getenv("DATABASE_URL") else "❌ Not Set"
    response["database_name"] = "✅ Set" if _os.getenv("DATABASE_NAME") else "❌ Not Set"
    return response


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
