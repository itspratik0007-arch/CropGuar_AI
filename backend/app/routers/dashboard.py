from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.database import get_db
from app.models import User, Bookmark, Plant
from app.schemas import DashboardSummaryResponse, RecentBookmark
from app.auth import get_current_user

router = APIRouter(prefix="/api/dashboard", tags=["Dashboard"])

@router.get("/summary", response_model=DashboardSummaryResponse)
def get_dashboard_summary(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    bookmarks_query = (
        db.query(Bookmark, Plant)
        .join(Plant, Bookmark.plant_id == Plant.id)
        .filter(Bookmark.user_id == current_user.id)
        .order_by(desc(Bookmark.created_at))
    )
    
    total_saved = bookmarks_query.count()
    recent_bookmarks_records = bookmarks_query.limit(5).all()

    recent_items = [
        RecentBookmark(
            plant_id=plant.id,
            common_name=plant.common_name,
            scientific_name=plant.scientific_name,
            image_url=plant.image_url,
            bookmarked_at=bookmark.created_at
        )
        for bookmark, plant in recent_bookmarks_records
    ]

    quick_tips = [
        "Regular field scouting prevents minor leaf infections from becoming major crop losses.",
        "Deep, infrequent watering promotes resilient taproot development over shallow root systems.",
        "Always confirm disease symptoms and check registration labels before any treatment application."
    ]

    return DashboardSummaryResponse(
        user_name=current_user.full_name,
        total_saved_plants=total_saved,
        recent_bookmarks=recent_items,
        quick_tips=quick_tips,
        system_status="Operational · Database connected"
    )
