"""State persistence plugin — remembers the last-used agent across restarts."""

from code_puppy.callbacks import register_callback
from code_puppy.config import set_default_agent
from code_puppy.tools.subagent_context import is_subagent


def _on_agent_run_start(agent_name, model_name, session_id=None):
    """Persist the last-used agent to puppy.cfg on top-level runs."""
    if is_subagent():
        return  # Don't persist during sub-agent invocations

    try:
        set_default_agent(agent_name)
    except Exception:
        pass  # Never crash the app


register_callback("agent_run_start", _on_agent_run_start)
