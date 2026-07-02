import base64
import tempfile
from pathlib import Path
from .ai_parser import parse_invoice_text

from odoo import models, fields
from odoo.exceptions import UserError

from ..ai.document_extractor import extract_text

class AiVendorBillImport(models.Model):
    _name = "ai.vendor.bill.import"
    _description = "AI Vendor Bill Import"

    name = fields.Char(string="Document Name", required=True)
    pdf_file = fields.Binary(string="Vendor Bill PDF", attachment=True)
    pdf_filename = fields.Char(string="PDF Filename")
    extracted_text = fields.Text(string="Extracted Text")
    parsed_data = fields.Text(
    string="Parsed Data",
    readonly=True,
    )

    vendor_name = fields.Char(string="Vendor")
    invoice_number = fields.Char(string="Invoice Number")
    invoice_date = fields.Date(string="Invoice Date")
    total_amount = fields.Float(string="Total Amount")

    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("uploaded", "Uploaded"),
            ("processed", "Processed"),
            ("error", "Error"),
        ],
        default="draft",
        string="Status",
    )

    def action_mark_uploaded(self):
        for record in self:
            if record.pdf_file:
                record.state = "uploaded"
        return True
    
    def action_extract_text(self):
        for record in self:
            if not record.pdf_file:
                raise UserError("Please upload a document first.")

            suffix = Path(record.pdf_filename or "").suffix.lower()

            if suffix not in [".pdf", ".jpg", ".jpeg", ".png"]:
                raise UserError("Unsupported file type. Please upload PDF, JPG or PNG.")

            file_data = base64.b64decode(record.pdf_file)

            with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
                tmp.write(file_data)
                tmp_path = tmp.name

            extracted = extract_text(tmp_path)

            record.extracted_text = extracted

            parsed_data = parse_invoice_text(record.extracted_text)
            
            record.parsed_data = str(parsed_data)
            record.vendor_name = parsed_data.get("vendor_name")
            record.invoice_number = parsed_data.get("invoice_number")
            record.total_amount = parsed_data.get("total_amount")

            record.state = "processed"