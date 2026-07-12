from dataclasses import dataclass

from modelfit.mcp.schemas import ToolPermissionContext, ToolPolicyRecord


@dataclass(frozen=True)
class ToolDecision:
    allowed: bool
    requires_confirmation: bool
    reason: str


class ToolPolicy:
    def evaluate(
        self,
        record: ToolPolicyRecord,
        context: ToolPermissionContext,
    ) -> ToolDecision:
        if not record.enabled:
            return ToolDecision(False, False, "Tool is disabled by administrators.")

        if record.server_name not in context.enabled_servers:
            return ToolDecision(False, False, "MCP server is not enabled for this session.")

        if record.tool_name not in context.enabled_tools:
            return ToolDecision(False, False, "Tool is not enabled for this session.")

        if context.user_role not in record.allowed_roles:
            return ToolDecision(False, False, "User role is not allowed to invoke this tool.")

        confirmation_needed = (
            record.requires_confirmation
            and record.tool_name not in context.explicitly_approved_tools
        )
        if confirmation_needed:
            return ToolDecision(False, True, "Explicit approval is required.")

        return ToolDecision(True, False, "Tool invocation is permitted.")
