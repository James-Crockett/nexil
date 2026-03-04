from .chat import cmd_chat
from .config import Config
from .devices import cmd_devices
from .download import cmd_download, OUTPUT_DIR

import argparse

def main():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="command")

    #adding subparsers 
    subparsers.add_parser("chat")
    subparsers.add_parser("download")
    subparsers.add_parser("devices")

    args = parser.parse_args()

    if args.command == "devices":
        cmd_devices()
    elif args.command == "download":
        output_dir = OUTPUT_DIR
        cmd_download("Qwen/Qwen2.5-3B-Instruct", output_dir)
    else:
        config = Config()
        cmd_chat(config)