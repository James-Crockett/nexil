```
 ███╗   ██╗ ███████╗ ██╗  ██╗ ██╗ ██╗
 ████╗  ██║ ██╔════╝ ╚██╗██╔╝ ██║ ██║
 ██╔██╗ ██║ █████╗    ╚███╔╝  ██║ ██║
 ██║╚██╗██║ ██╔══╝    ██╔██╗  ██║ ██║
 ██║ ╚████║ ███████╗ ██╔╝ ██╗ ██║ ███████╗
 ╚═╝  ╚═══╝ ╚══════╝ ╚═╝  ╚═╝ ╚═╝ ╚══════╝
```

A personal assistant that runs locally on your machine with a familiar CLI interface.

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
nexil download --model-id Qwen/Qwen3.5-4B
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

## License

Apache 2.0 — see [LICENSE](LICENSE) for details.
