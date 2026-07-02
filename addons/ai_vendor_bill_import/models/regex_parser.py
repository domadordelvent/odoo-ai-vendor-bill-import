import re

def parse_with_regex(text):
    if not text:
        return {}

    return {
        "vendor_name": extract_vendor_name(text),
        "invoice_number": extract_invoice_number(text),
        "invoice_date": extract_invoice_date(text),
        "base_amount": extract_amount(text, ["base", "subtotal", "importe neto", "base imponible"]),
        "tax_amount": extract_amount(text, ["iva", "vat", "tax"]),
        "total_amount": extract_amount(text, ["total", "importe total", "total factura"]),
    }


def extract_vendor_name(text):
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    return lines[0] if lines else ""


def extract_invoice_number(text):
    patterns = [
        r"(?:factura|invoice|n[úu]mero|num\.?)\s*[:\-]?\s*([A-Z0-9\-\/]+)",
        r"(?:invoice\s*no\.?)\s*[:\-]?\s*([A-Z0-9\-\/]+)",
    ]

    return find_first_match(text, patterns)


def extract_invoice_date(text):
    patterns = [
        r"(\d{1,2}[\/\-]\d{1,2}[\/\-]\d{2,4})",
        r"(\d{4}[\/\-]\d{1,2}[\/\-]\d{1,2})",
    ]

    return find_first_match(text, patterns)


def extract_amount(text, keywords):
    for keyword in keywords:
        pattern = rf"{keyword}\s*[:\-]?\s*([0-9]+(?:[.,][0-9]{{2}})?)"
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return normalize_amount(match.group(1))

    return 0.0


def find_first_match(text, patterns):
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return match.group(1).strip()
    return ""


def normalize_amount(value):
    value = value.replace(".", "").replace(",", ".")
    try:
        return float(value)
    except ValueError:
        return 0.0