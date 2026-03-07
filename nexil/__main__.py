from .cli import cmd_chat, print_banner
from .config import load_config
from .devices import cmd_devices
from .download import cmd_download, DEFAULT_MODEL_ID
from .models import find_model, cmd_model, MODELS_DIR
import argparse
from pathlib import Path
from rich.console import Console

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

        print_banner(config)

        if config.model_path is None:
            console = Console()
            console.print("[yellow]No model found.[/yellow] Download one to get started:\n")
            console.print(f"  [cyan]nexil download --model-id Qwen/Qwen3-4B[/cyan]\n")
            console.print(f"[dim]Models are stored in: {MODELS_DIR}[/dim]")
            return

        cmd_chat(config)