from odoo import models, fields


class AiVendorBillImport(models.Model):
    _name = "ai.vendor.bill.import"
    _description = "AI Vendor Bill Import"

    name = fields.Char(string="Document name", required=True, default="New")
    vendor_name = fields.Char(string="Vendor")
    invoice_number = fields.Char(string="Invoice Number")
    invoice_date = fields.Date(string="Invoice Date")
    total_amount = fields.Float(string="Total Amount")
    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("processed", "Processed"),
            ("error", "Error"),
        ],
        default="draft",
        string="Status",
    )