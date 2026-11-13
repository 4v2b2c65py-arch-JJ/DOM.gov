"""Government API connectors."""
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, Optional

import aiohttp
import structlog

logger = structlog.get_logger()


@dataclass
class ConnectorResult:
    success: bool
    data: Optional[Dict[str, Any]] = None
    timestamp: datetime = field(default_factory=datetime.utcnow)
    error: Optional[str] = None


class GovAPIConnectorManager:
    def __init__(self, settings: Any) -> None:
        self.settings = settings

    def _config_for(self, api: str) -> Optional[Dict[str, Any]]:
        s = self.settings
        mapping = {
            "dgii": (s.DGII_BASE_URL, s.DGII_CLIENT_ID, s.DGII_CLIENT_SECRET),
            "jce": (s.JCE_BASE_URL, None, None),
            "mivhed": (s.MIVHED_BASE_URL, s.MIVHED_CLIENT_ID, s.MIVHED_CLIENT_SECRET),
            "superate": (s.SUPERATE_BASE_URL, s.SUPERATE_CLIENT_ID, s.SUPERATE_CLIENT_SECRET),
            "adess": (s.ADESS_BASE_URL, s.ADESS_CLIENT_ID, s.ADESS_CLIENT_SECRET),
            "ede_norte": (s.EDE_NORTE_BASE_URL, s.EDE_NORTE_API_KEY, None),
            "ede_sur": (s.EDE_SUR_BASE_URL, s.EDE_SUR_API_KEY, None),
            "ede_este": (s.EDE_ESTE_BASE_URL, s.EDE_ESTE_API_KEY, None),
            "coraasan": (s.CORAASAN_BASE_URL, s.CORAASAN_API_KEY, None),
            "caasd": (s.CAASD_BASE_URL, s.CAASD_API_KEY, None),
            "inapa": (s.INAPA_BASE_URL, s.INAPA_API_KEY, None),
            "coe": (s.COE_BASE_URL, None, None),
        }
        if api not in mapping:
            return None
        base_url, client_id, client_secret = mapping[api]
        if not base_url:
            return None
        headers = {"Accept": "application/json"}
        if client_id:
            headers["X-Client-Id"] = client_id
        if client_secret:
            headers["X-Client-Secret"] = client_secret
        return {"base_url": base_url, "headers": headers}

    async def call(self, api: str, method: str, params: Dict[str, Any]) -> ConnectorResult:
        config = self._config_for(api)
        if config is None:
            return ConnectorResult(success=False, error=f"API not configured: {api}")
        url = f"{config['base_url'].rstrip('/')}/{method.lstrip('/')}"
        try:
            timeout = aiohttp.ClientTimeout(total=15)
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.post(url, json=params, headers=config["headers"]) as response:
                    payload = await response.json(content_type=None)
                    if response.status < 400:
                        return ConnectorResult(success=True, data=payload)
                    return ConnectorResult(success=False, error=f"HTTP {response.status}")
        except Exception as exc:
            logger.warning("gov_api_call_failed", api=api, method=method, error=str(exc))
            return ConnectorResult(success=False, error=str(exc))