from .ai_client import extract_invoice_data
from .regex_parser import parse_with_regex

import requests

from odoo.exceptions import UserError


def parse_invoice_text(text):
    if not _check_ollama():
        raise UserError(
            "Ollama server is not running.\n"
            "Start it with: ollama serve"
        )

    return extract_invoice_data(text)

def _check_ollama():
    try:
        response = requests.get(
            "http://host.docker.internal:11434/api/tags",
            timeout=3,
        )
        return response.status_code == 200
    except requests.RequestException:
        return False