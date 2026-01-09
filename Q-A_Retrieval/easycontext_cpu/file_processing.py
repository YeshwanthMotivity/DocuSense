import fitz  # PyMuPDF
import docx
import io

def process_file(file_storage, filename):
    """
    Extracts text from an uploaded file based on its extension.
    
    Args:
        file_storage: The Flask FileStorage object.
        filename: The name of the file.
        
    Returns:
        str: The extracted text content.
    """
    file_ext = filename.lower().split('.')[-1]
    
    if file_ext == 'pdf':
        return _read_pdf(file_storage)
    elif file_ext in ['docx', 'doc']:
        return _read_docx(file_storage)
    else:
        # Assume text-based for everything else
        return file_storage.read().decode("utf-8")

def _read_pdf(file_storage):
    """Extracts text from a PDF file."""
    text = ""
    # Read file stream into memory
    file_stream = file_storage.read()
    
    # Open PDF from memory
    with fitz.open(stream=file_stream, filetype="pdf") as doc:
        for page in doc:
            text += page.get_text() + "\n"
    
    return text

def _read_docx(file_storage):
    """Extracts text from a DOCX file."""
    # python-docx needs a file-like object, FileStorage works but let's be safe 
    # and not read it all into bytes if we don't have to, but for consistency we might.
    # Actually python-docx can take the stream directly.
    doc = docx.Document(file_storage)
    full_text = []
    for para in doc.paragraphs:
        full_text.append(para.text)
    return '\n'.join(full_text)
