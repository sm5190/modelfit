from modelfit.mcp.policy import ToolPolicy
from modelfit.mcp.schemas import (
    ToolPermissionContext,
    ToolPolicyRecord,
    ToolRisk,
)


def test_mcp_policy_requires_confirmation_for_sensitive_tool() -> None:
    record = ToolPolicyRecord(
        server_name="web",
        tool_name="web_search",
        risk=ToolRisk.EXTERNAL_READ,
        requires_confirmation=True,
    )
    context = ToolPermissionContext(
        enabled_servers={"web"},
        enabled_tools={"web_search"},
    )

    decision = ToolPolicy().evaluate(record, context)

    assert decision.allowed is False
    assert decision.requires_confirmation is True


def test_mcp_policy_allows_explicitly_approved_tool() -> None:
    record = ToolPolicyRecord(
        server_name="web",
        tool_name="web_search",
        risk=ToolRisk.EXTERNAL_READ,
        requires_confirmation=True,
    )
    context = ToolPermissionContext(
        enabled_servers={"web"},
        enabled_tools={"web_search"},
        explicitly_approved_tools={"web_search"},
    )

    decision = ToolPolicy().evaluate(record, context)

    assert decision.allowed is True
