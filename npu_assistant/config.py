#imports
from pathlib import Path
from dataclasses import dataclass
import tomllib



#default config
CONFIG_PATH = Path.home() / ".config" / "npu-assistant" / "config.toml"
DEFAULT_CONFIG = """ 

[assistant]
name = "Assistant"
system_prompt = "You are a helpful assistant. Be concise and direct. English is your primary language."

[model]
device = "NPU"
do_sample = false
max_new_tokens = 512
rep_penalty = 1.1

"""

#default model settings
MODELS_DIR = Path.home() / ".cache" / "npu-assistant" / "models"
DEFAULT_PROMPT = "You are a helpful assistant. Be concise and direct. English is your primary language."



@dataclass
class Config:
    name: str = "Assistant"
    system_prompt: str = DEFAULT_PROMPT
    device: str = "NPU"
    model_path: str = None
    do_sample: bool = False
    max_new_tokens: int = 512
    rep_penalty: float = 1.1

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
                do_sample=model.get("do_sample", False),
                max_new_tokens=model.get("max_new_tokens", 512),
                rep_penalty=model.get("rep_penalty", 1.1),
            )


    
        