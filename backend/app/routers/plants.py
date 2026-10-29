from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.database import get_db
from app.models import Plant, Bookmark, User
from app.schemas import PlantResponse, PlantSearchResponse
from app.auth import get_current_user
from app.services.plant_api import plant_api_service

router = APIRouter(prefix="/api/plants", tags=["Plantopedia"])

def build_plant_response(plant: Plant, user_id: Optional[int], db: Session) -> PlantResponse:
    is_bookmarked = False
    if user_id:
        bookmark = db.query(Bookmark).filter(
            Bookmark.user_id == user_id,
            Bookmark.plant_id == plant.id
        ).first()
        is_bookmarked = bookmark is not None

    return PlantResponse(
        id=plant.id,
        common_name=plant.common_name,
        scientific_name=plant.scientific_name,
        family=plant.family,
        category=plant.category,
        description=plant.description,
        sunlight=plant.sunlight,
        watering=plant.watering,
        soil_requirements=plant.soil_requirements,
        climate=plant.climate,
        temperature_range=plant.temperature_range,
        fertilizer=plant.fertilizer,
        season=plant.season,
        growing_conditions=plant.growing_conditions,
        common_diseases=plant.common_diseases,
        common_pests=plant.common_pests,
        prevention_treatment=plant.prevention_treatment,
        facts=plant.facts,
        image_url=plant.image_url,
        source_type=plant.source_type,
        data_source=plant.data_source,
        external_api_id=plant.external_api_id,
        created_at=plant.created_at,
        updated_at=plant.updated_at,
        is_bookmarked=is_bookmarked
    )

@router.get("/search", response_model=PlantSearchResponse)
async def search_plants_endpoint(
    q: Optional[str] = Query(None, description="Search term for common or scientific name"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Search endpoint compatible with GET /api/plants/search?q=tomato.
    Delegates to list_or_search_plants with pagination support.
    """
    return await list_or_search_plants(q=q, page=page, page_size=page_size, current_user=current_user, db=db)

@router.get("/bookmarks", response_model=List[PlantResponse])
def get_user_bookmarks(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    bookmarks = db.query(Bookmark).filter(Bookmark.user_id == current_user.id).all()
    plant_ids = [b.plant_id for b in bookmarks]
    plants = db.query(Plant).filter(Plant.id.in_(plant_ids)).all() if plant_ids else []
    return [build_plant_response(p, current_user.id, db) for p in plants]

@router.get("", response_model=PlantSearchResponse)
async def list_or_search_plants(
    q: Optional[str] = Query(None, description="Search term for common or scientific name"),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    query_str = q.strip() if q else ""
    api_source = "curated_local"

    # Local search
    local_query = db.query(Plant)
    if query_str:
        search_filter = or_(
            Plant.common_name.ilike(f"%{query_str}%"),
            Plant.scientific_name.ilike(f"%{query_str}%"),
            Plant.family.ilike(f"%{query_str}%"),
            Plant.category.ilike(f"%{query_str}%")
        )
        local_query = local_query.filter(search_filter)

    total_count = local_query.count()

    # If query provided and external API configured, try external API retrieval & deduplication
    if query_str and plant_api_service.is_configured:
        api_results = await plant_api_service.search_plants(query_str)
        if api_results:
            api_source = "external_api"
            for item in api_results:
                existing = db.query(Plant).filter(
                    (Plant.common_name == item["common_name"]) |
                    (Plant.scientific_name == item["scientific_name"])
                ).first()
                if not existing:
                    new_plant = Plant(**item)
                    db.add(new_plant)
                    try:
                        db.commit()
                        db.refresh(new_plant)
                    except Exception:
                        db.rollback()

            # Re-query
            local_query = db.query(Plant).filter(
                or_(
                    Plant.common_name.ilike(f"%{query_str}%"),
                    Plant.scientific_name.ilike(f"%{query_str}%"),
                    Plant.family.ilike(f"%{query_str}%"),
                    Plant.category.ilike(f"%{query_str}%")
                )
            )
            total_count = local_query.count()

    offset = (page - 1) * page_size
    plants = local_query.offset(offset).limit(page_size).all()

    items = [build_plant_response(p, current_user.id, db) for p in plants]
    return PlantSearchResponse(
        items=items,
        total=total_count,
        query=query_str,
        api_source=f"external_api ({plant_api_service.active_provider_name})" if (api_source == "external_api") else ("curated_local" if plant_api_service.is_configured else "curated_local (API key not configured)"),
        page=page,
        page_size=page_size
    )

@router.get("/{plant_id}", response_model=PlantResponse)
def get_plant_detail(
    plant_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    plant = db.query(Plant).filter(Plant.id == plant_id).first()
    if not plant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Plant record with ID {plant_id} not found."
        )
    return build_plant_response(plant, current_user.id, db)

@router.post("/{plant_id}/bookmark", status_code=status.HTTP_201_CREATED)
def add_bookmark(
    plant_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    plant = db.query(Plant).filter(Plant.id == plant_id).first()
    if not plant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Plant does not exist."
        )

    existing_bm = db.query(Bookmark).filter(
        Bookmark.user_id == current_user.id,
        Bookmark.plant_id == plant_id
    ).first()

    if existing_bm:
        return {"message": "Plant is already saved", "bookmarked": True}

    bm = Bookmark(user_id=current_user.id, plant_id=plant_id)
    db.add(bm)
    db.commit()
    return {"message": "Plant saved to your bookmarks", "bookmarked": True}

@router.delete("/{plant_id}/bookmark", status_code=status.HTTP_200_OK)
def remove_bookmark(
    plant_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    bm = db.query(Bookmark).filter(
        Bookmark.user_id == current_user.id,
        Bookmark.plant_id == plant_id
    ).first()

    if not bm:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Bookmark not found."
        )

    db.delete(bm)
    db.commit()
    return {"message": "Bookmark removed", "bookmarked": False}
