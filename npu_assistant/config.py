#imports
from pathlib import Path
from dataclasses import dataclass

#default settings
CONFIG_PATH = Path.home() / ".config" / "npu-assistant" / "config.toml"
DEFAULT_MODEL_PATH = Path.home() / ".cache" / "npu-assistant" / "models" / "Qwen2.5-3B-Instruct-int4-ov"
DEFAULT_PROMPT = "You are a helpful assistant. Be concise and direct"

@dataclass 
class Config:
    name: str = "Assistant"
    system_prompt: str = DEFAULT_PROMPT
    device: str = "NPU"
    model_path: str = DEFAULT_MODEL_PATH
    do_sample: bool = False
    max_new_tokens: int = 512
    rep_penalty: float = 1.1

    
        