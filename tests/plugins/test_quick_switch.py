"""Tests for the quick_switch plugin — /plan and /lead slash commands."""

from __future__ import annotations

import importlib
import sys
from unittest.mock import MagicMock, patch

# Ensure mcp sub-modules are mocked so the deep import chain doesn't explode.
# pydantic_ai.mcp imports a pile of mcp.* sub-modules at module scope.
for _m in (
    "mcp", "mcp.types", "mcp.client", "mcp.client.sse",
    "mcp.client.stdio", "mcp.client.session", "mcp.client.streamable_http",
    "mcp.shared", "mcp.shared.exceptions", "mcp.shared.context",
    "mcp.shared.message", "mcp.shared.session",
    "mcp.server", "mcp.server.sse",
):
    sys.modules.setdefault(_m, MagicMock())

from code_puppy.plugins.quick_switch.register_callbacks import (  # noqa: E402
    _custom_help,
    _handle_custom_command,
)

# ---------------------------------------------------------------------------
# Patch targets (all resolved in the plugin's own namespace)
# ---------------------------------------------------------------------------
_MOD = "code_puppy.plugins.quick_switch.register_callbacks"


# ---------------------------------------------------------------------------
# 1. /plan switches to planning-agent
# ---------------------------------------------------------------------------


class TestPlanCommand:
    @patch(f"{_MOD}.emit_info")
    @patch(f"{_MOD}.set_default_agent")
    @patch(f"{_MOD}.set_current_agent", return_value=True)
    def test_plan_switches_to_planning_agent(
        self, mock_set_current, mock_set_default, mock_emit_info
    ):
        result = _handle_custom_command("/plan", "plan")

        assert result is True
        mock_set_current.assert_called_once_with("planning-agent")
        mock_set_default.assert_called_once_with("planning-agent")
        mock_emit_info.assert_called_once_with("🐶 Switched to Planning Model")


# ---------------------------------------------------------------------------
# 2. /lead switches to pack-leader
# ---------------------------------------------------------------------------


class TestLeadCommand:
    @patch(f"{_MOD}.emit_info")
    @patch(f"{_MOD}.set_default_agent")
    @patch(f"{_MOD}.set_current_agent", return_value=True)
    def test_lead_switches_to_pack_leader(
        self, mock_set_current, mock_set_default, mock_emit_info
    ):
        result = _handle_custom_command("/lead", "lead")

        assert result is True
        mock_set_current.assert_called_once_with("pack-leader")
        mock_set_default.assert_called_once_with("pack-leader")
        mock_emit_info.assert_called_once_with("🐺 Pack Leader is now in charge")


# ---------------------------------------------------------------------------
# 3. Unknown command returns None (we don't own it)
# ---------------------------------------------------------------------------


class TestUnknownCommand:
    def test_unknown_command_returns_none(self):
        assert _handle_custom_command("/foo", "foo") is None


# ---------------------------------------------------------------------------
# 4. Agent not found → emit_warning, skip set_default_agent
# ---------------------------------------------------------------------------


class TestAgentNotFound:
    @patch(f"{_MOD}.emit_warning")
    @patch(f"{_MOD}.set_default_agent")
    @patch(f"{_MOD}.set_current_agent", return_value=False)
    def test_agent_not_found_emits_warning(
        self, mock_set_current, mock_set_default, mock_emit_warn
    ):
        result = _handle_custom_command("/plan", "plan")

        assert result is True
        mock_set_current.assert_called_once_with("planning-agent")
        mock_set_default.assert_not_called()
        mock_emit_warn.assert_called_once_with(
            "Agent 'planning-agent' is not available — is it registered?"
        )


# ---------------------------------------------------------------------------
# 5. /help includes plan and lead entries
# ---------------------------------------------------------------------------


class TestHelp:
    def test_help_returns_plan_and_lead(self):
        entries = _custom_help()
        names = [name for name, _desc in entries]

        assert "plan" in names
        assert "lead" in names
        assert len(entries) == 2


# ---------------------------------------------------------------------------
# 6. Callbacks are actually registered
# ---------------------------------------------------------------------------


class TestCallbackRegistration:
    @patch("code_puppy.callbacks.register_callback")
    def test_callbacks_registered(self, mock_register):
        """Re-importing the module should call register_callback twice."""
        import code_puppy.plugins.quick_switch.register_callbacks as mod

        importlib.reload(mod)

        hook_names = [call.args[0] for call in mock_register.call_args_list]
        assert "custom_command_help" in hook_names
        assert "custom_command" in hook_names
        assert mock_register.call_count == 2
