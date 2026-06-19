from odoo import models, fields


class AiVendorBillImport(models.Model):
    _name = "ai.vendor.bill.import"
    _description = "AI Vendor Bill Import"

    name = fields.Char(string="Document Name", required=True)
    pdf_file = fields.Binary(string="Vendor Bill PDF", attachment=True)
    pdf_filename = fields.Char(string="PDF Filename")
    extracted_text = fields.Text(string="Extracted Text")

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
            record.extracted_text = "OCR not implemented yet. Text extraction will appear here."
            record.state = "processed"
        return True