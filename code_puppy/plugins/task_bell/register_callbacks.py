"""Plugin: emit terminal bell on top-level agent task completion."""
import logging
import sys
from typing import Any

from code_puppy.callbacks import register_callback
from code_puppy.config import get_value
from code_puppy.tools.subagent_context import is_subagent

logger = logging.getLogger(__name__)


def _is_bell_enabled() -> bool:
    """Check if task bell is enabled in puppy.cfg (default: True)."""
    val = get_value("enable_task_bell")
    if val is None:
        return True
    return str(val).lower() not in ("0", "false", "no", "off")


def _on_agent_run_end(
    agent_name: str,
    model_name: str,
    session_id: str | None = None,
    success: bool = True,
    error: Exception | None = None,
    response_text: str | None = None,
    metadata: Any = None,
) -> None:
    """Emit terminal bell on top-level task completion."""
    if is_subagent():
        return  # Don't bell during sub-agent invocations
    if not _is_bell_enabled():
        return
    try:
        sys.stdout.write("\a")
        sys.stdout.flush()
    except Exception as exc:
        logger.warning("task_bell: failed to write bell character: %s", exc)


register_callback("agent_run_end", _on_agent_run_end)
