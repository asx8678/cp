"""Plugin: emit terminal bell on top-level agent task completion."""
import logging
import sys
from typing import Any

from code_puppy.callbacks import register_callback
from code_puppy.config import get_value, set_value
from code_puppy.messaging import emit_error, emit_info
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


def _notification_help() -> list[tuple[str, str]]:
    """Return help entry for the /notification command."""
    return [("notification", "Enable or disable sound notifications (on/off/status)")]


def _handle_notification_command(command: str, name: str) -> bool | None:
    """Handle the /notification slash command.

    Subcommands:
      /notification on     – enable the task bell permanently
      /notification off    – disable the task bell permanently
      /notification        – show current status
      /notification <other> – show usage hint
    """
    if name != "notification":
        return None

    parts = command.split(maxsplit=1)
    subcommand = parts[1].strip().lower() if len(parts) > 1 else ""

    if subcommand == "on":
        set_value("enable_task_bell", "true")
        emit_info("🔔 Sound notifications enabled (saved to config)")
        return True

    if subcommand == "off":
        set_value("enable_task_bell", "false")
        emit_info("🔕 Sound notifications disabled (saved to config)")
        return True

    if subcommand == "":
        status = "ON 🔔" if _is_bell_enabled() else "OFF 🔕"
        emit_info(f"Sound notifications are currently: {status}")
        return True

    # Unknown subcommand – show usage
    emit_error("Usage: /notification on|off")
    return True


register_callback("agent_run_end", _on_agent_run_end)
register_callback("custom_command_help", _notification_help)
register_callback("custom_command", _handle_notification_command)
