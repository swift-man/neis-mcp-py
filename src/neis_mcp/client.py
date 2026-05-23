import json
from typing import Any, Dict, Mapping, Optional, Tuple
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

import httpx

from neis_mcp.models import NeisApiDefinition, NeisCallResult
from neis_mcp.settings import Settings


class NeisApiError(RuntimeError):
    """Raised when the NEIS API cannot be called or parsed."""


class NeisApiClient:
    """HTTP client for NEIS Open API endpoints."""

    def __init__(self, settings: Settings, transport: Optional[httpx.AsyncBaseTransport] = None) -> None:
        self._settings = settings
        self._transport = transport
        self._client: Optional[httpx.AsyncClient] = None

    def build_params(self, api: NeisApiDefinition, arguments: Mapping[str, Any]) -> Dict[str, Any]:
        args = dict(arguments)
        extra_params = args.pop("extra_params", None) or {}

        params: Dict[str, Any] = {
            "Type": "json",
            "pIndex": self._coerce_positive_int(args.pop("pIndex", 1), "pIndex"),
            "pSize": self._coerce_page_size(args.pop("pSize", 100)),
        }

        key = args.pop("KEY", None) or self._settings.neis_api_key
        if key:
            params["KEY"] = key

        for parameter in api.parameters:
            value = args.pop(parameter.id, None)
            if value not in (None, ""):
                params[parameter.id] = value

        if not isinstance(extra_params, Mapping):
            raise NeisApiError("extra_params must be an object")

        reserved_params = {"Type", "pIndex", "pSize", "KEY"}
        reserved_params.update(parameter.id for parameter in api.parameters)
        for key, value in extra_params.items():
            if str(key) in reserved_params:
                raise NeisApiError(f"extra_params cannot override parameter: {key}")
            if value not in (None, ""):
                params[str(key)] = value

        return params

    async def fetch(self, api: NeisApiDefinition, arguments: Mapping[str, Any]) -> NeisCallResult:
        params = self.build_params(api, arguments)
        url = self._api_url(api)

        client = self._get_client()
        try:
            response = await client.get(url, params=params)
            response.raise_for_status()
        except httpx.HTTPError as exc:
            raise NeisApiError(f"NEIS API request failed: {exc}") from exc

        try:
            raw = response.json()
        except json.JSONDecodeError as exc:
            raise NeisApiError("NEIS API returned a non-JSON response") from exc

        if not isinstance(raw, dict):
            raise NeisApiError("NEIS API returned an unexpected JSON response")

        return self._normalize_response(api, raw, str(response.url), params)

    async def close(self) -> None:
        if self._client is not None:
            await self._client.aclose()
            self._client = None

    def _get_client(self) -> httpx.AsyncClient:
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(
                timeout=self._settings.request_timeout_seconds,
                transport=self._transport,
                follow_redirects=True,
            )
        return self._client

    def _api_url(self, api: NeisApiDefinition) -> str:
        return f"{self._settings.neis_base_url.rstrip('/')}/{api.api_res}"

    def _normalize_response(
        self,
        api: NeisApiDefinition,
        raw: Dict[str, Any],
        request_url: str,
        request_params: Mapping[str, Any],
    ) -> NeisCallResult:
        container = raw.get(api.api_res)
        rows = []
        result: Dict[str, Any] = {}
        total_count: Optional[int] = None

        if isinstance(container, list):
            for entry in container:
                if not isinstance(entry, dict):
                    continue
                if "head" in entry:
                    result, total_count = self._parse_head(entry["head"])
                if isinstance(entry.get("row"), list):
                    rows = entry["row"]
        elif isinstance(raw.get("RESULT"), dict):
            result = raw["RESULT"]
        else:
            result = {"CODE": "UNKNOWN", "MESSAGE": "Unexpected NEIS response shape"}

        return NeisCallResult(
            api_name=api.title,
            api_res=api.api_res,
            request_url=self._redact_key(request_url),
            request_params=self._redact_params(request_params),
            result=result,
            total_count=total_count,
            row_count=len(rows),
            rows=rows,
            raw=raw if not rows and result.get("CODE") == "UNKNOWN" else None,
        )

    def _parse_head(self, head: Any) -> Tuple[Dict[str, Any], Optional[int]]:
        result: Dict[str, Any] = {}
        total_count: Optional[int] = None
        if not isinstance(head, list):
            return result, total_count

        for item in head:
            if not isinstance(item, dict):
                continue
            if "list_total_count" in item:
                total_count = item["list_total_count"]
            if isinstance(item.get("RESULT"), dict):
                result = item["RESULT"]

        return result, total_count

    def _coerce_positive_int(self, value: Any, field_name: str) -> int:
        try:
            coerced = int(value)
        except (TypeError, ValueError) as exc:
            raise NeisApiError(f"{field_name} must be an integer") from exc
        if coerced < 1:
            raise NeisApiError(f"{field_name} must be greater than or equal to 1")
        return coerced

    def _coerce_page_size(self, value: Any) -> int:
        page_size = self._coerce_positive_int(value, "pSize")
        if page_size > 1000:
            raise NeisApiError("pSize must be less than or equal to 1000")
        return page_size

    def _redact_params(self, params: Mapping[str, Any]) -> Dict[str, Any]:
        redacted = dict(params)
        if "KEY" in redacted:
            redacted["KEY"] = "***"
        return redacted

    def _redact_key(self, url: str) -> str:
        parts = urlsplit(url)
        query = []
        for key, value in parse_qsl(parts.query, keep_blank_values=True):
            query.append((key, "***" if key == "KEY" else value))
        return urlunsplit((parts.scheme, parts.netloc, parts.path, urlencode(query), parts.fragment))
