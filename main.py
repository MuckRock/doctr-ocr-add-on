"""
This is an Add-On that uses docTR https://github.com/mindee/doctr to OCR documents for DocumentCloud
"""

from documentcloud.addon import AddOn


class docTR(AddOn):
    """Class definition"""

    def main(self):
        """The main add-on functionality goes here."""
        model = ocr_predictor(pretrained=True)
        for document in self.get_documents():
            pdf_name = f"'{document.title}.pdf'"
            with archive.open(f"{document.slug} - {document.id}.pdf", "w") as pdf:
                pdf.write(document.pdf)
                doc = DocumentFile.from_pdf(pdf_name)
                result = model(doc)
                json_export = result.export()
                print(json_export)

if __name__ == "__main__":
    docTR().main()
