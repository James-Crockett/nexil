from pathlib import Path
import subprocess

MODELS_DIR = Path.home() / ".cache" / "npu-assistant" / "models"
DEFAULT_MODEL_ID = "Qwen/Qwen3.5-4B"

def model_dir_from_id(model_id):
    """Build output path from model ID: Ex: 'Qwen/Qwen3.5-4B' -> '~/.cache/.../Qwen3.5-4B-int4-ov'"""
    model_name = model_id.split("/")[-1]
    return MODELS_DIR / f"{model_name}-int4-ov"

def cmd_download(model_id, output_dir=None):
    """ Checks if model exists else creates new"""
    
    if output_dir is None:
        output_dir = model_dir_from_id(model_id)

    if output_dir.exists() and any(output_dir.glob("*.xml")):
        print("Model already exists")
        return
    else:
        print("Model does not exist; Creating folder")
        output_dir.mkdir(parents=True, exist_ok=True)
        result = subprocess.run([
            "optimum-cli", "export", "openvino",
            "--model", model_id,
            "--weight-format", "int4",
            "--sym",
            "--ratio", "1.0",
            "--group-size", "128",
            str(output_dir),
        ])

        if result.returncode != 0:
            print("Model export failed")
        else:
            print("Model exported successfuly")
