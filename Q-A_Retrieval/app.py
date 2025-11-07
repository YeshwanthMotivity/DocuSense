import os
import logging
from flask import Flask, request, jsonify
from easycontext_cpu.chunk import chunk_text
from easycontext_cpu.retrieve_chunks import get_top_k_chunks
from easycontext_cpu.infer_model import generate_answer
from flask_cors import CORS
from werkzeug.exceptions import RequestEntityTooLarge

# --- Configuration ---
# Externalize debug mode: FLASK_DEBUG=true or FLASK_DEBUG=1 enables debug
DEBUG = os.environ.get("FLASK_DEBUG", "False").lower() in ("true", "1")
# Externalize max file size: MAX_FILE_SIZE_MB=10 for 10MB
MAX_FILE_SIZE_MB = int(os.environ.get("MAX_FILE_SIZE_MB", 5)) # Default to 5MB
MAX_FILE_SIZE_BYTES = MAX_FILE_SIZE_MB * 1024 * 1024

# --- Flask App Setup ---
app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

app.config["DEBUG"] = DEBUG
app.config["MAX_CONTENT_LENGTH"] = MAX_FILE_SIZE_BYTES # Set file size limit

# --- Logging Setup ---
# Configure basic logging for console output
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
app.logger.setLevel(logging.INFO)
if DEBUG:
    app.logger.setLevel(logging.DEBUG)


# --- Modularized Business Logic ---
def _process_text_qa(file_content: str, question: str):
    """
    Core business logic for processing text, chunking, retrieval, and answer generation.
    Raises exceptions for specific errors during processing.
    """
    app.logger.debug("Starting text processing for QA.")
    try:
        chunks = chunk_text(file_content)
        app.logger.debug(f"Chunked text into {len(chunks)} chunks.")

        top_chunks = get_top_k_chunks(question, chunks, k=5)
        app.logger.debug(f"Retrieved {len(top_chunks)} top chunks.")
        
        # Consider Asynchronous Processing: The 'generate_answer' call can be long-running.
        # This function could be offloaded to a background task queue (e.g., Celery)
        # to improve API responsiveness for large files or complex models.
        answer, prompt, debug_info, _ = generate_answer(question, top_chunks, return_debug=True)
        app.logger.info("Answer generated successfully.")
        return answer, prompt, debug_info
    except Exception as e:
        app.logger.error(f"Error during core QA processing: {e}", exc_info=True)
        # Re-raise to be caught by the main route's error handling for consistent response
        raise


# --- Error Handlers (for specific Flask/Werkzeug errors) ---
@app.errorhandler(RequestEntityTooLarge)
def handle_file_too_large(error):
    """Handles cases where the uploaded file exceeds MAX_CONTENT_LENGTH."""
    app.logger.warning(f"File upload too large: {error}")
    return jsonify({
        "status": "error",
        "message": f"File too large. Maximum allowed size is {MAX_FILE_SIZE_MB}MB."
    }), 413 # HTTP 413 Request Entity Too Large


# --- Main API Route ---
@app.route("/", methods=["POST"])
def index():
    app.logger.info("Received request to /")

    uploaded_file = request.files.get("file")
    question = request.form.get("question")

    # Input Validation: Check for missing file or question
    if not uploaded_file:
        app.logger.warning("Missing 'file' in request.")
        return jsonify({
            "status": "error",
            "message": "No file uploaded. Please include a 'file' in the form data."
        }), 400 # HTTP 400 Bad Request
    if not question:
        app.logger.warning("Missing 'question' in request form data.")
        return jsonify({
            "status": "error",
            "message": "No question provided. Please include a 'question' in the form data."
        }), 400 # HTTP 400 Bad Request

    # Input Validation: Validate Content-Type header
    # Allow any text-based content type, e.g., text/plain, text/markdown, etc.
    if not uploaded_file.content_type or not uploaded_file.content_type.startswith("text/"):
        app.logger.warning(f"Unsupported content type: {uploaded_file.content_type}")
        return jsonify({
            "status": "error",
            "message": f"Unsupported file type. Expected a text-based file (e.g., text/plain), but received '{uploaded_file.content_type}'."
        }), 415 # HTTP 415 Unsupported Media Type

    try:
        # Read and decode file content
        file_content = uploaded_file.read().decode("utf-8")
        app.logger.info("File content read and decoded successfully.")

        # Call modularized business logic
        answer, prompt, debug_info = _process_text_qa(file_content, question)

        # Successful response
        return jsonify({
            "status": "success",
            "answer": answer,
            "prompt": prompt,
            "debug_info": debug_info # Model-specific debug info can still be useful
        }), 200 # HTTP 200 OK

    except UnicodeDecodeError as e:
        app.logger.error(f"UnicodeDecodeError when reading file: {e}", exc_info=True)
        return jsonify({
            "status": "error",
            "message": "Failed to decode file content. Please ensure it is UTF-8 encoded plain text."
        }), 400 # HTTP 400 Bad Request
    except Exception as e:
        # Catch any other unexpected errors from _process_text_qa or other parts of the request
        app.logger.error(f"An unexpected server error occurred: {e}", exc_info=True)
        return jsonify({
            "status": "error",
            "message": "An internal server error occurred while processing your request. Please try again later."
        }), 500 # HTTP 500 Internal Server Error


# --- Run App ---
if __name__ == "__main__":
    # When running with `flask run`, FLASK_DEBUG environment variable is typically picked up.
    # For direct execution `python app.py`, we explicitly set the debug parameter.
    app.run(host="0.0.0.0", port=5000, debug=app.config["DEBUG"])