import sys

from code_puppy.callbacks import register_callback
from code_puppy.config import get_value
from code_puppy.tools.subagent_context import is_subagent


def _is_bell_enabled() -> bool:
    """Check if task bell is enabled in puppy.cfg (default: True)."""
    val = get_value("enable_task_bell")
    if val is None:
        return True
    return str(val).lower() not in ("0", "false", "no", "off")


def _on_agent_run_end(
    agent_name, model_name, session_id=None, success=True, error=None,
    response_text=None, metadata=None
):
    """Emit terminal bell on top-level task completion."""
    if is_subagent():
        return  # Don't bell during sub-agent invocations
    if not _is_bell_enabled():
        return
    try:
        sys.stdout.write("\a")
        sys.stdout.flush()
    except Exception:
        pass  # Never crash the app


register_callback("agent_run_end", _on_agent_run_end)
