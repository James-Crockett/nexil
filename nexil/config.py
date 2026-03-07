#imports
from pathlib import Path
from dataclasses import dataclass
import tomllib

#default config
CONFIG_PATH = Path.home() / ".config" / "nexil" / "config.toml"
DEFAULT_CONFIG = """ 

[assistant]
name = "Assistant"
system_prompt = "You are a helpful assistant. Be concise and direct. Always respond in English only. Address all parts of the user's message, not just the tool-related parts."

[model]
device = "NPU"
do_sample = false
max_new_tokens = 1024
rep_penalty = 1.1

"""

DEFAULT_PROMPT = "You are a helpful assistant. Be concise and direct. Always respond in English only. Address all parts of the user's message, not just the tool-related parts."

@dataclass
class Config:
    name: str = "Assistant"
    system_prompt: str = DEFAULT_PROMPT
    device: str = "NPU"
    model_path: str = None
    thinks: bool = False
    native_tools: bool = False
    do_sample: bool = False
    max_new_tokens: int = 1024
    rep_penalty: float = 1.1


def _escape_toml_value(value):
    """Escape a string for safe insertion into a TOML value."""
    return value.replace("\\", "\\\\").replace('"', '\\"').replace("\n", "\\n")


def save_model_path(model_path):
    """Save selected model path to config file."""
    if not CONFIG_PATH.exists():
        CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
        CONFIG_PATH.write_text(DEFAULT_CONFIG)

    safe_path = _escape_toml_value(str(model_path))
    text = CONFIG_PATH.read_text()
    lines = text.splitlines()
    new_lines = []
    found = False

    for line in lines:
        # Replace existing model_path line (exact key match)
        stripped = line.strip()
        if stripped == "model_path" or stripped.startswith("model_path ") or stripped.startswith("model_path="):
            new_lines.append(f'model_path = "{safe_path}"')
            found = True
        else:
            new_lines.append(line)

    # If no model_path line existed, add it under [model]
    if not found:
        final_lines = []
        for line in new_lines:
            final_lines.append(line)
            if line.strip() == "[model]":
                final_lines.append(f'model_path = "{safe_path}"')
        new_lines = final_lines

    CONFIG_PATH.write_text("\n".join(new_lines) + "\n")



def save_device(device):
    """Save selected device to config file."""
    if not CONFIG_PATH.exists():
        CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
        CONFIG_PATH.write_text(DEFAULT_CONFIG)

    safe_device = _escape_toml_value(str(device))
    text = CONFIG_PATH.read_text()
    lines = text.splitlines()
    new_lines = []
    found = False

    for line in lines:
        stripped = line.strip()
        if stripped == "device" or stripped.startswith("device ") or stripped.startswith("device="):
            new_lines.append(f'device = "{safe_device}"')
            found = True
        else:
            new_lines.append(line)

    if not found:
        final_lines = []
        for line in new_lines:
            final_lines.append(line)
            if line.strip() == "[model]":
                final_lines.append(f'device = "{safe_device}"')
        new_lines = final_lines

    CONFIG_PATH.write_text("\n".join(new_lines) + "\n")


def load_config():
    """Loads config files if created else goes with default configs"""
    if not CONFIG_PATH.exists():
        CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
        CONFIG_PATH.write_text(DEFAULT_CONFIG)
        return Config()
        
    else:
        with open(CONFIG_PATH, "rb") as f:
            data = tomllib.load(f)
            assistant = data.get("assistant", {})
            model = data.get("model", {})
            return Config(
                name=assistant.get("name", "Assistant"),
                system_prompt=assistant.get("system_prompt", DEFAULT_PROMPT),
                device=model.get("device", "NPU"),
                model_path=model.get("model_path", None),
                do_sample=model.get("do_sample", False),
                max_new_tokens=model.get("max_new_tokens", 1024),
                rep_penalty=model.get("rep_penalty", 1.1),
            )


    
        