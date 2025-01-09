def truncate_text(text, max_length=2000):
    return text if len(text) <= max_length else text[: max_length - 3] + "..."
