"""Tests for task_bell plugin — terminal bell on task completion."""

from __future__ import annotations

import io
from unittest.mock import patch

import pytest

from code_puppy.plugins.task_bell.register_callbacks import (
    _is_bell_enabled,
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
