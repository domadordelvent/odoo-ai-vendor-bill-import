import base64
import json
import tempfile
from pathlib import Path
from .ai_parser import parse_invoice_text
from datetime import datetime

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
    vendor_vat = fields.Char(string="Vendor VAT")
    invoice_number = fields.Char(string="Invoice Number")
    invoice_date = fields.Date(string="Invoice Date")
    total_amount = fields.Float(string="Total Amount")
    base_amount = fields.Float(string="Base Amount", readonly=True)
    tax_amount = fields.Float(string="Tax Amount", readonly=True)
    vendor_bill_id = fields.Many2one("account.move", string="Vendor Bill", readonly=True)

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
            
            record.parsed_data = json.dumps(parsed_data)
            
            
            record.vendor_name = parsed_data.get("vendor_name")
            record.vendor_vat = parsed_data.get("vendor_vat")
            record.invoice_number = parsed_data.get("invoice_number")
            record.total_amount = parsed_data.get("total_amount") or 0.0
            record.base_amount = parsed_data.get("base_amount") or 0.0
            record.tax_amount = parsed_data.get("tax_amount") or 0.0

            invoice_date = parsed_data.get("invoice_date")
            if invoice_date:
                record.invoice_date = record._parse_invoice_date(
                    parsed_data.get("invoice_date")
                )

            record.state = "processed"


    def _parse_invoice_date(self, invoice_date):
        if not invoice_date:
            return False

        value = invoice_date.replace("Z", "").split("T")[0]

        for date_format in ("%Y-%m-%d", "%d/%m/%Y", "%d-%m-%Y"):
            try:
                return datetime.strptime(value, date_format).date()
            except ValueError:
                continue

        raise UserError(f"Unsupported invoice date format: {invoice_date}")




    def action_create_vendor_bill(self):
        for record in self:
            if record.vendor_bill_id:
                return {
                    "type": "ir.actions.act_window",
                    "res_model": "account.move",
                    "res_id": record.vendor_bill_id.id,
                    "view_mode": "form",
                    "target": "current",
                }

            if not record.vendor_name:
                raise UserError("Vendor name is missing. Extract text first.")

            partner = False

            if record.vendor_vat:
                partner = self.env["res.partner"].search(
                    [("vat", "=", record.vendor_vat)],
                    limit=1,
                )

            if not partner:
                partner = self.env["res.partner"].search(
                    [("name", "=", record.vendor_name)],
                    limit=1,
                )

            if not partner:
                partner = self.env["res.partner"].create({
                    "name": record.vendor_name,
                    "vat": record.vendor_vat or False,
                    "supplier_rank": 1,
                })
            elif record.vendor_vat and not partner.vat:
                partner.vat = record.vendor_vat

            parsed_data = json.loads(record.parsed_data)
            invoice_lines = record._prepare_invoice_lines(parsed_data)

            if not record.total_amount and not record.base_amount:
                raise UserError("Total amount is missing. Extract text first.")

            bill = self.env["account.move"].create({
                "move_type": "in_invoice",
                "partner_id": partner.id,
                "invoice_date": record.invoice_date,
                "ref": record.invoice_number,
                "invoice_line_ids": invoice_lines,
            })

            record.vendor_bill_id = bill.id

        return {
            "type": "ir.actions.act_window",
            "res_model": "account.move",
            "res_id": bill.id,
            "view_mode": "form",
            "target": "current",
        }
    

    def _prepare_invoice_lines(self, parsed_data):
        invoice_lines = []

        

        for line in parsed_data.get("lines", []):
            product = self._get_product(line.get("description"))
            invoice_lines.append(
                (0, 0, {
                    "product_id": product.id if product else False,
                    "name": line.get("description") or "Imported line",
                    "quantity": line.get("quantity") or 1,
                    "price_unit": line.get("unit_price") or 0.0,
                    "tax_ids": self._get_purchase_tax(line.get("tax_rate")),
                    
                })
            )

        if not invoice_lines:
            invoice_lines.append(
                (0, 0, {
                    "name": self.name or "Imported vendor bill",
                    "quantity": 1,
                    "price_unit": self.base_amount or self.total_amount,
                    
                })
            )

        return invoice_lines
    
    def _get_purchase_tax(self, tax_rate):
        if tax_rate is None:
            return []

        tax = self.env["account.tax"].search(
            [
                ("type_tax_use", "=", "purchase"),
                ("amount_type", "=", "percent"),
                ("amount", "=", tax_rate),
                ("active", "=", True),
                ("company_id", "=", self.env.company.id),
                ("name", "=", f"{int(tax_rate)}% G"),
            ],
            limit=1,
        )

        if tax:
            return [(6, 0, tax.ids)]

        return []
    
    def _get_product(self, description):
        if not description:
            return False

        product = self.env["product.product"].search(
            [("name", "=", description)],
            limit=1,
        )

        if not product:
            product = self.env["product.product"].create({
                "name": description,
                "purchase_ok": True,
                "sale_ok": False,
            })

        return product