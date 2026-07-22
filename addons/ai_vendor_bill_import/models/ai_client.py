import json
import requests


OLLAMA_URL = "http://host.docker.internal:11434/api/generate"
OLLAMA_MODEL = "llama3.2"


def extract_invoice_data(text):
    if not text:
        return {}

    prompt = f"""
        You are an invoice parser.

        Extract the following fields from the OCR text.

        Return ONLY valid JSON.

        {{
            "vendor_name": string or null,
            "vendor_vat" : string or null,
            "invoice_number": string or null,
            "invoice_date": string or null,
            "base_amount": number or null,
            "tax_amount": number or null,
            "total_amount": number or null,
            "lines": [
                {{
                    "description": string,
                    "quantity": number,
                    "unit_price": number,
                    "tax_rate": number or null
                }}
            ]
        }}

        Rules:
        - vendor_name = company issuing the invoice.
        - vendor_vat = VAT/NIF/tax identification number of the company issuing the invoice.
        - Never extract summary or total rows as invoice lines.
        - Ignore rows containing labels such as Base imposable, Quota IVA, Subtotal, Tax, VAT amount, Total, Grand Total, Import total or Amount due.- Ignore the customer's VAT/NIF.
        - Ignore customer information.
        - invoice_number = invoice or quotation number.
        - invoice_date = ISO format YYYY-MM-DD.
        - base_amount = subtotal before taxes.
        - tax_amount = VAT amount.
        - total_amount = grand total.
        - Extract every invoice line.
        - Ignore headers, totals and notes.
        - description = product or service description.
        - quantity = quantity purchased.
        - unit_price = unit price before taxes.
        - Return an empty array if no lines are found.
        - tax_rate = VAT percentage applied to the line, for example 21, 10 or 4.
        - If only one VAT rate appears in the document, apply it to all lines.
        - Never extract summary rows such as "Base imposable", "Quota IVA", or "Total" as invoice lines, even if they appear in the OCR text.

        OCR:

        {text}
"""

    try:
        response = requests.post(
            OLLAMA_URL,
            json={
                "model": OLLAMA_MODEL,
                "prompt": prompt,
                "stream": False,
            },
            timeout=60,
        )
        response.raise_for_status()

        ollama_data = response.json()
        raw_response = ollama_data.get("response", "").strip()

        print("OLLAMA RAW RESPONSE:", raw_response)

        return extract_json(raw_response)

    except Exception as e:
        print(f"OLLAMA ERROR: {e}")
        return {}
    

def extract_json(raw_text):
    start = raw_text.find("{")
    end = raw_text.rfind("}")

    if start == -1 or end == -1:
        return {}

    json_text = raw_text[start:end + 1]

    try:
        return json.loads(json_text)
    except Exception as e:
        print(f"JSON PARSE ERROR: {e}")
        return {}
    