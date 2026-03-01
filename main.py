#!/usr/bin/env python3
"""NPU Personal Assistant — local LLM chat powered by Intel NPU via OpenVINO."""

import argparse
import subprocess
import sys
from pathlib import Path

DEFAULT_MODEL_ID = "Qwen/Qwen2.5-3B-Instruct"
DEFAULT_MODEL_DIR = Path.home() / ".cache" / "npu-assistant" / "models" / "Qwen2.5-3B-Instruct-int4-ov"
DEFAULT_DEVICE = "NPU"


def cmd_devices(args):
    """List available OpenVINO devices."""
    import openvino as ov

    core = ov.Core()
    devices = core.available_devices

    from rich.console import Console
    from rich.table import Table

    console = Console()
    table = Table(title="Available OpenVINO Devices")
    table.add_column("Device", style="bold cyan")
    table.add_column("Full Name")

    for device in devices:
        try:
            full_name = core.get_property(device, "FULL_DEVICE_NAME")
        except Exception:
            full_name = ""
        table.add_row(device, full_name)

    console.print(table)


def cmd_download(args):
    """Download and export a model to OpenVINO IR format."""
    from rich.console import Console

    console = Console()
    model_id = args.model_id
    output_dir = Path(args.output)

    if output_dir.exists() and any(output_dir.glob("*.xml")):
        console.print(f"[yellow]Model already exists at {output_dir}[/yellow]")
        console.print("To re-download, delete the directory first.")
        return

    output_dir.mkdir(parents=True, exist_ok=True)

    console.print(f"[bold]Exporting [cyan]{model_id}[/cyan] to OpenVINO IR (INT4)...[/bold]")
    console.print(f"Output: {output_dir}")
    console.print("This may take 5-10 minutes.\n")

    cmd = [
        "optimum-cli", "export", "openvino",
        "--model", model_id,
        "--weight-format", "int4",
        "--sym",
        "--ratio", "1.0",
        "--group-size", "128",
        str(output_dir),
    ]

    result = subprocess.run(cmd)
    if result.returncode != 0:
        console.print("[red]Model export failed.[/red]")
        sys.exit(1)

    console.print(f"\n[green]Model exported successfully to {output_dir}[/green]")


def cmd_chat(args):
    """Interactive chat REPL."""
    import openvino_genai as ov_genai
    from rich.console import Console
    from rich.live import Live
    from rich.markdown import Markdown
    from rich.spinner import Spinner

    console = Console()
    model_path = str(Path(args.model))
    device = args.device

    if not Path(model_path).exists():
        console.print(f"[red]Model not found at {model_path}[/red]")
        console.print("Run the download command first:")
        console.print(f"  [cyan]python main.py download[/cyan]")
        sys.exit(1)

    # Load model
    with console.status(
        f"[bold cyan]Compiling model for {device}... this may take a minute on first run",
        spinner="dots",
    ):
        pipe = ov_genai.LLMPipeline(model_path, device, MAX_PROMPT_LEN=1024, MIN_RESPONSE_LEN=512)

    console.print(f"[green]Model loaded on {device}.[/green]")
    console.print("Type [bold]/quit[/bold] to exit, [bold]/clear[/bold] to reset history.\n")

    history = ov_genai.ChatHistory()

    while True:
        try:
            user_input = console.input("[bold blue]> [/bold blue]")
        except (EOFError, KeyboardInterrupt):
            console.print("\nBye!")
            break

        text = user_input.strip()
        if not text:
            continue

        # Slash commands
        if text.lower() == "/quit":
            console.print("Bye!")
            break
        if text.lower() == "/clear":
            history = ov_genai.ChatHistory()
            console.print("[dim]History cleared.[/dim]")
            continue
        if text.lower().startswith("/device"):
            parts = text.split(maxsplit=1)
            if len(parts) < 2:
                console.print(f"[dim]Current device: {device}[/dim]")
                continue
            new_device = parts[1].strip().upper()
            console.print(f"[dim]Switching to {new_device}...[/dim]")
            with console.status(f"[bold cyan]Recompiling model for {new_device}..."):
                pipe = ov_genai.LLMPipeline(model_path, new_device, MAX_PROMPT_LEN=1024, MIN_RESPONSE_LEN=512)
            device = new_device
            console.print(f"[green]Now using {device}.[/green]")
            continue

        # Build conversation prompt
        history.append({"role": "user", "content": text})

        # Stream response
        response_tokens = []

        def streamer(token):
            response_tokens.append(token)
            console.print(token, end="", highlight=False)
            return False  # continue generating

        generation_config = ov_genai.GenerationConfig()
        generation_config.max_new_tokens = 2048
        generation_config.do_sample = False

        try:
            pipe.generate(history, generation_config=generation_config, streamer=streamer)
        except Exception as e:
            console.print(f"\n[red]Generation error: {e}[/red]")
            # Remove the failed user message
            msgs = history.get_messages()
            msgs.pop()
            history.set_messages(msgs)
            continue

        full_response = "".join(response_tokens)
        history.append({"role": "assistant", "content": full_response})
        console.print()  # newline after streamed output


def main():
    parser = argparse.ArgumentParser(
        prog="npu-assistant",
        description="Local LLM chat assistant powered by Intel NPU via OpenVINO",
    )
    subparsers = parser.add_subparsers(dest="command")

    # chat (default)
    chat_parser = subparsers.add_parser("chat", help="Interactive chat REPL")
    chat_parser.add_argument(
        "--device", default=DEFAULT_DEVICE,
        help=f"OpenVINO device to use (default: {DEFAULT_DEVICE})",
    )
    chat_parser.add_argument(
        "--model", default=str(DEFAULT_MODEL_DIR),
        help="Path to OpenVINO model directory",
    )

    # download
    dl_parser = subparsers.add_parser("download", help="Download and export a model")
    dl_parser.add_argument(
        "--model-id", default=DEFAULT_MODEL_ID,
        help=f"HuggingFace model ID (default: {DEFAULT_MODEL_ID})",
    )
    dl_parser.add_argument(
        "--output", default=str(DEFAULT_MODEL_DIR),
        help="Output directory for exported model",
    )

    # devices
    subparsers.add_parser("devices", help="List available OpenVINO devices")

    args = parser.parse_args()

    if args.command is None or args.command == "chat":
        # Default to chat if no subcommand given
        if args.command is None:
            # Re-parse with chat defaults
            args.device = DEFAULT_DEVICE
            args.model = str(DEFAULT_MODEL_DIR)
        cmd_chat(args)
    elif args.command == "download":
        cmd_download(args)
    elif args.command == "devices":
        cmd_devices(args)


if __name__ == "__main__":
    main()
