from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, EmailStr, Field

# User Schemas
class UserRegister(BaseModel):
    full_name: str = Field(..., min_length=2, max_length=100)
    email: EmailStr
    password: str = Field(..., min_length=6, max_length=128)
    confirm_password: str = Field(..., min_length=6, max_length=128)

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    id: int
    full_name: str
    email: str
    farm_location: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse

# Plant Schemas
class PlantResponse(BaseModel):
    id: int
    common_name: str
    scientific_name: str
    family: Optional[str] = None
    category: Optional[str] = None
    description: str
    sunlight: str
    watering: str
    soil_requirements: str
    climate: str
    temperature_range: Optional[str] = None
    fertilizer: Optional[str] = None
    season: Optional[str] = None
    growing_conditions: str
    common_diseases: Optional[str] = None
    common_pests: Optional[str] = None
    prevention_treatment: Optional[str] = None
    facts: Optional[str] = None
    image_url: Optional[str] = None
    source_type: str
    data_source: Optional[str] = None
    external_api_id: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    is_bookmarked: bool = False

    class Config:
        from_attributes = True

class PlantSearchResponse(BaseModel):
    items: List[PlantResponse]
    total: int
    query: Optional[str] = None
    api_source: str
    page: int = 1
    page_size: int = 20

# Conversational Plant Assistant Schemas
class MessageResponse(BaseModel):
    id: int
    conversation_id: int
    role: str
    content: str
    model_metadata: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True

class ConversationSummaryResponse(BaseModel):
    id: int
    title: str
    plant_id: Optional[int] = None
    plant_common_name: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    message_count: int = 0
    last_message: Optional[str] = None

    class Config:
        from_attributes = True

class ConversationDetailResponse(BaseModel):
    id: int
    title: str
    plant_id: Optional[int] = None
    plant: Optional[PlantResponse] = None
    created_at: datetime
    updated_at: datetime
    messages: List[MessageResponse]

    class Config:
        from_attributes = True

class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=4000)
    plant_id: Optional[int] = None
    conversation_id: Optional[int] = None
    language: Optional[str] = "en"

class ChatResponse(BaseModel):
    conversation_id: int
    title: str
    plant_id: Optional[int] = None
    plant_common_name: Optional[str] = None
    message: MessageResponse
    grounding_sources: List[str] = []
    model: str = "assistant"
    is_fallback: bool = False

# Dashboard Summary Schema
class RecentBookmark(BaseModel):
    plant_id: int
    common_name: str
    scientific_name: str
    image_url: Optional[str] = None
    bookmarked_at: datetime

class DashboardSummaryResponse(BaseModel):
    user_name: str
    total_saved_plants: int
    recent_bookmarks: List[RecentBookmark]
    quick_tips: List[str]
    system_status: str

# Nearby Stores Schema
class DemoStore(BaseModel):
    id: str
    name: str
    category: str
    address: str
    phone: str
    sample_products: List[str]
    operating_hours: str
    is_demo: bool = True

# Disease Detection Schemas
class TopClassProbability(BaseModel):
    label: str
    confidence: int
    probability: float

class DiseaseInfo(BaseModel):
    crop: str
    scientific_name: str
    is_healthy: bool
    description: str
    precautions: List[str]
    expert_note: str
    plantopedia_crop: Optional[str] = None

class DiseaseDetectionResponse(BaseModel):
    id: int
    selected_crop: str
    predicted_label: str
    confidence: int
    is_healthy: bool
    model_version: str
    created_at: datetime
    image_reference: Optional[str] = None
    crop: Optional[str] = None
    crop_mismatch: bool = False
    top_classes: Optional[List[TopClassProbability]] = None
    disease_info: Optional[DiseaseInfo] = None
    plantopedia_plant_id: Optional[int] = None

    class Config:
        from_attributes = True

class DiseaseHistoryItem(BaseModel):
    id: int
    selected_crop: str
    predicted_label: str
    confidence: int
    is_healthy: bool
    model_version: str
    status: str
    image_reference: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True

class DiseaseModelStatusResponse(BaseModel):
    is_configured: bool
    model_version: str
    supported_crops: List[str]
    supported_classes: List[str]
    total_classes: int
