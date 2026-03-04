#imports
from pathlib import Path
from dataclasses import dataclass

#default settings
CONFIG_PATH = Path.home() / ".config" / "npu-assistant" / "config.toml"
MODELS_DIR = Path.home() / ".cache" / "npu-assistant" / "models"
DEFAULT_PROMPT = "You are a helpful assistant. Be concise and direct. English is your primary language."

def find_model():
    """Auto-detect installed model. Returns path string or None."""
    if not MODELS_DIR.exists():
        return None
    
    models = []
    for folder in MODELS_DIR.iterdir():
        if folder.is_dir() and any(folder.glob("*.xml")): #just checking for.xml is fine because openvino is taking care of the installation
            models.append(folder)                           
    
    if len(models) == 1:
        return str(models[0])
    if len(models) > 1:
        return str(models[0])  # use first found else user can override with --model
    return None

@dataclass
class Config:
    name: str = "Assistant"
    system_prompt: str = DEFAULT_PROMPT
    device: str = "NPU"
    model_path: str = None
    do_sample: bool = False
    max_new_tokens: int = 512
    rep_penalty: float = 1.1

    
        