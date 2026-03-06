from datetime import datetime


def get_current_datetime():
    """Returns current date, time, and day of week."""
    now = datetime.now()
    return now.strftime("%A, %B %d, %Y — %I:%M %p")


TOOL = {
    "name": "get_current_datetime",
    "description": "Get the current date, time, and day of week",
    "parameters": {"type": "object", "properties": {}},
    "handler": get_current_datetime,
}
