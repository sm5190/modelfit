from enum import StrEnum

from pydantic import BaseModel, Field


class ToolRisk(StrEnum):
    LOW = "low"
    EXTERNAL_READ = "external_read"
    SENSITIVE_READ = "sensitive_read"
    EXECUTION = "execution"
    EXTERNAL_WRITE = "external_write"


class ToolPolicyRecord(BaseModel):
    server_name: str
    tool_name: str
    risk: ToolRisk = ToolRisk.LOW
    enabled: bool = True
    requires_confirmation: bool = False
    read_only: bool = True
    allowed_roles: set[str] = Field(default_factory=lambda: {"user", "admin"})


class ToolPermissionContext(BaseModel):
    user_role: str = "user"
    enabled_servers: set[str] = Field(default_factory=set)
    enabled_tools: set[str] = Field(default_factory=set)
    explicitly_approved_tools: set[str] = Field(default_factory=set)
