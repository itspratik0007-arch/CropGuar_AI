import datetime
from sqlalchemy import (
    Column, Integer, String, Text, DateTime, ForeignKey, Boolean, UniqueConstraint, Index
)
from sqlalchemy.orm import relationship
from app.database import Base

def utc_now():
    return datetime.datetime.now(datetime.timezone.utc)

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    farm_location = Column(String(255), nullable=True, default="Demo farm")
    preferences = Column(Text, nullable=True, default="{}")  # JSON or text user preferences
    created_at = Column(DateTime, default=utc_now, nullable=False)
    updated_at = Column(DateTime, default=utc_now, onupdate=utc_now, nullable=False)

    bookmarks = relationship("Bookmark", back_populates="user", cascade="all, delete-orphan")
    detections = relationship("DiseaseDetection", back_populates="user", cascade="all, delete-orphan")
    conversations = relationship("PlantConversation", back_populates="user", cascade="all, delete-orphan")


class Plant(Base):
    __tablename__ = "plants"

    id = Column(Integer, primary_key=True, index=True)
    common_name = Column(String(255), nullable=False, index=True)
    scientific_name = Column(String(255), nullable=False, index=True)
    family = Column(String(255), nullable=True, index=True)
    category = Column(String(100), nullable=True, default="Vegetable", index=True)
    description = Column(Text, nullable=False)
    sunlight = Column(String(255), nullable=False)
    watering = Column(String(255), nullable=False)
    soil_requirements = Column(String(255), nullable=False)
    climate = Column(String(255), nullable=False)
    temperature_range = Column(String(100), nullable=True)
    fertilizer = Column(Text, nullable=True)
    season = Column(String(100), nullable=True)
    growing_conditions = Column(Text, nullable=False)
    common_diseases = Column(Text, nullable=True)
    common_pests = Column(Text, nullable=True)
    prevention_treatment = Column(Text, nullable=True)
    facts = Column(Text, nullable=True)
    image_url = Column(String(1024), nullable=True)
    source_type = Column(String(50), nullable=False, default="curated_local")  # curated_local or external_api
    data_source = Column(String(255), nullable=True, default="Curated Botanical Knowledgebase")
    external_api_id = Column(String(100), nullable=True, index=True)
    created_at = Column(DateTime, default=utc_now, nullable=False)
    updated_at = Column(DateTime, default=utc_now, onupdate=utc_now, nullable=False)

    bookmarks = relationship("Bookmark", back_populates="plant", cascade="all, delete-orphan")
    conversations = relationship("PlantConversation", back_populates="plant", cascade="all, delete-orphan")
    detections = relationship("DiseaseDetection", back_populates="plant")


class Bookmark(Base):
    __tablename__ = "bookmarks"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    plant_id = Column(Integer, ForeignKey("plants.id", ondelete="CASCADE"), nullable=False, index=True)
    created_at = Column(DateTime, default=utc_now, nullable=False)

    user = relationship("User", back_populates="bookmarks")
    plant = relationship("Plant", back_populates="bookmarks")

    __table_args__ = (
        UniqueConstraint("user_id", "plant_id", name="uq_user_plant_bookmark"),
        Index("ix_bookmarks_user_plant", "user_id", "plant_id"),
    )


class PlantConversation(Base):
    __tablename__ = "plant_conversations"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    plant_id = Column(Integer, ForeignKey("plants.id", ondelete="SET NULL"), nullable=True, index=True)
    title = Column(String(255), nullable=False, default="Plant Inquiry")
    created_at = Column(DateTime, default=utc_now, nullable=False, index=True)
    updated_at = Column(DateTime, default=utc_now, onupdate=utc_now, nullable=False, index=True)

    user = relationship("User", back_populates="conversations")
    plant = relationship("Plant", back_populates="conversations")
    messages = relationship("ConversationMessage", back_populates="conversation", cascade="all, delete-orphan", order_by="ConversationMessage.created_at.asc()")

    __table_args__ = (
        Index("ix_conversations_user_updated", "user_id", "updated_at"),
    )


class ConversationMessage(Base):
    __tablename__ = "conversation_messages"

    id = Column(Integer, primary_key=True, index=True)
    conversation_id = Column(Integer, ForeignKey("plant_conversations.id", ondelete="CASCADE"), nullable=False, index=True)
    role = Column(String(20), nullable=False)  # user, assistant, system
    content = Column(Text, nullable=False)
    model_metadata = Column(Text, nullable=True)  # JSON metadata (e.g. model, latency, tokens, source)
    created_at = Column(DateTime, default=utc_now, nullable=False, index=True)

    conversation = relationship("PlantConversation", back_populates="messages")

    __table_args__ = (
        Index("ix_messages_conv_created", "conversation_id", "created_at"),
    )


class DiseaseDetection(Base):
    __tablename__ = "disease_detections"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    plant_id = Column(Integer, ForeignKey("plants.id", ondelete="SET NULL"), nullable=True, index=True)
    selected_crop = Column(String(100), nullable=False)
    predicted_label = Column(String(255), nullable=False)
    confidence = Column(Integer, nullable=False)  # stored as percentage 0-100
    is_healthy = Column(Boolean, default=False, nullable=False)
    model_version = Column(String(100), nullable=False, default="mobilenet_v2_plantvillage_v1")
    image_reference = Column(String(500), nullable=True)  # sanitized generated filename or data ref
    status = Column(String(50), nullable=False, default="completed")
    created_at = Column(DateTime, default=utc_now, nullable=False, index=True)

    user = relationship("User", back_populates="detections")
    plant = relationship("Plant", back_populates="detections")
