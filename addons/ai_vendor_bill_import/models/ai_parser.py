from .ai_client import extract_invoice_data
from .regex_parser import parse_with_regex


def parse_invoice_text(text):
    data = extract_invoice_data(text)

    if data:
        return data

    return parse_with_regex(text)