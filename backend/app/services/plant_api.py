import httpx
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
from app.config import settings

logger = logging.getLogger(__name__)

class PlantApiService:
    """
    Botanical reference API service supporting:
    1. Perenual API (Primary, if PERENUAL_API_KEY is configured)
    2. Trefle API (Fallback/Alternative, if PLANT_API_KEY is configured)
    Provides in-memory caching to minimize external API roundtrips and avoid rate limits.
    """
    def __init__(self):
        self.perenual_api_key = settings.PERENUAL_API_KEY
        self.perenual_base_url = settings.PERENUAL_API_BASE_URL.rstrip('/')

        self.trefle_api_key = settings.PLANT_API_KEY
        self.trefle_base_url = settings.PLANT_API_BASE_URL.rstrip('/')

        self.timeout = 8.0
        self._cache: Dict[str, Dict[str, Any]] = {}  # query -> {timestamp, data}
        self.cache_ttl_seconds = 3600  # 1 hour cache

    @property
    def is_perenual_configured(self) -> bool:
        return bool(self.perenual_api_key and self.perenual_api_key.strip())

    @property
    def is_trefle_configured(self) -> bool:
        return bool(self.trefle_api_key and self.trefle_api_key.strip())

    @property
    def is_configured(self) -> bool:
        return self.is_perenual_configured or self.is_trefle_configured

    @property
    def active_provider_name(self) -> str:
        if self.is_perenual_configured:
            return "Perenual Botanical API"
        if self.is_trefle_configured:
            return "Trefle Botanical API"
        return "None"

    async def search_plants(self, query: str) -> Optional[List[Dict[str, Any]]]:
        if not self.is_configured:
            return None

        clean_query = query.strip().lower()
        now = datetime.utcnow().timestamp()

        # Check in-memory cache
        if clean_query in self._cache:
            entry = self._cache[clean_query]
            if now - entry["timestamp"] < self.cache_ttl_seconds:
                return entry["data"]

        # 1. Try Perenual if configured
        if self.is_perenual_configured:
            results = await self._search_perenual(query)
            if results:
                self._cache[clean_query] = {"timestamp": now, "data": results}
                return results

        # 2. Try Trefle as alternative/legacy if configured
        if self.is_trefle_configured:
            results = await self._search_trefle(query)
            if results:
                self._cache[clean_query] = {"timestamp": now, "data": results}
                return results

        return None

    async def _search_perenual(self, query: str) -> Optional[List[Dict[str, Any]]]:
        """
        Perenual Species List search:
        Endpoint: /species-list?key={key}&q={query}
        """
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                url = f"{self.perenual_base_url}/species-list"
                params = {
                    "key": self.perenual_api_key,
                    "q": query
                }
                response = await client.get(url, params=params)
                if response.status_code == 200:
                    data = response.json()
                    raw_items = data.get("data", [])
                    results: List[Dict[str, Any]] = []

                    for item in raw_items:
                        # Extract common and scientific names
                        common = item.get("common_name") or "Unknown Crop"
                        # Scientific name can be a list or a string in Perenual
                        sci_raw = item.get("scientific_name")
                        if isinstance(sci_raw, list) and len(sci_raw) > 0:
                            scientific = sci_raw[0]
                        elif isinstance(sci_raw, str):
                            scientific = sci_raw
                        else:
                            scientific = common

                        family = item.get("family") or "Botanical Specimen"
                        category = item.get("type") or "Cultivated Plant"

                        # Extract image url if available
                        image_url = None
                        default_img = item.get("default_image")
                        if isinstance(default_img, dict):
                            image_url = (
                                default_img.get("regular_url") or
                                default_img.get("medium_url") or
                                default_img.get("original_url") or
                                default_img.get("thumbnail")
                            )

                        # Watering & Sunlight strings
                        watering_val = item.get("watering") or "Moderate watering based on soil moisture"
                        sunlight_raw = item.get("sunlight")
                        if isinstance(sunlight_raw, list):
                            sunlight_val = ", ".join(sunlight_raw).capitalize()
                        elif isinstance(sunlight_raw, str):
                            sunlight_val = sunlight_raw
                        else:
                            sunlight_val = "Full sun to partial shade"

                        cycle = item.get("cycle") or "Annual / Perennial"

                        results.append({
                            "external_api_id": str(item.get("id")),
                            "common_name": common.strip().title(),
                            "scientific_name": scientific.strip(),
                            "family": family,
                            "category": category.title(),
                            "image_url": image_url,
                            "description": f"Botanical record from Perenual for {common} ({scientific}). Life cycle: {cycle}. Watering: {watering_val}.",
                            "sunlight": f"{sunlight_val} (Perenual recommendation)",
                            "watering": f"{watering_val.capitalize()} moisture maintenance",
                            "soil_requirements": "Well-draining, nutrient-balanced soil; check local agricultural parameters",
                            "climate": f"Adaptable growing zones; growth cycle: {cycle}",
                            "temperature_range": "15°C - 30°C (standard optimal)",
                            "fertilizer": "Apply balanced organic compost and NPK as per localized soil test",
                            "season": f"{cycle} growing cycle",
                            "growing_conditions": f"Care Level: {item.get('care_level', 'Moderate')}. Growth Cycle: {cycle}.",
                            "common_diseases": "Foliar blights, powdery mildew, and root rots in humid, poor-drainage conditions.",
                            "common_pests": "Aphids, thrips, spider mites, and caterpillars.",
                            "prevention_treatment": "Routine scouting, crop rotation, and integrated pest management (IPM) practices.",
                            "facts": f"Perenual ID: {item.get('id')}. Life cycle: {cycle}.",
                            "source_type": "external_api",
                            "data_source": "Perenual Botanical API"
                        })
                    return results
                else:
                    logger.warning("Perenual API returned status %s: %s", response.status_code, response.text[:200])
                    return None
        except Exception as e:
            logger.warning("Perenual API request failed: %s", e)
            return None

    async def _search_trefle(self, query: str) -> Optional[List[Dict[str, Any]]]:
        """
        Legacy Trefle search endpoint fallback.
        """
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                url = f"{self.trefle_base_url}/plants/search"
                params = {
                    "token": self.trefle_api_key,
                    "q": query
                }
                response = await client.get(url, params=params)
                if response.status_code == 200:
                    data = response.json()
                    results = []
                    for item in data.get("data", []):
                        common = item.get("common_name") or item.get("scientific_name") or "Unknown Plant"
                        scientific = item.get("scientific_name") or "Not recorded"
                        family = item.get("family") or item.get("family_common_name") or "Unclassified"
                        genus = item.get("genus") or "N/A"
                        author = item.get("author") or "Standard botanical nomenclature"

                        results.append({
                            "external_api_id": str(item.get("id")),
                            "common_name": common,
                            "scientific_name": scientific,
                            "family": family,
                            "category": "External Botanical Catalog",
                            "image_url": item.get("image_url"),
                            "description": f"Botanical record retrieved from external plant service for {common} ({scientific}).",
                            "sunlight": "Full to partial sunlight based on regional variety requirements",
                            "watering": "Moderate irrigation calibrated to regional soil moisture",
                            "soil_requirements": "Well-draining, fertile loamy soil; check local agricultural extension parameters",
                            "climate": "Check regional climate zone adaptability",
                            "temperature_range": "18°C - 30°C (typical temperate to tropical)",
                            "fertilizer": "Apply balanced organic compost and NPK as per localized soil test",
                            "season": "Cultivated across typical regional growing calendar",
                            "growing_conditions": f"Taxonomic Genus: {genus}. Botanical Family: {family}.",
                            "common_diseases": "Susceptible to typical foliar fungal blights and root rots in humid, poor-drainage conditions.",
                            "common_pests": "Aphids, thrips, spider mites, and leaf-feeding larvae.",
                            "prevention_treatment": "Routine field scouting, crop rotation, and integrated pest management (IPM) practices.",
                            "facts": f"Botanical authority: {author}. Genus: {genus}.",
                            "source_type": "external_api",
                            "data_source": "Trefle Botanical API"
                        })
                    return results
                return None
        except Exception as e:
            logger.warning("Trefle API request failed: %s", e)
            return None

plant_api_service = PlantApiService()
