#imports
from pathlib import Path
from dataclasses import dataclass
import tomllib

#default config
CONFIG_PATH = Path.home() / ".config" / "npu-assistant" / "config.toml"
DEFAULT_CONFIG = """ 

[assistant]
name = "Assistant"
system_prompt = "You are a helpful assistant. Be concise and direct. Always respond in English only."

[model]
device = "NPU"
do_sample = false
max_new_tokens = 512
rep_penalty = 1.1

"""

#default model settings
MODELS_DIR = Path.home() / ".cache" / "npu-assistant" / "models"
DEFAULT_PROMPT = "You are a helpful assistant. Be concise and direct. Always respond in English only."

@dataclass
class Config:
    name: str = "Assistant"
    system_prompt: str = DEFAULT_PROMPT
    device: str = "NPU"
    model_path: str = None
    do_sample: bool = False
    max_new_tokens: int = 512
    rep_penalty: float = 1.1


def save_model_path(model_path):
    """Save selected model path to config file."""
    if not CONFIG_PATH.exists():
        CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
        CONFIG_PATH.write_text(DEFAULT_CONFIG)

    text = CONFIG_PATH.read_text()
    lines = text.splitlines()
    new_lines = []
    found = False

    for line in lines:
        # Replace existing model_path line
        if line.strip().startswith("model_path"):
            new_lines.append(f'model_path = "{model_path}"')
            found = True
        else:
            new_lines.append(line)

    # If no model_path line existed, add it under [model]
    if not found:
        final_lines = []
        for line in new_lines:
            final_lines.append(line)
            if line.strip() == "[model]":
                final_lines.append(f'model_path = "{model_path}"')
        new_lines = final_lines

    CONFIG_PATH.write_text("\n".join(new_lines) + "\n")



def save_device(device):
    """Save selected device to config file."""
    if not CONFIG_PATH.exists():
        CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
        CONFIG_PATH.write_text(DEFAULT_CONFIG)

    text = CONFIG_PATH.read_text()
    lines = text.splitlines()
    new_lines = []
    found = False

    for line in lines:
        if line.strip().startswith("device"):
            new_lines.append(f'device = "{device}"')
            found = True
        else:
            new_lines.append(line)

    if not found:
        final_lines = []
        for line in new_lines:
            final_lines.append(line)
            if line.strip() == "[model]":
                final_lines.append(f'device = "{device}"')
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
                max_new_tokens=model.get("max_new_tokens", 512),
                rep_penalty=model.get("rep_penalty", 1.1),
            )


    
        