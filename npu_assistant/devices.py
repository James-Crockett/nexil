import openvino as ov
from rich.console import Console
from rich.table import Table


def cmd_devices():

    #get devices
    core = ov.Core()
    devices = core.available_devices

    table = Table()
    table.add_column("Devices Onboard", justify="right", style="cyan", no_wrap=True)
    table.add_column("Device Name", justify="right", style="cyan", no_wrap=True)
    for device in devices:
        device_name = core.get_property(device, "FULL_DEVICE_NAME")
        table.add_row(device,device_name)
      
    console = Console()
    console.print(table) 