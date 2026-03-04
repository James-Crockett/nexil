from pathlib import Path
from rich.console import Console
from rich.table import Table
from .config import save_model_path, load_config
from InquirerPy import inquirer

MODELS_DIR = Path.home() / ".cache" / "npu-assistant" / "models"


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
    
    if not MODELS_DIR.exists():
        return None
    
    if len(models) == 1:
        return str(models[0])

    return str(models[0])


def cmd_model():
    """ Display downloaded models and choose what to use in runtime"""
    models = get_installed_models()

    if not models:
        print("No models installed. Download one first:")
        print("  npu-assistant download --model-id Qwen/Qwen2.5-3B-Instruct")
        return

    #show downloaded models, highlight active model
    config = load_config()
    active_path = config.model_path

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

    #picking model
    choices = [model.name for model in models]
    selected = inquirer.select(
        message="Select a model:",
        choices=choices,
    ).execute()

    for model in models:
        if model.name == selected:
            save_model_path(str(model))
            print(f"Model set to: {selected}")
            break

    