import PyPDF2
import os
from app import db

def extract_pdf_info(file_path):
    """
    Extract information from a PDF file
    Returns the total number of pages
    """
    if not os.path.exists(file_path):
        return 0
        
    try:
        # Open the PDF file in binary mode
        with open(file_path, 'rb') as file:
            # Create a PDF reader object
            pdf_reader = PyPDF2.PdfReader(file)
            
            # Get the total number of pages
            total_pages = len(pdf_reader.pages)
            
            return total_pages
    except Exception as e:
        print(f"Error extracting PDF info: {e}")
        return 0

def extract_pdf_content(file_path, start_page, end_page):
    """
    Extract content from a range of pages in a PDF
    Returns the extracted text content
    """
    if not os.path.exists(file_path):
        return ""
        
    try:
        # Open the PDF file in binary mode
        with open(file_path, 'rb') as file:
            # Create a PDF reader object
            pdf_reader = PyPDF2.PdfReader(file)
            
            # Total pages in the PDF
            total_pages = len(pdf_reader.pages)
            
            # Adjust page range if necessary
            start_page = max(0, start_page - 1)  # Convert to 0-indexed
            end_page = min(total_pages - 1, end_page - 1)  # Convert to 0-indexed
            
            # Extract text from the specified page range
            content = ""
            for page_num in range(start_page, end_page + 1):
                page = pdf_reader.pages[page_num]
                content += page.extract_text() + "\n\n--- Page Break ---\n\n"
            
            return content
    except Exception as e:
        print(f"Error extracting PDF content: {e}")
        return "" 