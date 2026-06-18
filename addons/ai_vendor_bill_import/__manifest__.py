{
    "name": "AI Vendor Bill Import",
    "version": "1.0",
    "summary": "Import vendor bills using OCR and AI-assisted data extraction",
    "author": "Jordi Prim",
    "category": "Accounting",
    "depends": ["base", "account"],
    "data": [
        "security/ir.model.access.csv",
        "views/vendor_bill_import_views.xml",
    ],
    "installable": True,
    "application": True,
}
