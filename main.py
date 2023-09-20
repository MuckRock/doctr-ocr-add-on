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
                pages = []
                for page in json_export['pages']:
                    page_idx = page['page_idx']
                    text = ''
                    dc_page = {
                        "page_number": page_idx,
                        "text": text,
                        "ocr": "docTR",
                        "positions": [],
                    }
                    print(f"Page {page_idx}:")
                    for block in page['blocks']:
                        for line in block['lines']:
                            line_text = ""
                            for word in line['words']:
                                line_text += word['value'] + ' '
                                word_value = word['value']
                                word_bounding_box = word['geometry']
                                print(f"Word: {word_value}")
                                print(f"Bounding Box: {word_bounding_box}")
        
                                x1 = word_bounding_box[0][0]
                                y1 = word_bounding_box[0][1]
                                x2 = word_bounding_box[1][0]
                                y2 = word_bounding_box[1][1]
                                position_info = {
                                    "text": word_value,
                                    "x1": x1,
                                    "x2": x2,
                                    "y1": y1,
                                    "y2": y2,
                                }
                                dc_page["positions"].append(position_info)
                            text += line_text.strip() + '\n'
                        text += '\n'
                    dc_page['text'] = text
                    pages.append(dc_page)
                resp = self.client.patch(f"documents/{document.id}/", json={"pages": pages})
                resp.raise_for_status()

if __name__ == "__main__":
    docTR().main()
