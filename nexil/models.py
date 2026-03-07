from pathlib import Path
from rich.console import Console
from rich.table import Table
from .config import save_model_path, load_config
from InquirerPy import inquirer

MODELS_DIR = Path.home() / ".cache" / "nexil" / "models"


def get_installed_models():
      """Returns list of model folders."""
      if not MODELS_DIR.exists():
          return []
      models = []
      for folder in MODELS_DIR.iterdir():
          if folder.is_dir() and any(folder.glob("*.xml")):
              models.append(folder)
      return models


def find_model():
    """Auto-detect installed model. Returns path string or None."""
    models = get_installed_models()

    if len(models) == 1:
        return str(models[0])

    return None


def select_model(current_path=None):
    """Show model table and selection prompt. Returns selected model path string, or None if cancelled."""
    models = get_installed_models()

    if not models:
        console = Console()
        console.print("[red]No models installed.[/red] Download one first:")
        console.print("  nexil download --model-id Qwen/Qwen2.5-3B-Instruct")
        return None

    active_path = current_path

    table = Table()
    table.add_column("Models Onboard", justify="left", style="cyan", no_wrap=True)
    table.add_column("", justify="left", no_wrap=True)
    for model in models:
        if str(model) == active_path:
            table.add_row(f"[bold green]{model.name}[/bold green]", "[bold green]Active[/bold green]")
        else:
            table.add_row(model.name, "")

    console = Console()
    console.print(table)

    choices = [model.name for model in models]
    choices.append("Exit")
    selected = inquirer.select(
        message="Select a model:",
        choices=choices,
    ).execute()

    if selected == "Exit":
        return None

    for model in models:
        if model.name == selected:
            return str(model)

    return None


def cmd_model():
    """ Display downloaded models and choose what to use in runtime"""
    config = load_config()
    selected = select_model(current_path=config.model_path)
    if selected:
        save_model_path(selected)
        print(f"Model set to: {Path(selected).name}")

    