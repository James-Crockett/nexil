from .cli import cmd_chat
from .config import load_config
from .devices import cmd_devices
from .download import cmd_download, DEFAULT_MODEL_ID
from .models import find_model, cmd_model, MODELS_DIR
import argparse
from pathlib import Path

def main():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="command")

    #parsers for chat
    chat_parser = subparsers.add_parser("chat")
    chat_parser.add_argument("--model", default=None)
    chat_parser.add_argument("--device", default=None)

    #parsers for downloads
    dl_parser = subparsers.add_parser("download")
    dl_parser.add_argument("--model-id", default=DEFAULT_MODEL_ID)
    dl_parser.add_argument("--output", default=None)

    #parser for device
    subparsers.add_parser("devices")

    #parser for models
    subparsers.add_parser("models")

    args = parser.parse_args()

    if args.command == "devices":
        cmd_devices()
    elif args.command == "download":
        output_dir = Path(args.output) if args.output else None
        cmd_download(args.model_id, output_dir)
    elif args.command == "models":
        cmd_model()
    else:
        config = load_config()

        # CLI args override config
        if hasattr(args, 'model') and args.model:
            config.model_path = args.model
        elif config.model_path is None:
            config.model_path = find_model()

        if hasattr(args, 'device') and args.device:
            config.device = args.device

        if config.model_path is None:
            print("No model found. Install one first:")
            print(f"  npu-assistant download --model-id Qwen/Qwen3.5-4B")
            print(f"\nModels are stored in: {MODELS_DIR}")
            return

        cmd_chat(config)