"""
This is an Add-On that uses docTR https://github.com/mindee/doctr to OCR documents for DocumentCloud
"""
import time
from documentcloud.addon import AddOn
from doctr.io import DocumentFile
from doctr.models import ocr_predictor

class docTR(AddOn):
    """Class definition"""

    def main(self):
        """The main add-on functionality goes here."""
        to_tag=self.data.get("to_tag", False)
        if self.get_document_count() is None:
            self.set_message("Please select at least one document.")
            return
        model = ocr_predictor('db_resnet50', 'crnn_vgg16_bn', pretrained=True, assume_straight_pages=False, export_as_straight_boxes=True)
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
                        "ocr": "doctr",
                        "positions": [],
                    }
                    for block in page['blocks']:
                        for line in block['lines']:
                            line_text = ""
                            for word in line['words']:
                                line_text += word['value'] + ' '
                                word_value = word['value']
                                word_bounding_box = word['geometry']
                                x1 = word_bounding_box[0][0]
                                y1 = word_bounding_box[0][1]
                                x2 = word_bounding_box[1][0]
                                y2 = word_bounding_box[1][1]
                                if word['value']:
                                    position_info = {
                                        "text": word_value,
                                        "x1": float(x1),
                                        "x2": float(x2),
                                        "y1": float(y1),
                                        "y2": float(y2),
                                    }
                                    dc_page["positions"].append(position_info)
                            text += line_text.strip() + '\n'
                        text += '\n'
                    dc_page['text'] = text
                    pages.append(dc_page)
                page_chunk_size = 100  # Set your desired chunk size
                for i in range(0, len(pages), page_chunk_size):
                    chunk = pages[i:i + page_chunk_size]
                    resp = self.client.patch(f"documents/{document.id}/", json={"pages": chunk})
                    resp.raise_for_status()
                    while True:
                        document_ref = self.client.documents.get(document.id)
                        time.sleep(15)
                        if document_ref.status == "success": # Break out of for loop if document status becomes success
                            break
            if to_tag:
                document.data["ocr_engine"]="doctr"
                document.save()
if __name__ == "__main__":
    docTR().main()
