from code_puppy.callbacks import register_callback
from code_puppy.agents import set_current_agent
from code_puppy.config import set_default_agent
from code_puppy.messaging import emit_info, emit_warning

_SWITCH_COMMANDS = {
    "plan": ("planning-agent", "🐶 Switched to Planning Model"),
    "lead": ("pack-leader", "🐺 Pack Leader is now in charge"),
}


def _custom_help():
    return [
        ("plan", "Switch to planning-agent for task breakdown"),
        ("lead", "Switch to pack-leader for multi-agent orchestration"),
    ]


def _handle_custom_command(command: str, name: str):
    if name not in _SWITCH_COMMANDS:
        return None

    agent_name, message = _SWITCH_COMMANDS[name]

    if not set_current_agent(agent_name):
        emit_warning(f"Agent '{agent_name}' is not available — is it registered?")
        return True

    set_default_agent(agent_name)
    emit_info(message)
    return True


register_callback("custom_command_help", _custom_help)
register_callback("custom_command", _handle_custom_command)
