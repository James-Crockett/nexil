import openvino_genai as ov_genai
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from .chat import detect_model_caps, build_system_prompt, handle_response
from .models import select_model
from .devices import select_device
from .config import save_model_path, save_device

console = Console()


def print_banner(config):
    """Print a styled banner with model and device info."""
    model_name = Path(config.model_path).name if config.model_path else "None"
    subtitle = f"Model: [cyan]{model_name}[/cyan]  |  Device: [cyan]{config.device}[/cyan]"
    banner = Panel(
        subtitle,
        title="[bold]Nexil[/bold]",
        border_style="blue",
        padding=(0, 2),
    )
    console.print(banner)
    console.print("[dim]/help for commands, /model to switch, /quit to exit[/dim]")
    console.print()


def create_pipeline(config):
    """Create LLM pipeline with loading feedback."""
    cache_dir = str(Path.home() / ".cache" / "nexil" / "compiled")
    with console.status("Loading model...", spinner="dots"):
        if config.device == "NPU":
            pipe = ov_genai.LLMPipeline(
                config.model_path,
                config.device,
                MAX_PROMPT_LEN=2048,
                MIN_RESPONSE_LEN=512,
                CACHE_DIR=cache_dir,
            )
        else:
            pipe = ov_genai.LLMPipeline(
                config.model_path,
                config.device,
            )
    return pipe


def print_help():
    """Print a table of available commands."""
    table = Table(show_header=False, box=None, padding=(0, 2))
    table.add_column(style="bold cyan")
    table.add_column()
    table.add_row("/help", "Show this help message")
    table.add_row("/model", "Switch model")
    table.add_row("/device", "Switch device")
    table.add_row("/clear", "Clear conversation history")
    table.add_row("/quit", "Exit the assistant")
    console.print(table)


def handle_command(user_input, history, system_prompt):
    """Handle slash commands. Returns (action, history) where action is 'quit', 'clear', 'switch_model', 'switch_device', or None."""
    if user_input == "/quit":
        console.print("[dim]Bye Bye![/dim]")
        return "quit", history
    elif user_input == "/clear":
        history = ov_genai.ChatHistory()
        history.append({"role": "system", "content": system_prompt})
        console.print("[dim]History cleared.[/dim]")
        return "clear", history
    elif user_input == "/help":
        print_help()
        return None, history
    elif user_input == "/model":
        return "switch_model", history
    elif user_input == "/device":
        return "switch_device", history
    else:
        console.print(f"[red]Unknown command:[/red] {user_input}")
        return None, history


def print_stats(perf, elapsed):
    """Print generation stats: duration, input tokens, output tokens."""
    input_tokens = perf.get_num_input_tokens()
    output_tokens = perf.get_num_generated_tokens()
    console.print(f"Duration {elapsed:.2f}s | Input tokens: {input_tokens:,} | Output tokens: {output_tokens}", style="dim")


def cmd_chat(config):
    """Chat things """
    pipe = create_pipeline(config)

    caps = detect_model_caps(config.model_path)
    config.thinks = caps["thinks"]
    config.native_tools = caps["native_tools"]

    system_prompt = build_system_prompt(config)
    history = ov_genai.ChatHistory()
    history.append({"role": "system", "content": system_prompt})

    gen_config = ov_genai.GenerationConfig()
    gen_config.max_new_tokens = config.max_new_tokens
    gen_config.do_sample = config.do_sample
    gen_config.repetition_penalty = config.rep_penalty

    print_banner(config)

    while True:
        try:
            console.print("[bold cyan]>[/bold cyan] ", end="")
            user_input = input()
        except EOFError:
            console.print("\n[dim]Bye Bye![/dim]")
            break
        except KeyboardInterrupt:
            console.print()
            continue

        if not user_input.strip():
            continue

        if user_input.startswith("/"):
            action, history = handle_command(user_input, history, system_prompt)
            if action == "quit":
                break
            elif action == "switch_model":
                selected = select_model(current_path=config.model_path)
                if selected and selected != config.model_path:
                    save_model_path(selected)
                    config.model_path = selected
                    pipe = create_pipeline(config)
                    caps = detect_model_caps(config.model_path)
                    config.thinks = caps["thinks"]
                    config.native_tools = caps["native_tools"]
                    system_prompt = build_system_prompt(config)
                    history = ov_genai.ChatHistory()
                    history.append({"role": "system", "content": system_prompt})
                    console.print(f"[green]Switched to {Path(selected).name}[/green]")
            elif action == "switch_device":
                selected = select_device(current_device=config.device)
                if selected and selected != config.device:
                    save_device(selected)
                    config.device = selected
                    pipe = create_pipeline(config)
                    history = ov_genai.ChatHistory()
                    history.append({"role": "system", "content": system_prompt})
                    console.print(f"[green]Switched to {selected}[/green]")
            continue

        history.append({"role": "user", "content": user_input})
        history, elapsed, perf = handle_response(pipe, history, gen_config, config)
        print()
        print_stats(perf, elapsed)
