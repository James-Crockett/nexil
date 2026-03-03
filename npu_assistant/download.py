from pathlib import Path
import subprocess

OUTPUT_DIR = Path.home() / ".cache" / "npu-assistant" / "models" / "Qwen2.5-3B-Instruct-int4-ov"

def cmd_download(model_id, output_dir):
    """ Checks if model exists else creates new"""
    
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
