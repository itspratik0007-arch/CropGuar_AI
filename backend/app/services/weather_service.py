import httpx
import logging
from typing import Optional, Dict, Any
from app.config import settings

logger = logging.getLogger(__name__)

class WeatherService:
    """
    Fetches real-time localized weather data to support context-aware agricultural advisory.
    Uses in-memory cache to avoid redundant API calls.
    """
    def __init__(self):
        self.api_key = settings.WEATHER_API_KEY
        self.base_url = settings.WEATHER_API_BASE_URL.rstrip('/')
        self.timeout = 5.0
        self._cache: Dict[str, Dict[str, Any]] = {}

    @property
    def is_configured(self) -> bool:
        return bool(self.api_key and self.api_key.strip())

    async def get_current_weather(self, location: str) -> Optional[Dict[str, Any]]:
        if not self.is_configured:
            return None

        clean_loc = location.strip().lower()
        if clean_loc in self._cache:
            entry = self._cache[clean_loc]
            import time
            if time.time() - entry["timestamp"] < 1800:  # 30 minute cache
                return entry["data"]

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                url = f"{self.base_url}/weather"
                params = {
                    "q": location,
                    "appid": self.api_key,
                    "units": "metric"
                }
                res = await client.get(url, params=params)
                if res.status_code == 200:
                    payload = res.json()
                    weather_summary = {
                        "location": payload.get("name", location),
                        "temp_c": payload.get("main", {}).get("temp"),
                        "humidity": payload.get("main", {}).get("humidity"),
                        "condition": payload.get("weather", [{}])[0].get("description", "clear"),
                        "wind_speed_ms": payload.get("wind", {}).get("speed")
                    }
                    import time
                    self._cache[clean_loc] = {
                        "timestamp": time.time(),
                        "data": weather_summary
                    }
                    return weather_summary
                return None
        except Exception as e:
            logger.warning("Weather API lookup failed: %s", e)
            return None

weather_service = WeatherService()
