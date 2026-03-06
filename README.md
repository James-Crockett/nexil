# Nexil

A personal assistant that runs locally on your machine with a familiar CLI interface.

## Features

- Run LLMs locally on Intel NPU and GPU. (GPU not supported as of now but could theoritically work).
- Native tool calling (Ex: date/time lookups, only tool as of now)
- Rich terminal UI with streaming responses
- Download and manage OpenVINO-optimized models
- Configurable via TOML

## Requirements

- Linux (tested on Arch based system)
- Python 3.12+
- Intel hardware. (e.g., Core Ultra) (ONLY SUPPORTS INTEL BASED CPU AND NPU)
- OpenVINO runtime

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
