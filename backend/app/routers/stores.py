from typing import List, Optional
from fastapi import APIRouter, Query

from app.schemas import DemoStore
from app.services.demo_stores import DEMO_STORES

router = APIRouter(prefix="/api/stores", tags=["Nearby Stores"])

@router.get("/demo", response_model=List[DemoStore])
def get_demo_stores(
    search: Optional[str] = Query(None, description="Search by store name or product"),
    category: Optional[str] = Query(None, description="Filter by category")
):
    results = DEMO_STORES

    if category and category.lower() != "all":
        results = [s for s in results if category.lower() in s["category"].lower()]

    if search:
        q = search.strip().lower()
        results = [
            s for s in results
            if q in s["name"].lower()
            or q in s["category"].lower()
            or any(q in p.lower() for p in s.get("sample_products", []))
        ]

    return [DemoStore(**s) for s in results]
