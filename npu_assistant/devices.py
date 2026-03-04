import openvino as ov
from rich.console import Console
from rich.table import Table
from .config import load_config, save_device
from InquirerPy import inquirer

#Openvino can detect gpus but cannot run on them, will work with Intel GPUs
UNSUPPORTED_DEVICES = {"GPU"}


def cmd_devices():
    """ List out the devices onboard"""
    core = ov.Core()
    devices = core.available_devices
    config = load_config()

    table = Table()
    table.add_column("Devices Onboard", justify="right", style="cyan", no_wrap=True)
    table.add_column("Device Name", justify="right", style="cyan", no_wrap=True)
    table.add_column("", justify="left", no_wrap=True)
    for device in devices:
        device_name = core.get_property(device, "FULL_DEVICE_NAME")
        if device == config.device:
            table.add_row(f"[bold green]{device}[/bold green]", f"[bold green]{device_name}[/bold green]", "[bold green]Active[/bold green]")
        elif device in UNSUPPORTED_DEVICES:
            table.add_row(f"[dim][grey62]{device}[/grey62][/dim]", f"[dim][grey62]{device_name}[/grey62][/dim]", "[red]Unsupported[/red]")
        else:
            table.add_row(f"[cyan]{device}[/cyan]", f"[cyan]{device_name}[/cyan]", "[cyan]Inactive[/cyan]")

    console = Console()
    console.print(table)

    #picking supported devices
    supported = []
    for d in devices:
        if d not in UNSUPPORTED_DEVICES:
            supported.append(d)
    if supported:
        supported.append("Exit") #additional option
        selected = inquirer.select(
            message="Select a device:",
            choices=supported,
        ).execute()
        if selected == "Exit": # if user wants to do nothing
            return
        save_device(selected)
        print(f"Device set to: {selected}")