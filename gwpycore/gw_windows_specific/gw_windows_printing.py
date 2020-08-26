from pypdf import PdfFileWriter
import win32api, win32print

def print_pdf(pdfName: str, printer="default"):
    if printer == "default":
        printer = win32print.GetDefaultPrinter()
    win32api.ShellExecute(0, "print", pdfName, '/d:"%s"' % printer, ".", 0)


def fill_in_pdf(template_pdf, field_values, filename):
    output = PdfFileWriter(filename)
    output.have_viewer_render_fields()
    for page_no in range(template_pdf.numPages):
        template_page = template_pdf.getPage(page_no)
        output.addPage(template_page)
        page = output.getPage(page_no)
        output.updatePageFormFieldValues(page, field_values, read_only=True)
    output.write()
    print("Created '%s'" % (filename))


__all__ = ("print_pdf", "fill_in_pdf")
