import json
import os


def extract_invoice_data(text):
    """
    Main AI extraction entry point.
    If AI is not configured, return empty dict so regex fallback can run.
    """
    if not text:
        return {}

    api_key = os.getenv("OPENAI_API_KEY")

    if not api_key:
        return {}

    # AI integration will be added here
    return {}