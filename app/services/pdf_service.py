import fitz  # PyMuPDF
import re
from fastapi import HTTPException, status

class PDFService:
    @staticmethod
    def extract_text_from_pdf_bytes(pdf_bytes: bytes, filename: str) -> str:
        """
        Extracts clean raw text from a PDF file byte stream using PyMuPDF.
        Raises HTTPException if PDF is invalid, encrypted without password, or empty.
        """
        if not pdf_bytes:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"The file '{filename}' is empty (0 bytes)."
            )
            
        try:
            doc = fitz.open(stream=pdf_bytes, filetype="pdf")
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Failed to parse '{filename}' as a PDF document. File may be corrupted. Error: {str(e)}"
            )

        if doc.is_encrypted:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"The file '{filename}' is encrypted/password-protected and cannot be read."
            )

        extracted_text_pages = []
        for page_num in range(len(doc)):
            page = doc.load_page(page_num)
            text = page.get_text("text")
            if text:
                extracted_text_pages.append(text)

        doc.close()

        full_text = "\n".join(extracted_text_pages).strip()

        if not full_text:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"No readable text found in '{filename}'. It may be a scanned image or empty PDF."
            )

        # Normalize line endings and multiple spaces
        cleaned_text = re.sub(r'\r\n|\r', '\n', full_text)
        cleaned_text = re.sub(r'\n{3,}', '\n\n', cleaned_text)
        
        return cleaned_text
