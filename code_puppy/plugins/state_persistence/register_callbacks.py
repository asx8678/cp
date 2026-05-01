"""Plugin: persist last-used agent to puppy.cfg on top-level agent runs."""
import logging

from code_puppy.callbacks import register_callback
from code_puppy.config import get_value, set_default_agent
from code_puppy.tools.subagent_context import is_subagent

logger = logging.getLogger(__name__)


def _on_agent_run_start(agent_name: str, model_name: str, session_id=None) -> None:
    """Persist the last-used agent to puppy.cfg on top-level runs."""
    if is_subagent():
        return  # Don't persist during sub-agent invocations
    if get_value("default_agent") == agent_name:
        return  # Already persisted, skip unnecessary write
    try:
        set_default_agent(agent_name)
    except Exception as exc:
        logger.warning("state_persistence: failed to persist agent %r: %s", agent_name, exc)


register_callback("agent_run_start", _on_agent_run_start)
