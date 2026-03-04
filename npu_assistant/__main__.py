from .chat import cmd_chat
from .config import Config, find_model, MODELS_DIR
from .devices import cmd_devices
from .download import cmd_download, DEFAULT_MODEL_ID

import argparse
from pathlib import Path

def main():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="command")

    #adding subparsers
    chat_parser = subparsers.add_parser("chat")
    chat_parser.add_argument("--model", default=None)
    chat_parser.add_argument("--device", default=None)

    dl_parser = subparsers.add_parser("download")
    dl_parser.add_argument("--model-id", default=DEFAULT_MODEL_ID)
    dl_parser.add_argument("--output", default=None)

    subparsers.add_parser("devices")

    args = parser.parse_args()

    if args.command == "devices":
        cmd_devices()
    elif args.command == "download":
        output_dir = Path(args.output) if args.output else None
        cmd_download(args.model_id, output_dir)
    else:
        config = Config()

        # CLI args override defaults
        if hasattr(args, 'model') and args.model:
            config.model_path = args.model
        else:
            config.model_path = find_model()
            
        if hasattr(args, 'device') and args.device:
            config.device = args.device

        if config.model_path is None:
            print("No model found. Install one first:")
            print(f"  npu-assistant download --model-id Qwen/Qwen3.5-4B")
            print(f"\nModels are stored in: {MODELS_DIR}")
            return

        cmd_chat(config)