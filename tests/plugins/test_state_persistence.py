"""Tests for the state_persistence plugin."""

from unittest.mock import patch, MagicMock

import pytest


MODULE = "code_puppy.plugins.state_persistence.register_callbacks"


class TestOnAgentRunStart:
    """Tests for _on_agent_run_start behaviour."""

    @patch(f"{MODULE}.set_default_agent")
    @patch(f"{MODULE}.is_subagent", return_value=False)
    def test_top_level_run_persists_agent(self, _mock_sub, mock_set):
        from code_puppy.plugins.state_persistence.register_callbacks import (
            _on_agent_run_start,
        )

        _on_agent_run_start("my-agent", "some-model", session_id="s1")

        mock_set.assert_called_once_with("my-agent")

    @patch(f"{MODULE}.set_default_agent")
    @patch(f"{MODULE}.is_subagent", return_value=True)
    def test_subagent_run_skips_persist(self, _mock_sub, mock_set):
        from code_puppy.plugins.state_persistence.register_callbacks import (
            _on_agent_run_start,
        )

        _on_agent_run_start("sub-agent", "some-model")

        mock_set.assert_not_called()

    @patch(f"{MODULE}.set_default_agent", side_effect=RuntimeError("boom"))
    @patch(f"{MODULE}.is_subagent", return_value=False)
    def test_exception_is_swallowed(self, _mock_sub, _mock_set):
        from code_puppy.plugins.state_persistence.register_callbacks import (
            _on_agent_run_start,
        )

        # Should not raise — the bare except swallows everything.
        _on_agent_run_start("explody-agent", "some-model")


class TestCallbackRegistration:
    """Verify the callback is wired up at import time."""

    @patch("code_puppy.callbacks.register_callback")
    def test_callback_registered(self, mock_register):
        import importlib
        import code_puppy.plugins.state_persistence.register_callbacks as mod

        importlib.reload(mod)

        mock_register.assert_any_call("agent_run_start", mod._on_agent_run_start)
