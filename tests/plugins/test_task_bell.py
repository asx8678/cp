"""Tests for task_bell plugin — terminal bell on task completion."""

from __future__ import annotations

import io
from unittest.mock import call, patch

import pytest

from code_puppy.plugins.task_bell.register_callbacks import (
    _handle_notification_command,
    _is_bell_enabled,
    _notification_help,
    _on_agent_run_end,
)

_PLUGIN = "code_puppy.plugins.task_bell.register_callbacks"


# -- helpers ------------------------------------------------------------------

def _call_on_agent_run_end(**overrides):
    """Call the handler with sensible defaults, accepting keyword overrides."""
    defaults = dict(
        agent_name="test-agent",
        model_name="test-model",
        session_id=None,
        success=True,
        error=None,
        response_text=None,
        metadata=None,
    )
    defaults.update(overrides)
    _on_agent_run_end(**defaults)


# -- test_bell_emitted_on_top_level_run ---------------------------------------

def test_bell_emitted_on_top_level_run():
    """Bell char written to stdout for a top-level (non-subagent) run."""
    buf = io.StringIO()
    with (
        patch(f"{_PLUGIN}.is_subagent", return_value=False),
        patch(f"{_PLUGIN}.get_value", return_value=None),
        patch("sys.stdout", buf),
    ):
        _call_on_agent_run_end()

    assert "\a" in buf.getvalue()


# -- test_no_bell_on_subagent_run ---------------------------------------------

def test_no_bell_on_subagent_run():
    """No bell when running inside a sub-agent invocation."""
    buf = io.StringIO()
    with (
        patch(f"{_PLUGIN}.is_subagent", return_value=True),
        patch(f"{_PLUGIN}.get_value", return_value=None),
        patch("sys.stdout", buf),
    ):
        _call_on_agent_run_end()

    assert "\a" not in buf.getvalue()


# -- test_bell_disabled_via_config --------------------------------------------

@pytest.mark.parametrize("falsy_value", ["false", "0", "no", "off"])
def test_bell_disabled_via_config(falsy_value: str):
    """Bell suppressed for every false-ish config value."""
    buf = io.StringIO()
    with (
        patch(f"{_PLUGIN}.is_subagent", return_value=False),
        patch(f"{_PLUGIN}.get_value", return_value=falsy_value),
        patch("sys.stdout", buf),
    ):
        _call_on_agent_run_end()

    assert "\a" not in buf.getvalue()


# -- test_bell_enabled_by_default ---------------------------------------------

def test_bell_enabled_by_default():
    """When config key is absent (None), bell is enabled."""
    with patch(f"{_PLUGIN}.get_value", return_value=None):
        assert _is_bell_enabled() is True


# -- test_callback_registered -------------------------------------------------

def test_callback_registered():
    """agent_run_end hook includes our handler after module import."""
    from code_puppy.callbacks import get_callbacks

    callbacks = get_callbacks("agent_run_end")
    assert _on_agent_run_end in callbacks


# =============================================================================
# /notification slash command tests
# =============================================================================

# -- test_notification_help_entry ---------------------------------------------

def test_notification_help_entry():
    """_notification_help returns a list with a 'notification' entry."""
    entries = _notification_help()
    assert isinstance(entries, list)
    names = [name for name, _ in entries]
    assert "notification" in names
    # Description should mention on/off
    for name, desc in entries:
        if name == "notification":
            assert "on" in desc.lower() or "off" in desc.lower() or "sound" in desc.lower()


# -- test_notification_on -----------------------------------------------------

def test_notification_on_enables_bell():
    """/notification on calls set_value with 'true' and returns True."""
    with (
        patch(f"{_PLUGIN}.set_value") as mock_set,
        patch(f"{_PLUGIN}.emit_info") as mock_info,
    ):
        result = _handle_notification_command("notification on", "notification")

    assert result is True
    mock_set.assert_called_once_with("enable_task_bell", "true")
    mock_info.assert_called_once()
    assert "enabled" in mock_info.call_args[0][0].lower()


# -- test_notification_off ----------------------------------------------------

def test_notification_off_disables_bell():
    """/notification off calls set_value with 'false' and returns True."""
    with (
        patch(f"{_PLUGIN}.set_value") as mock_set,
        patch(f"{_PLUGIN}.emit_info") as mock_info,
    ):
        result = _handle_notification_command("notification off", "notification")

    assert result is True
    mock_set.assert_called_once_with("enable_task_bell", "false")
    mock_info.assert_called_once()
    assert "disabled" in mock_info.call_args[0][0].lower()


# -- test_notification_status_when_enabled ------------------------------------

def test_notification_status_when_enabled():
    """/notification (no args) shows ON status when bell is enabled."""
    with (
        patch(f"{_PLUGIN}.get_value", return_value=None),  # default = enabled
        patch(f"{_PLUGIN}.emit_info") as mock_info,
    ):
        result = _handle_notification_command("notification", "notification")

    assert result is True
    mock_info.assert_called_once()
    msg = mock_info.call_args[0][0]
    assert "on" in msg.lower()


# -- test_notification_status_when_disabled -----------------------------------

def test_notification_status_when_disabled():
    """/notification (no args) shows OFF status when bell is disabled."""
    with (
        patch(f"{_PLUGIN}.get_value", return_value="false"),
        patch(f"{_PLUGIN}.emit_info") as mock_info,
    ):
        result = _handle_notification_command("notification", "notification")

    assert result is True
    mock_info.assert_called_once()
    msg = mock_info.call_args[0][0]
    assert "off" in msg.lower()


# -- test_notification_invalid_arg --------------------------------------------

def test_notification_invalid_arg():
    """/notification foobar emits an error about usage and returns True."""
    with (
        patch(f"{_PLUGIN}.emit_error") as mock_err,
    ):
        result = _handle_notification_command("notification foobar", "notification")

    assert result is True
    mock_err.assert_called_once()
    assert "usage" in mock_err.call_args[0][0].lower() or "on" in mock_err.call_args[0][0].lower()


# -- test_notification_unrelated_name -----------------------------------------

def test_notification_unrelated_name():
    """Unrelated command name returns None (plugin doesn't own it)."""
    result = _handle_notification_command("foo bar", "foo")
    assert result is None


# -- test_notification_callbacks_registered -----------------------------------

def test_notification_callbacks_registered():
    """Both custom_command and custom_command_help are registered after import."""
    from code_puppy.callbacks import get_callbacks

    cmd_callbacks = get_callbacks("custom_command")
    help_callbacks = get_callbacks("custom_command_help")

    assert _handle_notification_command in cmd_callbacks
    assert _notification_help in help_callbacks
