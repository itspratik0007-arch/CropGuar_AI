import uuid
import base64
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, Query, status
from sqlalchemy.orm import Session
from PIL import Image
import io

from app.database import get_db
from app.models import User, Plant, DiseaseDetection
from app.auth import get_current_user
from app.services.disease_model import disease_model_service, CLASS_NAMES
from app.disease_metadata import SUPPORTED_CROPS, get_disease_info
from app.schemas import (
    DiseaseDetectionResponse,
    DiseaseHistoryItem,
    DiseaseModelStatusResponse,
    TopClassProbability,
    DiseaseInfo
)

router = APIRouter(prefix="/api/disease", tags=["Disease Detection"])

# Constants for strict file upload validation
MAX_FILE_SIZE_BYTES = 10 * 1024 * 1024  # 10 MB limit
ALLOWED_MIME_TYPES = {
    "image/jpeg",
    "image/jpg",
    "image/png",
    "image/webp"
}
ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}
MIN_DIMENSION = 32
MAX_DIMENSION = 4096

@router.get("/status", response_model=DiseaseModelStatusResponse)
def get_model_status():
    """
    Returns model configuration status, supported crops, and supported disease classes.
    """
    return DiseaseModelStatusResponse(
        is_configured=disease_model_service.is_configured,
        model_version=disease_model_service.model_version,
        supported_crops=SUPPORTED_CROPS,
        supported_classes=CLASS_NAMES,
        total_classes=len(CLASS_NAMES)
    )

@router.post("/detect", response_model=DiseaseDetectionResponse, status_code=status.HTTP_201_CREATED)
async def detect_disease(
    crop: str = Form(..., description="Selected crop, e.g. Tomato, Potato, Apple, or General"),
    file: UploadFile = File(..., description="Uploaded crop leaf image file"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Analyzes an uploaded leaf image with the real fine-tuned MobileNetV2 plant disease model.
    Validates file format, decoded content, and size. Persists record in the database.
    """
    # 1. Model Availability Check
    if not disease_model_service.is_configured:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Plant disease detection model is not configured. Please download model weights to backend/models/."
        )

    # 2. File size and reading validation
    contents = await file.read()
    if not contents or len(contents) == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The uploaded image file is empty."
        )

    if len(contents) > MAX_FILE_SIZE_BYTES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File exceeds maximum allowed size of {MAX_FILE_SIZE_BYTES // (1024 * 1024)}MB."
        )

    # 3. Inspect decoded image content safely (avoid blind MIME/extension trust)
    try:
        with Image.open(io.BytesIO(contents)) as pil_img:
            img_format = (pil_img.format or "").upper()
            if img_format not in ["JPEG", "JPG", "PNG", "WEBP"]:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Unsupported image format: {img_format}. Allowed formats: JPEG, PNG, WebP."
                )
            width, height = pil_img.size
            if width < MIN_DIMENSION or height < MIN_DIMENSION:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Image dimensions ({width}x{height}) are too small. Minimum size is {MIN_DIMENSION}x{MIN_DIMENSION}."
                )
            if width > MAX_DIMENSION or height > MAX_DIMENSION:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Image dimensions ({width}x{height}) exceed maximum allowed {MAX_DIMENSION}x{MAX_DIMENSION}."
                )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Corrupted or invalid image data: {str(e)}"
        )

    # 4. Crop validation
    cleaned_crop = crop.strip()
    if not cleaned_crop:
        cleaned_crop = "General / Auto-Detect"

    # 5. Run real model inference
    try:
        prediction_result = disease_model_service.predict(contents, crop_hint=cleaned_crop)
    except Exception as err:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Inference execution failed: {str(err)}"
        )

    # 6. Generate controlled, non-sensitive image reference identifier
    image_token = f"img_{uuid.uuid4().hex[:16]}"

    # 7. Check if related Plantopedia plant exists for cross-linking
    disease_info_dict = prediction_result["disease_info"]
    plantopedia_crop_name = disease_info_dict.get("plantopedia_crop") or prediction_result["crop"]
    plant_link = None
    if plantopedia_crop_name:
        plant_link = db.query(Plant).filter(
            Plant.common_name.ilike(f"%{plantopedia_crop_name}%")
        ).first()

    plantopedia_id = plant_link.id if plant_link else None

    # 8. Persist detection record into database for logged-in user
    detection_record = DiseaseDetection(
        user_id=current_user.id,
        plant_id=plantopedia_id,
        selected_crop=cleaned_crop,
        predicted_label=prediction_result["predicted_label"],
        confidence=prediction_result["confidence"],
        is_healthy=prediction_result["is_healthy"],
        model_version=prediction_result["model_version"],
        image_reference=image_token,
        status="completed"
    )
    db.add(detection_record)
    db.commit()
    # Construct response
    return DiseaseDetectionResponse(
        id=detection_record.id,
        selected_crop=detection_record.selected_crop,
        predicted_label=detection_record.predicted_label,
        confidence=detection_record.confidence,
        is_healthy=detection_record.is_healthy,
        model_version=detection_record.model_version,
        created_at=detection_record.created_at,
        image_reference=detection_record.image_reference,
        crop=prediction_result["crop"],
        crop_mismatch=prediction_result["crop_mismatch"],
        top_classes=[
            TopClassProbability(
                label=tc["label"],
                confidence=tc["confidence"],
                probability=tc["probability"]
            ) for tc in prediction_result.get("top_classes", [])
        ],
        disease_info=DiseaseInfo(
            crop=disease_info_dict.get("crop", ""),
            scientific_name=disease_info_dict.get("scientific_name", ""),
            is_healthy=disease_info_dict.get("is_healthy", False),
            description=disease_info_dict.get("description", ""),
            precautions=disease_info_dict.get("precautions", []),
            expert_note=disease_info_dict.get("expert_note", ""),
            plantopedia_crop=disease_info_dict.get("plantopedia_crop")
        ),
        plantopedia_plant_id=plantopedia_id
    )

@router.get("/history", response_model=List[DiseaseHistoryItem])
def get_user_detection_history(
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Returns user-isolated disease detection history records sorted with newest first.
    """
    records = db.query(DiseaseDetection).filter(
        DiseaseDetection.user_id == current_user.id
    ).order_by(
        DiseaseDetection.created_at.desc()
    ).offset(offset).limit(limit).all()

    return records

@router.get("/history/{record_id}", response_model=DiseaseDetectionResponse)
def get_detection_record(
    record_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Fetches full prediction details for a specific record, enforcing user ownership.
    """
    record = db.query(DiseaseDetection).filter(
        DiseaseDetection.id == record_id
    ).first()

    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Detection record not found."
        )

    # Strictly enforce user ownership isolation
    if record.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to view this detection record."
        )

    disease_info_dict = get_disease_info(record.predicted_label)
    plantopedia_crop_name = disease_info_dict.get("plantopedia_crop") or disease_info_dict.get("crop")
    plant_link = None
    if plantopedia_crop_name:
        plant_link = db.query(Plant).filter(
            Plant.common_name.ilike(f"%{plantopedia_crop_name}%")
        ).first()

    plantopedia_id = plant_link.id if plant_link else None

    return DiseaseDetectionResponse(
        id=record.id,
        selected_crop=record.selected_crop,
        predicted_label=record.predicted_label,
        confidence=record.confidence,
        is_healthy=record.is_healthy,
        model_version=record.model_version,
        created_at=record.created_at,
        image_reference=record.image_reference,
        crop=disease_info_dict.get("crop"),
        crop_mismatch=False,
        top_classes=[
            TopClassProbability(
                label=record.predicted_label,
                confidence=record.confidence,
                probability=round(record.confidence / 100.0, 4)
            )
        ],
        disease_info=DiseaseInfo(
            crop=disease_info_dict.get("crop", ""),
            scientific_name=disease_info_dict.get("scientific_name", ""),
            is_healthy=disease_info_dict.get("is_healthy", False),
            description=disease_info_dict.get("description", ""),
            precautions=disease_info_dict.get("precautions", []),
            expert_note=disease_info_dict.get("expert_note", ""),
            plantopedia_crop=disease_info_dict.get("plantopedia_crop")
        ),
        plantopedia_plant_id=plantopedia_id
    )

@router.delete("/history/{record_id}", status_code=status.HTTP_200_OK)
def delete_detection_record(
    record_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Deletes a detection record belonging to the authenticated user.
    """
    record = db.query(DiseaseDetection).filter(
        DiseaseDetection.id == record_id
    ).first()

    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Detection record not found."
        )

    if record.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to delete this record."
        )

    db.delete(record)
    db.commit()
    return {"message": "Record deleted successfully.", "id": record_id}
