"""
PDF Service - Handles PDF text extraction
"""
import PyPDF2


def extract_text_from_pdf(pdf_path):
    """Extract text content from a PDF file - all pages"""
    pages = []
    try:
        with open(pdf_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            for page_num in range(len(pdf_reader.pages)):
                page = pdf_reader.pages[page_num]
                text = page.extract_text() or ""
                pages.append({
                    'page_number': page_num + 1,
                    'content': text
                })
    except Exception as e:
        print(f"Error extracting text: {e}")
        return None
    return pages


def get_full_text(pages):
    """Combine all pages into full text"""
    if not pages:
        return ""
    return '\n\n'.join([f"--- Page {p['page_number']} ---\n{p['content']}" for p in pages])
