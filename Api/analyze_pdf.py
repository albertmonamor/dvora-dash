import sys

PDF_OPTIONS = {
    'page-size': 'A4',
}


if sys.platform == "win32":
    pass
elif sys.platform == "linux":
    import pdfkit

import pdfkit
def create_invoice_event(client:dict, path_out):
    pass



# Specify the output file path
output_path = "example.pdf"
# Convert HTML to PDF
pdfkit.from_string(TEMPLATE,
                   output_path,
                   configuration=pdfkit.configuration(wkhtmltopdf=r"C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe"),
                   options=PDF_OPTIONS)



