import openvino_genai as ov_genai
import json
import re
import time
from pathlib import Path
from .tools import get_all_tools, execute_tool
from .streamer import ThinkingStreamer


def detect_model_caps(model_path):
    """Auto-detect model capabilities from tokenizer metadata."""
    caps = {"thinks": False, "native_tools": False}

    if not model_path:
        return caps
    tok_config = Path(model_path) / "tokenizer_config.json"

    if not tok_config.exists():
        return caps

    try:
        with open(tok_config) as f:
            data = json.load(f)
    except (json.JSONDecodeError, OSError):
        return caps
    added = data.get("added_tokens_decoder", {})

    for token_info in added.values():
        token = token_info.get("content")
        if token == "<think>":
            caps["thinks"] = True
        elif token == "<tool_call>":
            caps["native_tools"] = True
    return caps


def parse_tool_call(response):
    """Check if the model's response contains a tool call. Returns dict with name/arguments or None."""
    # Try native <tool_call> format first
    match = re.search(r'<tool_call>\s*(.*?)\s*</tool_call>', response, re.DOTALL)
    if match:
        try:
            data = json.loads(match.group(1))
            if isinstance(data, dict) and "name" in data:
                return {"name": data["name"], "arguments": data.get("arguments", {})}
        except json.JSONDecodeError:
            pass

    # Fallback: ```json``` code blocks
    json_blocks = re.findall(r'```(?:\w*)\n?(.*?)```', response, re.DOTALL)
    for block in json_blocks:
        try:
            data = json.loads(block.strip())
            if isinstance(data, dict):
                if "function" in data and "name" in data["function"]:
                    return {"name": data["function"]["name"], "arguments": data["function"].get("arguments", {})}
                if "name" in data:
                    return {"name": data["name"], "arguments": data.get("arguments", {})}
                if "tool_used" in data:
                    return {"name": data["tool_used"], "arguments": data.get("arguments", {})}
        except json.JSONDecodeError:
            continue
    return None


def build_system_prompt(config):
    """Build system prompt with tool descriptions. Uses native format if model supports it."""
    tools = get_all_tools()

    if config.native_tools:
        tools_json = "\n".join(json.dumps(t, ensure_ascii=False) for t in tools)
        return (
            config.system_prompt
            + "\n\n# Tools\n\nYou have access to tools. Only use them when the user's request requires it. Do not use tools for greetings or general conversation.\n\n"
            + "You are provided with function signatures within <tools></tools> XML tags:\n"
            + f"<tools>\n{tools_json}\n</tools>\n\n"
            + "For each function call, return a json object with function name and arguments "
            + "within <tool_call></tool_call> XML tags:\n"
            + "<tool_call>\n"
            + '{"name": <function-name>, "arguments": <args-json-object>}\n'
            + "</tool_call>"
        )

    # Fallback prompt-based format for models without native tool calling
    tool_names = [f"- {t['function']['name']}: {t['function']['description']}" for t in tools]
    tool_list_str = "\n".join(tool_names)
    return (
        config.system_prompt
        + f"\n\nYou have access to these tools:\n{tool_list_str}\n\n"
        + "IMPORTANT RULES:\n"
        + "- For normal conversation (greetings, questions, chitchat), just respond naturally in plain text. NEVER output JSON for normal conversation.\n"
        + "- ONLY use a tool when the user explicitly asks for something the tool provides (e.g. asking for the current time/date).\n"
        + "- When you do need a tool, reply with ONLY this format and nothing else:\n"
        + "```json\n"
        + '{{"tool_used": "tool_name", "arguments": {{}}}}\n'
        + "```"
    )


def handle_response(pipe, history, gen_config, config):
    """Generate a response, handle tool calls if present. Returns (history, elapsed, perf_metrics)."""
    start = time.monotonic()
    response_tokens = []
    streamer = ThinkingStreamer(response_tokens, config.thinks, config.native_tools)
    result = pipe.generate(history, generation_config=gen_config, streamer=streamer)
    streamer.flush()
    full_response = "".join(response_tokens)

    tool_call = parse_tool_call(full_response)

    if tool_call is None:
        elapsed = time.monotonic() - start
        history.append({"role": "assistant", "content": full_response})
        return history, elapsed, result.perf_metrics

    # Tool call detected — run the tool
    if not config.native_tools:
        streamer.erase_response()
    tool_name = tool_call["name"]
    tool_args = tool_call.get("arguments", {})
    tool_result = execute_tool(tool_name, tool_args)

    # Feed tool result back and generate a natural follow-up
    if config.native_tools:
        history.append({"role": "assistant", "content": full_response})
        history.append({"role": "user", "content": f"<tool_response>\n{tool_result}\n</tool_response>"})
    else:
        history.append({"role": "assistant", "content": f"[Called {tool_name}]"})
        history.append({"role": "user", "content": f"Tool result: {tool_result}\nRespond naturally using this information. Be brief."})

    response_tokens = []
    streamer = ThinkingStreamer(response_tokens, config.thinks, config.native_tools)

    result = pipe.generate(history, generation_config=gen_config, streamer=streamer)
    streamer.flush()
    elapsed = time.monotonic() - start

    full_response = "".join(response_tokens)

    history.append({"role": "assistant", "content": full_response})

    return history, elapsed, result.perf_metrics
