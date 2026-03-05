import openvino_genai as ov_genai
import json
import re
from pathlib import Path
from .tools import get_all_tools, execute_tool

def parse_tool_call(response):
    """Check if the model's response contains a tool call. Returns dict with name/arguments or None."""
    # Look for JSON blocks containing "function" and "name"
    # The model outputs JSON in code blocks like ```...```
    json_blocks = re.findall(r'```(?:\w*)\n?(.*?)```', response, re.DOTALL)
    for block in json_blocks:
        try:
            data = json.loads(block.strip())
            # Format: {"type": "function", "function": {"name": "..."}}
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
    # Add tool descriptions to system prompt so model knows what's available
    tools = get_all_tools()
    # Build compact tool list for prompt
    tool_names = []
    for t in tools:
        tool_names.append(f"- {t['function']['name']}: {t['function']['description']}")
    tool_list_str = "\n".join(tool_names)

    tool_prompt = config.system_prompt + f"\n\nTools available:\n{tool_list_str}\n\nTo use a tool, reply with ONLY:\n```json\n{{\"tool_used\": \"tool_name\", \"arguments\": {{}}}}\n```\nNo other text. Wait for the result."
    history.append({"role": "system", "content": tool_prompt})

    while True:
        user_input = input("> ")

        #checks for slash
        if user_input.startswith("/"):
            if user_input == "/quit":
                print("Bye Bye!")
                break
            elif user_input == "/clear":
                history = ov_genai.ChatHistory()
                history.append({"role": "system", "content": tool_prompt})
                print("History cleared.")
                continue
            else:                                                                                                                           
                  print("Unknown command:", user_input)
                  continue   
            
        history.append({"role": "user", "content": user_input})

        #generation config
        gen_config = ov_genai.GenerationConfig()
        gen_config.max_new_tokens = config.max_new_tokens
        gen_config.do_sample = config.do_sample
        gen_config.repetition_penalty = config.rep_penalty

        # First generation — silent (don't stream), check for tool call
        response_tokens = []

        def silent_streamer(token):
            response_tokens.append(token)
            return False

        def loud_streamer(token):
            response_tokens.append(token)
            print(token, end="", flush=True)
            return False

        pipe.generate(history, generation_config=gen_config, streamer=silent_streamer)
        full_response = "".join(response_tokens)

        # Check if the response contains a tool call
        tool_call = parse_tool_call(full_response)

        if tool_call is None:
            # No tool call — just print the response
            print(full_response)
            history.append({"role": "assistant", "content": full_response})
        else:
            # Tool call detected — run it silently, then generate a visible response
            tool_name = tool_call["name"]
            tool_args = tool_call.get("arguments", {})
            result = execute_tool(tool_name, tool_args)

            # Feed tool result back and generate a natural response (streamed)
            history.append({"role": "assistant", "content": f"[Called {tool_name}]"})
            history.append({"role": "user", "content": f"Tool result: {result}\nRespond naturally using this information. Be brief."})
            response_tokens = []
            pipe.generate(history, generation_config=gen_config, streamer=loud_streamer)
            full_response = "".join(response_tokens)
            history.append({"role": "assistant", "content": full_response})
            print()




