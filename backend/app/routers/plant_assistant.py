import json
import logging
from typing import List, Optional
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.database import get_db
from app.models import User, Plant, PlantConversation, ConversationMessage
from app.schemas import (
    ChatRequest,
    ChatResponse,
    ConversationSummaryResponse,
    ConversationDetailResponse,
    MessageResponse,
    PlantResponse
)
from app.auth import get_current_user
from app.routers.plants import build_plant_response
from app.services.ai_assistant import ai_assistant_service
from app.services.weather_service import weather_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/plant-assistant", tags=["Plant AI Assistant"])

@router.get("/conversations", response_model=List[ConversationSummaryResponse])
def get_user_conversations(
    limit: int = Query(30, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Returns user-isolated conversations, ordered with most recently updated first.
    Strictly scoped to current_user.id.
    """
    convs = db.query(PlantConversation).filter(
        PlantConversation.user_id == current_user.id
    ).order_by(
        desc(PlantConversation.updated_at)
    ).offset(offset).limit(limit).all()

    results = []
    for c in convs:
        last_msg = db.query(ConversationMessage).filter(
            ConversationMessage.conversation_id == c.id
        ).order_by(desc(ConversationMessage.created_at)).first()

        count = db.query(ConversationMessage).filter(
            ConversationMessage.conversation_id == c.id
        ).count()

        results.append(
            ConversationSummaryResponse(
                id=c.id,
                title=c.title,
                plant_id=c.plant_id,
                plant_common_name=c.plant.common_name if c.plant else None,
                created_at=c.created_at,
                updated_at=c.updated_at,
                message_count=count,
                last_message=last_msg.content[:120] if last_msg else None
            )
        )
    return results

@router.get("/conversations/{conversation_id}", response_model=ConversationDetailResponse)
def get_conversation_detail(
    conversation_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Fetches full message history for a specific conversation with strict ownership check.
    """
    conv = db.query(PlantConversation).filter(
        PlantConversation.id == conversation_id
    ).first()

    if not conv:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found."
        )

    if conv.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to access this conversation."
        )

    plant_resp = build_plant_response(conv.plant, current_user.id, db) if conv.plant else None

    messages_resp = [
        MessageResponse(
            id=m.id,
            conversation_id=m.conversation_id,
            role=m.role,
            content=m.content,
            model_metadata=m.model_metadata,
            created_at=m.created_at
        )
        for m in conv.messages
    ]

    return ConversationDetailResponse(
        id=conv.id,
        title=conv.title,
        plant_id=conv.plant_id,
        plant=plant_resp,
        created_at=conv.created_at,
        updated_at=conv.updated_at,
        messages=messages_resp
    )

@router.delete("/conversations/{conversation_id}", status_code=status.HTTP_200_OK)
def delete_conversation(
    conversation_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Deletes a conversation and its messages. Enforces strict user authorization.
    """
    conv = db.query(PlantConversation).filter(
        PlantConversation.id == conversation_id
    ).first()

    if not conv:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found."
        )

    if conv.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to delete this conversation."
        )

    db.delete(conv)
    db.commit()
    return {"message": "Conversation deleted successfully.", "id": conversation_id}

@router.post("/chat", response_model=ChatResponse, status_code=status.HTTP_200_OK)
async def chat_with_assistant(
    request: ChatRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Multi-turn Conversational AI Endpoint for Plant Assistant.
    - Resolves/creates conversation strictly bound to current_user.id
    - Retrieves botanical profile from database
    - Retrieves weather advisory context based on farm location
    - Passes grounded context and message history to AI service
    - Saves user and assistant messages atomically in transaction
    """
    user_query = request.message.strip()
    if not user_query:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Message content cannot be blank."
        )

    # 1. Resolve or create conversation
    conv: Optional[PlantConversation] = None
    if request.conversation_id:
        conv = db.query(PlantConversation).filter(
            PlantConversation.id == request.conversation_id
        ).first()

        if not conv:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Specified conversation does not exist."
            )

        if conv.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Unauthorized access to conversation."
            )
        
        # If plant_id supplied on existing conversation, update it if not set
        if request.plant_id and not conv.plant_id:
            conv.plant_id = request.plant_id
    else:
        # Create new conversation
        # Generate initial title from plant or query
        title = "Plant Discussion"
        if request.plant_id:
            p = db.query(Plant).filter(Plant.id == request.plant_id).first()
            if p:
                title = f"{p.common_name} Advice"
        else:
            title = user_query[:40] + ("..." if len(user_query) > 40 else "")

        conv = PlantConversation(
            user_id=current_user.id,
            plant_id=request.plant_id,
            title=title
        )
        db.add(conv)
        db.commit()
        db.refresh(conv)

    # 2. Retrieve plant profile for context
    plant: Optional[Plant] = None
    active_plant_id = conv.plant_id or request.plant_id
    if active_plant_id:
        plant = db.query(Plant).filter(Plant.id == active_plant_id).first()

    plant_context = None
    if plant:
        plant_context = {
            "id": plant.id,
            "common_name": plant.common_name,
            "scientific_name": plant.scientific_name,
            "family": plant.family,
            "category": plant.category,
            "description": plant.description,
            "sunlight": plant.sunlight,
            "watering": plant.watering,
            "soil_requirements": plant.soil_requirements,
            "climate": plant.climate,
            "temperature_range": plant.temperature_range,
            "fertilizer": plant.fertilizer,
            "season": plant.season,
            "growing_conditions": plant.growing_conditions,
            "common_diseases": plant.common_diseases,
            "common_pests": plant.common_pests,
            "prevention_treatment": plant.prevention_treatment,
            "facts": plant.facts,
            "data_source": plant.data_source
        }

    # 3. Retrieve weather context if farm location is present
    weather_context = None
    if current_user.farm_location:
        weather_context = await weather_service.get_current_weather(current_user.farm_location)

    # 4. Fetch past message history for context window (last 10 turns)
    history_messages = db.query(ConversationMessage).filter(
        ConversationMessage.conversation_id == conv.id
    ).order_by(ConversationMessage.created_at.asc()).limit(10).all()

    msg_payload = [{"role": m.role, "content": m.content} for m in history_messages]
    msg_payload.append({"role": "user", "content": user_query})

    # 5. Call AI Assistant Service
    ai_result = await ai_assistant_service.generate_response(
        messages=msg_payload,
        plant_context=plant_context,
        weather_context=weather_context,
        user_name=current_user.full_name
    )

    # 6. Atomic Persistence: Save User Message + Assistant Message
    try:
        user_msg = ConversationMessage(
            conversation_id=conv.id,
            role="user",
            content=user_query,
            created_at=datetime.now(timezone.utc)
        )
        db.add(user_msg)

        meta_json = json.dumps({
            "model": ai_result.get("model"),
            "grounding_sources": ai_result.get("grounding_sources", []),
            "is_fallback": ai_result.get("is_fallback", False)
        })

        asst_msg = ConversationMessage(
            conversation_id=conv.id,
            role="assistant",
            content=ai_result.get("content", ""),
            model_metadata=meta_json,
            created_at=datetime.now(timezone.utc)
        )
        db.add(asst_msg)

        # Update conversation timestamp
        conv.updated_at = datetime.now(timezone.utc)
        db.commit()
        db.refresh(asst_msg)

    except Exception as e:
        db.rollback()
        logger.exception("Failed to persist conversation turn: %s", e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to save message to database."
        )

    return ChatResponse(
        conversation_id=conv.id,
        title=conv.title,
        plant_id=plant.id if plant else None,
        plant_common_name=plant.common_name if plant else None,
        message=MessageResponse(
            id=asst_msg.id,
            conversation_id=asst_msg.conversation_id,
            role=asst_msg.role,
            content=asst_msg.content,
            model_metadata=asst_msg.model_metadata,
            created_at=asst_msg.created_at
        ),
        grounding_sources=ai_result.get("grounding_sources", []),
        model=ai_result.get("model", "assistant"),
        is_fallback=ai_result.get("is_fallback", False)
    )
