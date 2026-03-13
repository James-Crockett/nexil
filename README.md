```
 ███╗   ██╗ ███████╗ ██╗  ██╗ ██╗ ██╗
 ████╗  ██║ ██╔════╝ ╚██╗██╔╝ ██║ ██║
 ██╔██╗ ██║ █████╗    ╚███╔╝  ██║ ██║
 ██║╚██╗██║ ██╔══╝    ██╔██╗  ██║ ██║
 ██║ ╚████║ ███████╗ ██╔╝ ██╗ ██║ ███████╗
 ╚═╝  ╚═══╝ ╚══════╝ ╚═╝  ╚═╝ ╚═╝ ╚══════╝
```

A personal assistant that runs locally on your machine with a familiar CLI interface.

## Reason for project existence 
> (Skip if you want, not necessary to read)

My laptop has a NPU and it does nothing. So, I did some research and I thought it would be a cool project to run a local llm that can do stuff locally (tool callls and what not), espcially with OpenClaw being a big hype rn, I decided to do it... and this is the result of it. Since, I have an Intel processor I went with OpenVino as the base (I plan to support all hardware and brands). But, from what I know this is the only way to run stuff of the NPU. Some people said stuff about Onnx runtime would work but I dont know. I have a lot of ideas to make this tool more use full. As of now it only tells time (lmao). I feel this project has a lot of potential. Let's see where this goes.

https://github.com/user-attachments/assets/97170686-7d46-496d-9d75-3636a5f5ab51

## Features

- Run LLMs locally on Intel NPU and GPU. (GPU not supported as of now but could theoritically work).
- Native tool calling (Ex: date/time lookups, only tool as of now)
- Rich terminal UI with streaming responses
- Download and manage OpenVINO-optimized models
- Configurable via TOML

## Requirements

- Linux (tested on Arch based system, should work on any distro)
- Python 3.12+
- Intel Core Ultra processor (Meteor Lake / Lunar Lake) for NPU support
- Intel NPU driver
- OpenVINO runtime (installed automatically via pip)

### NPU driver setup

The Intel NPU driver is required to run models on the NPU. Without it, you can still run on CPU.

**Arch Linux (AUR):**
```sh
yay -S intel-npu-driver
```
or 

```sh
paru -S intel-npu-driver
```
**Ubuntu/Debian:**

Download the latest `.deb` packages from the [intel-npu-driver releases](https://github.com/intel/linux-npu-driver/releases) and install:
```sh
sudo dpkg -i intel-driver-compiler-npu_*.deb intel-fw-npu_*.deb intel-level-zero-npu_*.deb
```

**Fedora:**

Download the latest `.rpm` packages from the [intel-npu-driver releases](https://github.com/intel/linux-npu-driver/releases) and install:
```sh
sudo rpm -i intel-driver-compiler-npu-*.rpm intel-fw-npu-*.rpm intel-level-zero-npu-*.rpm
```

After installing the driver, add your user to the `render` group to access the NPU device:
```sh
sudo usermod -aG render $USER
```
Log out and back in for the group change to take effect.

You can verify the NPU is available by running:
```sh
nexil devices
```

## Installation

From PyPI:

```sh
pip install nexil
```

From GitHub:

```sh
pip install git+https://github.com/James-Crockett/nexil.git
```

## Quick start

Download a model:

```sh
nexil download --model-id Qwen/Qwen3-4B
```
> Thinking models work better with this application, so I'd recommed it. Instruct models do work but not well with the tools.

Start the assistant:

```sh
nexil
```

Or launch the CLI chat directly:

```sh
nexil chat
```

## Commands

| Command | Description |
|---------|-------------|
| `nexil` | Start the chat assistant |
| `nexil chat` | Start CLI chat mode |
| `nexil download` | Download a model |
| `nexil models` | List installed models |
| `nexil devices` | List available devices |

### Chat commands

| Command | Description |
|---------|-------------|
| `/help` | Show available commands |
| `/model` | Switch model |
| `/device` | Switch device |
| `/clear` | Clear chat history |
| `/quit` | Exit the assistant |

## Configuration

Config file: `~/.config/nexil/config.toml`

```toml
model_path = "/path/to/model"
device = "NPU"
```

## NPU Monitoring Tool:

https://github.com/DMontgomery40/intel-npu-top

## License

Apache 2.0 — see [LICENSE](LICENSE) for details.
