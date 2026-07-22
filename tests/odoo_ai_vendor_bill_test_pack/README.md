# Odoo AI Vendor Bill Import - Test Pack

Synthetic documents created exclusively for testing. Every document is marked as a test and contains fictitious data.

## Contents
- 15 documents: text PDFs, image-only scanned PDF, PNG and JPG.
- `expected_json/`: expected structured output for every document.
- `manifest.json`: test matrix with the purpose of each case.

## Suggested workflow
1. Upload each document to the Odoo module.
2. Run `Mark as Uploaded` and `Extract Text`.
3. Compare `Parsed Data` with the matching JSON file.
4. Create the vendor bill and verify supplier, reference, date, lines, taxes and totals.
5. Record pass/fail and any difference.

## Important edge cases
- `08_pdf_same_vat_different_name.pdf` shares VAT `B12345678` with case 01 but uses a different vendor name.
- `13_pdf_scanned_image_only.pdf` has no text layer and forces OCR.
- `14_pdf_two_pages.pdf` tests multi-page and many-line extraction.
- `15_pdf_missing_invoice_number.pdf` intentionally omits the invoice number.
