"""Tool registry — stores tools and runs them by name."""

import json
from .datetime_tool import TOOL as datetime_tool

# All registered tools
TOOLS = {}
TOOLS[datetime_tool["name"]] = datetime_tool


def get_all_tools():
    """Return tool definitions for the model."""
    tool_list = []
    for tool in TOOLS.values():
        tool_list.append({
            "type": "function",
            "function": {
                "name": tool["name"],
                "description": tool["description"],
                "parameters": tool["parameters"],
            },
        })
    return tool_list


def get_tool_descriptions():
    """Return (name, description) pairs for display."""
    result = []
    for tool in TOOLS.values():
        result.append((tool["name"], tool["description"]))
    return result


def execute_tool(name, arguments="{}"):
    """Run a tool by name and return the result as a string."""
    if name not in TOOLS:
        return json.dumps({"error": f"Unknown tool: {name}"})

    tool = TOOLS[name]
    handler = tool["handler"]

    if isinstance(arguments, str):
        try:
            args = json.loads(arguments)
        except json.JSONDecodeError:
            args = {}
    else:
        args = arguments

    try:
        return handler(**args)
    except TypeError:
        return json.dumps({"error": f"Invalid arguments for tool: {name}"})
