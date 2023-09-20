"""
This is an Add-On that uses docTR https://github.com/mindee/doctr to OCR documents for DocumentCloud
"""

from documentcloud.addon import AddOn
from doctr.io import DocumentFile
from doctr.models import ocr_predictor

class docTR(AddOn):
    """Class definition"""

    def main(self):
        """The main add-on functionality goes here."""
        model = ocr_predictor('db_resnet50_rotation', 'crnn_vgg16_bn', pretrained=True, assume_straight_pages=False, export_as_straight_boxes=True)
        for document in self.get_documents():
            pdf_name = f"'{document.id}.pdf'"
            with open(pdf_name, "wb") as pdf:
                pdf.write(document.pdf)
                doc = DocumentFile.from_pdf(pdf_name)
                result = model(doc)
                json_export = result.export()
                for page in json_export['pages']:
                    page_idx = page['page_idx']
                    print(f"Page {page_idx}:")
                    for block in page['blocks']:
                        for line in block['lines']:
                            for word in line['words']:
                                word_value = word['value']
                                word_bounding_box = word['geometry']
                                print(f"Word: {word_value}")
                                print(f"Bounding Box: {word_bounding_box}")
                

if __name__ == "__main__":
    docTR().main()
