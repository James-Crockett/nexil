"""Streaming handlers for token output with thinking animation support."""

import os
import re


SPINNER_FRAMES = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]


class ThinkingStreamer:
    """Streamer that shows a rolling single-line spinner with live thinking
    text during <think> tags, then streams the actual response normally."""

    def __init__(self, token_list, thinks=False, native_tools=False):
        self.tokens = token_list
        self.thinks = thinks
        self.native_tools = native_tools
        self.buffer = ""
        self.think_line = ""
        self.inside_think = False
        self.inside_tool_call = False
        self.frame = 0
        self.printed_lines = 0  # track lines printed outside think tags

    def _render_think_line(self):
        """Render the current thinking text as a single spinner line."""
        try:
            cols = os.get_terminal_size().columns
        except OSError:
            cols = 80

        frame = SPINNER_FRAMES[self.frame % len(SPINNER_FRAMES)]
        self.frame += 1

        prefix = f"{frame} Thinking: "
        max_text = cols - len(prefix) - 3  # room for "..."
        text = self.think_line.replace("\n", " ")

        if max_text > 0 and len(text) > max_text:
            display = prefix + "..." + text[-(max_text):]
        else:
            display = prefix + text

        # Pad to terminal width to clear leftover chars, then return to start
        print(f"\r\033[90m{display:<{cols}}\033[0m", end="", flush=True)

    def _clear_line(self):
        """Clear the spinner line."""
        try:
            cols = os.get_terminal_size().columns
        except OSError:
            cols = 80
        print("\r" + " " * cols + "\r", end="", flush=True)

    def __call__(self, token):
        self.tokens.append(token)
        self.buffer += token

        # Check for <think> opening tag (only if model supports thinking)
        if self.thinks and "<think>" in self.buffer and not self.inside_think:
            self.inside_think = True
            self.buffer = self.buffer.split("<think>", 1)[1]
            self.think_line = ""
            self._render_think_line()
            return False

        # Check for </think> closing tag
        if "</think>" in self.buffer and self.inside_think:
            self.inside_think = False
            self._clear_line()
            after = self.buffer.split("</think>", 1)[1]
            self.buffer = ""
            if after.strip():
                self.printed_lines += after.count("\n")
                print(after, end="", flush=True)
            return False

        # Inside think tags — update the rolling spinner line
        if self.inside_think:
            text = self.buffer
            self.buffer = ""
            # On newline, reset the thinking line to show fresh thought
            if "\n" in text:
                # Keep only text after the last newline
                self.think_line = text.rsplit("\n", 1)[1]
            else:
                self.think_line += text
            self._render_think_line()
            return False

        # Check for <tool_call> opening tag (only if model supports native tools)
        if self.native_tools and "<tool_call>" in self.buffer and not self.inside_tool_call:
            self.inside_tool_call = True
            self.buffer = self.buffer.split("<tool_call>", 1)[1]
            return False

        # Check for </tool_call> closing tag
        if "</tool_call>" in self.buffer and self.inside_tool_call:
            self.inside_tool_call = False
            after = self.buffer.split("</tool_call>", 1)[1]
            self.buffer = after
            # Fall through to print anything after the closing tag

        # Inside tool_call tags — silently consume
        if self.inside_tool_call:
            self.buffer = ""
            return False

        # Outside think/tool_call tags — wait for partial tags to resolve
        if "<" in self.buffer and not self.buffer.endswith(">"):
            return False

        self.printed_lines += self.buffer.count("\n")
        print(self.buffer, end="", flush=True)
        self.buffer = ""
        return False

    def erase_response(self):
        """Erase all non-think output that was printed (e.g. tool call JSON)."""
        try:
            cols = os.get_terminal_size().columns
        except OSError:
            cols = 80
        print("\r" + " " * cols + "\r", end="", flush=True)
        for _ in range(self.printed_lines):
            print("\033[A\033[2K", end="", flush=True)
        self.printed_lines = 0

    def flush(self):
        """Print any remaining buffer content."""
        if self.inside_think:
            self._clear_line()
        if self.buffer and not self.inside_think:
            cleaned = re.sub(r'</?think>', '', self.buffer)
            if cleaned.strip():
                self.printed_lines += cleaned.count("\n")
                print(cleaned, end="", flush=True)
        self.buffer = ""
