import openvino_genai as ov_genai
import json
import re
from pathlib import Path
from .tools import get_all_tools, execute_tool
from .streamer import ThinkingStreamer

def parse_tool_call(response):
    """Check if the model's response contains a <tool_call> block. Returns dict with name/arguments or None."""
    match = re.search(r'<tool_call>\s*(.*?)\s*</tool_call>', response, re.DOTALL)
    if not match:
        return None
    try:
        data = json.loads(match.group(1))
        if isinstance(data, dict) and "name" in data:
            return {"name": data["name"], "arguments": data.get("arguments", {})}
    except json.JSONDecodeError:
        pass
    return None


def build_system_prompt(config):
    """Build system prompt with tool descriptions in Qwen3's native format."""
    tools = get_all_tools()
    tools_json = "\n".join(json.dumps(t, ensure_ascii=False) for t in tools)
    return (
        config.system_prompt
        + "\n\n# Tools\n\nYou may call one or more functions to assist with the user query.\n\n"
        + "You are provided with function signatures within <tools></tools> XML tags:\n"
        + f"<tools>\n{tools_json}\n</tools>\n\n"
        + "For each function call, return a json object with function name and arguments "
        + "within <tool_call></tool_call> XML tags:\n"
        + "<tool_call>\n"
        + '{"name": <function-name>, "arguments": <args-json-object>}\n'
        + "</tool_call>"
    )


def handle_command(user_input, history, system_prompt):
    """Handle slash commands. Returns (should_break, history)."""
    if user_input == "/quit":
        print("Bye Bye!")
        return True, history
    elif user_input == "/clear":
        history = ov_genai.ChatHistory()
        history.append({"role": "system", "content": system_prompt})
        print("History cleared.")
        return False, history
    else:
        print("Unknown command:", user_input)
        return False, history


def handle_response(pipe, history, gen_config):
    """Generate a response, handle tool calls if present. Returns updated history."""
    response_tokens = []
    streamer = ThinkingStreamer(response_tokens)
    pipe.generate(history, generation_config=gen_config, streamer=streamer)
    streamer.flush()
    full_response = "".join(response_tokens)

    tool_call = parse_tool_call(full_response)

    if tool_call is None:
        print()
        history.append({"role": "assistant", "content": full_response})
        return history

    # Tool call detected — run the tool (streamer already suppressed the raw JSON)
    tool_name = tool_call["name"]
    tool_args = tool_call.get("arguments", {})
    result = execute_tool(tool_name, tool_args)

    # Feed tool result back using native format and generate a natural follow-up
    history.append({"role": "assistant", "content": full_response})
    history.append({"role": "user", "content": f"<tool_response>\n{result}\n</tool_response>"})
    response_tokens = []
    streamer = ThinkingStreamer(response_tokens)
    pipe.generate(history, generation_config=gen_config, streamer=streamer)
    streamer.flush()
    full_response = "".join(response_tokens)
    history.append({"role": "assistant", "content": full_response})
    print()
    return history


def cmd_chat(config):
    """Chat things """
    # NPU-specific options (MAX_PROMPT_LEN, MIN_RESPONSE_LEN only work on NPU)
    # 9s to load without cache, around 3s with
    cache_dir = str(Path.home() / ".cache" / "npu-assistant" / "compiled")
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
    history = ov_genai.ChatHistory()
    system_prompt = build_system_prompt(config)
    history.append({"role": "system", "content": system_prompt})

    gen_config = ov_genai.GenerationConfig()
    gen_config.max_new_tokens = config.max_new_tokens
    gen_config.do_sample = config.do_sample
    gen_config.repetition_penalty = config.rep_penalty

    while True:
        user_input = input("> ")

        if user_input.startswith("/"):
            should_break, history = handle_command(user_input, history, system_prompt)
            if should_break:
                break
            continue

        history.append({"role": "user", "content": user_input})
        history = handle_response(pipe, history, gen_config)




