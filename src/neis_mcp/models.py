from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class ApiParameter(BaseModel):
    """NEIS Open API request parameter metadata."""

    id: str = Field(..., description="NEIS request parameter name")
    name_ko: str = Field(..., description="Korean parameter display name")
    description: str = Field(default="", description="Parameter description")
    value_type: str = Field(default="string", description="JSON Schema value type")
    required: bool = Field(default=False, description="Whether the parameter is required")


class NeisApiDefinition(BaseModel):
    """A NEIS Open API exposed as an MCP tool."""

    tool_name: str
    title: str
    api_res: str
    description: str
    parameters: List[ApiParameter]
    sample_url: str


class NeisCallResult(BaseModel):
    """Normalized NEIS Open API response."""

    api_name: str
    api_res: str
    request_url: str
    request_params: Dict[str, Any]
    result: Dict[str, Any]
    total_count: Optional[int]
    row_count: int
    rows: List[Dict[str, Any]]
    raw: Optional[Dict[str, Any]] = None
