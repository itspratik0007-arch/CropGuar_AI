import httpx
import json
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
from app.config import settings

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """You are CropShield AI's expert Agricultural and Botanical Advisor.
Your mission is to provide accurate, reliable, practical, and scientifically sound crop guidance and plant care advice to farmers, agronomists, and home growers.

Core Persona & Communication Guidelines:
1. Grounding & Scientific Integrity:
   - Base your recommendations on verified agronomy and botanical science.
   - Use the retrieved plant profile data provided in the context whenever available.
   - If information is uncertain, unknown, or depends on specific local soil testing, explicitly state the limitation.
   - Distinguish confirmed factual diagnoses from possible causes or working hypotheses.
   - Never invent scientific facts, research citations, fake chemical compound dosages, or arbitrary confidence scores.

2. Safety & Chemical Pesticides:
   - Prioritize cultural, biological, and Integrated Pest Management (IPM) practices (e.g. neem oil, sticky traps, spacing, crop rotation, resistant varieties).
   - Do NOT provide arbitrary pesticide dosages or hazardous chemical handling instructions without reliable crop-specific regulatory guidance and safety precautions.
   - Advise the user to consult local agricultural extension officers or certified agronomy dealers before applying restricted synthetic chemicals.

3. Formatting & Clarity:
   - Organize detailed answers cleanly with markdown headings (###), numbered steps, and bullet points.
   - Keep answers clear and easy to read. If technical terms (e.g., tillering, necrosis, solanaceous, transpiration) are used, briefly clarify them in simple language.
   - If the user asks in another language (e.g., Hindi, Marathi, Spanish), respond fluently and accurately in that requested language.

4. Weather & Disease Risk Context:
   - Remind farmers that weather-based risk predictions are estimates based on humidity and temperature patterns, not guaranteed outbreaks.
"""

class AiAssistantService:
    def __init__(self):
        # Google Gemini Configuration
        self.gemini_api_key = settings.GEMINI_API_KEY
        self.gemini_model = settings.GEMINI_MODEL or "gemini-3.5-flash"
        self.gemini_base_url = "https://generativelanguage.googleapis.com/v1beta"

        # OpenAI Configuration (Alternative fallback)
        self.openai_api_key = settings.OPENAI_API_KEY
        self.openai_base_url = settings.OPENAI_BASE_URL.rstrip('/')
        self.openai_model = settings.OPENAI_MODEL

        self.timeout = 35.0

    @property
    def is_gemini_configured(self) -> bool:
        return bool(self.gemini_api_key and self.gemini_api_key.strip())

    @property
    def is_openai_configured(self) -> bool:
        return bool(self.openai_api_key and self.openai_api_key.strip())

    @property
    def is_configured(self) -> bool:
        return self.is_gemini_configured or self.is_openai_configured

    async def generate_response(
        self,
        messages: List[Dict[str, str]],
        plant_context: Optional[Dict[str, Any]] = None,
        weather_context: Optional[Dict[str, Any]] = None,
        user_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generates a grounded agricultural advice response.
        Priority:
        1. Google Gemini API (Primary)
        2. OpenAI API (Alternative if Gemini is not configured)
        3. Local verified rule-based agronomic fallback (if no keys configured or on API errors)
        """
        grounding_sources = []
        if plant_context:
            source_name = plant_context.get("data_source") or "CropShield Botanical Knowledgebase"
            grounding_sources.append(f"{plant_context.get('common_name')} ({plant_context.get('scientific_name')}): {source_name}")
        if weather_context:
            grounding_sources.append(f"Weather Station ({weather_context.get('location')}): Temp {weather_context.get('temp_c')}°C, Humidity {weather_context.get('humidity')}%")

        if not self.is_configured:
            # Safe grounded fallback when keys are absent
            fallback_text = self._generate_grounded_fallback(
                messages=messages,
                plant_context=plant_context,
                weather_context=weather_context,
                user_name=user_name,
                is_missing_key=True
            )
            return {
                "content": fallback_text,
                "model": "rule-based-botanical-fallback (GEMINI_API_KEY not configured)",
                "grounding_sources": grounding_sources,
                "is_fallback": True
            }

        # 1. Attempt Google Gemini call if configured
        if self.is_gemini_configured:
            gemini_res = await self._call_gemini(messages, plant_context, weather_context, grounding_sources)
            if gemini_res:
                return gemini_res

        # 2. Attempt OpenAI call if configured
        if self.is_openai_configured:
            openai_res = await self._call_openai(messages, plant_context, weather_context, grounding_sources)
            if openai_res:
                return openai_res

        # 3. Fallback if configured providers failed
        fallback_text = self._generate_grounded_fallback(
            messages=messages,
            plant_context=plant_context,
            weather_context=weather_context,
            user_name=user_name,
            is_missing_key=False,
            error_detail="Configured AI provider request failed"
        )
        return {
            "content": fallback_text,
            "model": "rule-based-botanical-fallback (AI provider offline)",
            "grounding_sources": grounding_sources,
            "is_fallback": True
        }

    async def _call_gemini(
        self,
        messages: List[Dict[str, str]],
        plant_context: Optional[Dict[str, Any]],
        weather_context: Optional[Dict[str, Any]],
        grounding_sources: List[str]
    ) -> Optional[Dict[str, Any]]:
        """
        Calls Google Gemini generateContent API via standard HTTP.
        """
        system_instruction = self._build_system_instruction(plant_context, weather_context)
        
        # Build contents array in Gemini format: {"role": "user"|"model", "parts": [{"text": ...}]}
        contents = []
        for msg in messages:
            role = "user" if msg.get("role") in ["user", "system"] else "model"
            contents.append({
                "role": role,
                "parts": [{"text": msg.get("content", "")}]
            })

        payload = {
            "system_instruction": {
                "parts": [{"text": system_instruction}]
            },
            "contents": contents,
            "generationConfig": {
                "temperature": 0.4,
                "maxOutputTokens": 2048,
            }
        }

        import asyncio
        url = f"{self.gemini_base_url}/models/{self.gemini_model}:generateContent"
        params = {"key": self.gemini_api_key}

        for attempt in range(3):
            try:
                async with httpx.AsyncClient(timeout=self.timeout) as client:
                    res = await client.post(url, params=params, json=payload)
                    if res.status_code == 200:
                        data = res.json()
                        candidates = data.get("candidates", [])
                        if candidates and "content" in candidates[0]:
                            parts = candidates[0]["content"].get("parts", [])
                            text = "".join([p.get("text", "") for p in parts])
                            return {
                                "content": text,
                                "model": f"Gemini ({self.gemini_model})",
                                "grounding_sources": grounding_sources,
                                "is_fallback": False
                            }
                    elif res.status_code in [503, 429] and attempt < 2:
                        logger.warning("Gemini returned %s (attempt %d/3), retrying in %ds...", res.status_code, attempt + 1, attempt + 2)
                        await asyncio.sleep(attempt + 2)
                        continue
                    else:
                        logger.warning("Gemini API returned status %s: %s", res.status_code, res.text[:300])
                        return None
            except Exception as e:
                logger.warning("Gemini API request failed (attempt %d/3): %s", attempt + 1, e)
                if attempt < 2:
                    await asyncio.sleep(attempt + 1)
                    continue
                return None

    async def _call_openai(
        self,
        messages: List[Dict[str, str]],
        plant_context: Optional[Dict[str, Any]],
        weather_context: Optional[Dict[str, Any]],
        grounding_sources: List[str]
    ) -> Optional[Dict[str, Any]]:
        """
        Calls OpenAI chat completions API.
        """
        system_instruction = self._build_system_instruction(plant_context, weather_context)
        formatted_messages = [{"role": "system", "content": system_instruction}]
        for msg in messages:
            formatted_messages.append({
                "role": msg.get("role", "user"),
                "content": msg.get("content", "")
            })

        try:
            headers = {
                "Authorization": f"Bearer {self.openai_api_key}",
                "Content-Type": "application/json"
            }
            payload = {
                "model": self.openai_model,
                "messages": formatted_messages,
                "temperature": 0.4,
                "max_tokens": 1500
            }

            async with httpx.AsyncClient(timeout=self.timeout) as client:
                res = await client.post(
                    f"{self.openai_base_url}/chat/completions",
                    headers=headers,
                    json=payload
                )
                if res.status_code == 200:
                    data = res.json()
                    ai_content = data["choices"][0]["message"]["content"]
                    model_used = data.get("model", self.openai_model)
                    return {
                        "content": ai_content,
                        "model": f"OpenAI ({model_used})",
                        "grounding_sources": grounding_sources,
                        "is_fallback": False
                    }
                return None
        except Exception as e:
            logger.warning("OpenAI API request failed: %s", e)
            return None

    def _build_system_instruction(
        self,
        plant_context: Optional[Dict[str, Any]],
        weather_context: Optional[Dict[str, Any]]
    ) -> str:
        system_content = SYSTEM_PROMPT
        if plant_context:
            system_content += f"\n\n### RETRIEVED PLANT PROFILE FOR CURRENT CONVERSATION:\n"
            system_content += f"- Common Name: {plant_context.get('common_name')}\n"
            system_content += f"- Scientific Name: {plant_context.get('scientific_name')}\n"
            system_content += f"- Family: {plant_context.get('family', 'N/A')}\n"
            system_content += f"- Category: {plant_context.get('category', 'Crop')}\n"
            system_content += f"- Sunlight: {plant_context.get('sunlight', 'N/A')}\n"
            system_content += f"- Watering: {plant_context.get('watering', 'N/A')}\n"
            system_content += f"- Soil Requirements: {plant_context.get('soil_requirements', 'N/A')}\n"
            system_content += f"- Climate & Temperature: {plant_context.get('climate', 'N/A')} ({plant_context.get('temperature_range', 'N/A')})\n"
            system_content += f"- Fertilizer Needs: {plant_context.get('fertilizer', 'N/A')}\n"
            system_content += f"- Season: {plant_context.get('season', 'N/A')}\n"
            system_content += f"- Growing Conditions: {plant_context.get('growing_conditions', 'N/A')}\n"
            system_content += f"- Common Diseases: {plant_context.get('common_diseases', 'N/A')}\n"
            system_content += f"- Common Pests: {plant_context.get('common_pests', 'N/A')}\n"
            system_content += f"- Prevention & Treatment: {plant_context.get('prevention_treatment', 'N/A')}\n"
            system_content += f"- Agricultural Facts: {plant_context.get('facts', 'N/A')}\n"
            system_content += f"- Data Source: {plant_context.get('data_source', 'Botanical Library')}\n"

        if weather_context:
            system_content += f"\n### CURRENT LOCAL WEATHER CONDITIONS (for {weather_context.get('location')}):\n"
            system_content += f"- Temperature: {weather_context.get('temp_c')}°C\n"
            system_content += f"- Humidity: {weather_context.get('humidity')}%\n"
            system_content += f"- Conditions: {weather_context.get('condition')}\n"
            system_content += f"- Wind Speed: {weather_context.get('wind_speed_ms')} m/s\n"

        return system_content

    def _generate_grounded_fallback(
        self,
        messages: List[Dict[str, str]],
        plant_context: Optional[Dict[str, Any]] = None,
        weather_context: Optional[Dict[str, Any]] = None,
        user_name: Optional[str] = None,
        is_missing_key: bool = True,
        error_detail: Optional[str] = None
    ) -> str:
        """
        Creates an agronomic, highly informative response based directly on the verified
        database record when an AI API key is not configured or offline.
        """
        last_user_query = messages[-1]["content"].lower() if messages else ""
        plant_name = plant_context.get("common_name", "this crop") if plant_context else "your crop"
        sci_name = plant_context.get("scientific_name", "") if plant_context else ""

        # Language detection (Marathi request check)
        is_marathi = any(k in last_user_query for k in ["marathi", "मराठी"])

        disclaimer_banner = ""
        if is_missing_key:
            disclaimer_banner = "> [!NOTE]\n> **Configuration Note:** `GEMINI_API_KEY` is not currently set in `.env`. Serving verified agronomic guidance directly from CropShield's curated database.\n\n"
        elif error_detail:
            disclaimer_banner = f"> [!WARNING]\n> **Service Notice:** External AI provider connection failed ({error_detail}). Serving verified agronomic guidance from local database records.\n\n"

        if is_marathi:
            if plant_context:
                return (
                    f"{disclaimer_banner}### {plant_name} ({sci_name}) - शेती व पीक संरक्षण माहिती\n\n"
                    f"**१. माती व हवामान आवश्यकता:**\n"
                    f"- माती: {plant_context.get('soil_requirements', 'सुपीक आणि उत्तम निचरा होणारी जमीन')}\n"
                    f"- हवामान व तापमान: {plant_context.get('climate', 'उबदार हवामान')} ({plant_context.get('temperature_range', 'अनुकूल तापमान')})\n\n"
                    f"**२. पाणी आणि सूर्यप्रकाश:**\n"
                    f"- सूर्यप्रकाश: {plant_context.get('sunlight', 'दररोज ६-८ तास पूर्ण सूर्यप्रकाश')}\n"
                    f"- पाणी व्यवस्थापन: {plant_context.get('watering', 'जमिनीतील ओलाव्यानुसार मध्यम पाणी')}\n\n"
                    f"**३. मुख्य रोग आणि कीड नियंत्रण:**\n"
                    f"- मुख्य रोग: {plant_context.get('common_diseases', 'बुरशीजन्य करपा, पानांवरील ठिपके')}\n"
                    f"- मुख्य किडी: {plant_context.get('common_pests', 'मावा, तुडतुडे, पांढरी माशी')}\n"
                    f"- प्रतिबंधक उपाय: {plant_context.get('prevention_treatment', 'नीम तेलाची फवारणी, पिकांची फेरपालट आणि योग्य अंतर')}\n\n"
                    f"**४. खत व्यवस्थापन:**\n"
                    f"- {plant_context.get('fertilizer', 'सेंद्रिय शेणखत आणि संतुलित NPK खतांचा वापर')}\n\n"
                    f"**महत्त्वाची टीप:** रासायनिक औषधांचा वापर करण्यापूर्वी स्थानिक कृषी अधिकाऱ्यांचा सल्ला घ्या."
                )
            else:
                return f"{disclaimer_banner}कृपया वनस्पती किंवा पिकाची निवड करा जेणेकरून आम्ही अचूक माहिती पुरवू शकू."

        # Generic plant context fallback
        if not plant_context:
            return (
                f"{disclaimer_banner}### CropShield Botanical Assistant\n\n"
                f"Welcome! To give you the most accurate growing advice, please select a specific crop from the Plantopedia library or mention the crop name.\n\n"
                f"I can provide complete guidance on:\n"
                f"- **Soil preparation and suitable pH**\n"
                f"- **Watering schedules and sunlight requirements**\n"
                f"- **Fertilizer programs (NPK split applications)**\n"
                f"- **Disease symptoms, fungal vs bacterial diagnostics**\n"
                f"- **Natural pest management with IPM**\n\n"
                f"Which plant would you like to explore today?"
            )

        # Disease questions
        if any(w in last_user_query for w in ["disease", "fungal", "bacterial", "infection", "sick", "yellow", "brown", "spot", "blight"]):
            return (
                f"{disclaimer_banner}### Disease Diagnostics & Health Management for {plant_name} (*{sci_name}*)\n\n"
                f"#### 1. Common Diseases Affecting This Crop\n"
                f"- **Known Pathogens:** {plant_context.get('common_diseases')}\n\n"
                f"#### 2. Symptom Analysis (Yellowing vs Brown Spots)\n"
                f"- **Yellowing Leaves (Chlorosis):** Often caused by nitrogen deficiency, overwatering leading to root suffocation, or viral vectors like whiteflies. If yellowing is concentrated between veins, check for magnesium or iron deficiency.\n"
                f"- **Brown Spots / Concentric Rings:** Typically fungal blights (e.g. *Alternaria* or *Phytophthora*). Bacterial spots usually present water-soaked margins with a faint yellow halo.\n\n"
                f"#### 3. Step-by-Step Prevention & Treatment Plan\n"
                f"1. **Sanitation:** Remove and safely dispose of heavily infected leaves. Do not compost diseased foliage.\n"
                f"2. **Irrigation adjustment:** Switch to base/drip irrigation; water splash is the primary vector for fungal spore dispersal.\n"
                f"3. **Airflow:** Maintain adequate row and plant spacing to facilitate rapid drying of morning dew.\n"
                f"4. **Protective Treatment:** {plant_context.get('prevention_treatment')}\n\n"
                f"> [!IMPORTANT]\n"
                f"> **Safety Reminder:** Before applying synthetic fungicides or bactericides, verify approved local registrations and strictly observe Pre-Harvest Intervals (PHI)."
            )

        # Fertilizer questions
        if any(w in last_user_query for w in ["fertilizer", "nutrient", "npk", "feed", "manure"]):
            return (
                f"{disclaimer_banner}### Fertilizer & Nutrient Guide for {plant_name} (*{sci_name}*)\n\n"
                f"#### Recommended Nutrition Program\n"
                f"{plant_context.get('fertilizer')}\n\n"
                f"#### Application Timeline & Best Practices\n"
                f"- **Basal / Planting Stage:** Incorporate well-decomposed farmyard manure (FYM) or compost alongside initial phosphorus and potassium to establish deep root architecture.\n"
                f"- **Vegetative Growth:** Supply nitrogen in split doses to sustain vigorous leafy canopy without inducing succulent excess.\n"
                f"- **Flowering & Fruit Development:** Increase potassium (K) to support flower retention, fruit sizing, and stress resilience.\n\n"
                f"> [!TIP]\n"
                f"> Excessive nitrogen causes dense, lush foliage that attracts aphids and makes plants highly susceptible to fungal mildew."
            )

        # Care and growing questions
        if any(w in last_user_query for w in ["water", "soil", "sunlight", "ph", "growing guide", "care", "how to grow", "temperature"]):
            return (
                f"{disclaimer_banner}### Comprehensive Growing & Agronomic Profile: {plant_name} (*{sci_name}*)\n\n"
                f"**Botanical Family:** {plant_context.get('family', 'N/A')}  \n"
                f"**Crop Category:** {plant_context.get('category', 'Vegetable/Crop')}  \n"
                f"**Optimal Season:** {plant_context.get('season', 'Check local season')}  \n\n"
                f"#### 1. Soil & Field Preparation\n"
                f"- **Requirements:** {plant_context.get('soil_requirements')}\n"
                f"- Ensure deep tilling and organic incorporation for soil aeration and drainage.\n\n"
                f"#### 2. Sunlight & Climate\n"
                f"- **Sunlight:** {plant_context.get('sunlight')}\n"
                f"- **Climate:** {plant_context.get('climate')}\n"
                f"- **Temperature Range:** {plant_context.get('temperature_range', 'Moderate conditions')}\n\n"
                f"#### 3. Irrigation Strategy\n"
                f"- **Watering Routine:** {plant_context.get('watering')}\n"
                f"- *What if you overwater?* Stagnant water deprives roots of oxygen, triggering damping-off and root rot (*Pythium/Rhizoctonia*). Allow topsoil to dry slightly between watering cycles.\n\n"
                f"#### 4. Cultivation & Management\n"
                f"{plant_context.get('growing_conditions')}\n\n"
                f"**Notable Agricultural Note:** {plant_context.get('facts', 'Cultivated globally.')}"
            )

        # Pest control questions
        if any(w in last_user_query for w in ["pest", "insect", "natural", "organic", "bug", "worm"]):
            return (
                f"{disclaimer_banner}### Integrated Pest Management (IPM) for {plant_name}\n\n"
                f"#### 1. Common Pests Scouting\n"
                f"- **Major Threats:** {plant_context.get('common_pests')}\n\n"
                f"#### 2. Natural & Bio-Control Tactics\n"
                f"- **Neem Oil Spray:** Dilute cold-pressed neem oil (3-5 ml/L) with a mild surfactant; disrupts insect feeding and hormone molting.\n"
                f"- **Physical Trapping:** Deploy yellow sticky traps for whiteflies and aphids, and blue sticky traps for thrips (15-20 traps/acre).\n"
                f"- **Beneficial Predators:** Preserve ladybird beetles, lacewings, and predatory mites which prey heavily on soft-bodied pests.\n"
                f"- **Crop Rotation:** {plant_context.get('prevention_treatment')}"
            )

        # Default comprehensive answer
        return (
            f"{disclaimer_banner}### Agronomic Advisory: {plant_name} (*{sci_name}*)\n\n"
            f"**Overview:** {plant_context.get('description')}\n\n"
            f"#### Key Growing Specifications\n"
            f"- **Sunlight:** {plant_context.get('sunlight')}\n"
            f"- **Watering:** {plant_context.get('watering')}\n"
            f"- **Soil & pH:** {plant_context.get('soil_requirements')}\n"
            f"- **Climate & Temperature:** {plant_context.get('climate')} ({plant_context.get('temperature_range', 'N/A')})\n"
            f"- **Fertilizer Program:** {plant_context.get('fertilizer')}\n\n"
            f"#### Protection & Health Management\n"
            f"- **Common Diseases:** {plant_context.get('common_diseases')}\n"
            f"- **Common Pests:** {plant_context.get('common_pests')}\n"
            f"- **Prevention Guidance:** {plant_context.get('prevention_treatment')}\n\n"
            f"Feel free to ask follow-up questions such as:\n"
            f"- *'What if I overwater it?'*\n"
            f"- *'How can I identify early fungal symptoms?'*\n"
            f"- *'Give me a step-by-step fertilizer plan.'*\n"
            f"- *'Explain this in Marathi.'*"
        )

ai_assistant_service = AiAssistantService()
