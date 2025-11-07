import os
import logging
from flask import Flask, request, jsonify
from easycontext_cpu.chunk import chunk_text
from easycontext_cpu.retrieve_chunks import get_top_k_chunks
from easycontext_cpu.infer_model import generate_answer
from flask_cors import CORS
from werkzeug.exceptions import RequestEntityTooLarge

# --- Configuration Management ---
# Use environment variables for sensitive or deployment-specific settings
DEBUG = os.environ.get("FLASK_DEBUG", "False").lower() in ("true", "1", "t")
MAX_UPLOAD_SIZE_MB = int(os.environ.get("MAX_UPLOAD_SIZE_MB", 5)) # Default 5 MB
MAX_CONTENT_LENGTH = MAX_UPLOAD_SIZE_MB * 1024 * 1024 # Convert MB to bytes

ALLOWED_MIMETYPES = os.environ.get("ALLOWED_MIMETYPES", "text/plain,application/csv").split(',')
# For more restrictive CORS, specify origins, methods, and headers
CORS_ORIGINS = os.environ.get("CORS_ORIGINS", "*").split(',') # Example: "http://localhost:3000,https://yourdomain.com"
CORS_METHODS = os.environ.get("CORS_METHODS", "POST") # Only POST for this route
CORS_HEADERS = os.environ.get("CORS_HEADERS", "Content-Type,Authorization") # Common headers

# --- Logging Setup ---
logging.basicConfig(level=logging.INFO if not DEBUG else logging.DEBUG,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = MAX_CONTENT_LENGTH # Set max file size for uploads

# Configure CORS more restrictively
CORS(app,
     origins=CORS_ORIGINS,
     methods=CORS_METHODS.split(','),
     headers=CORS_HEADERS.split(','),
     supports_credentials=True # If your frontend requires credentials (e.g., cookies, auth headers)
)

# --- Error Handlers ---
@app.errorhandler(RequestEntityTooLarge)
def handle_request_entity_too_large(e):
    logger.warning(f"File upload too large: {e}")
    return jsonify({"error": f"File too large. Maximum size is {MAX_UPLOAD_SIZE_MB}MB."}), 413

@app.errorhandler(400)
def handle_bad_request(e):
    logger.warning(f"Bad request: {e}")
    return jsonify({"error": "Bad request. Please check your input."}), 400

@app.errorhandler(Exception)
def handle_general_exception(e):
    logger.exception(f"An unhandled internal server error occurred: {e}")
    return jsonify({"error": "An internal server error occurred. Please try again later."}), 500


@app.route("/", methods=["POST"])
def index():
    logger.info("Received request to /")
    answer = None
    prompt = None
    debug_info = None

    uploaded_file = request.files.get("file")
    question = request.form.get("question")

    if not uploaded_file:
        logger.warning("Missing 'file' in request.")
        return jsonify({"error": "No file uploaded."}), 400
    if not question:
        logger.warning("Missing 'question' in request form data.")
        return jsonify({"error": "No question provided."}), 400

    # --- File Type Validation ---
    if uploaded_file.mimetype not in ALLOWED_MIMETYPES:
        logger.warning(f"Invalid file type uploaded: {uploaded_file.mimetype}. Allowed: {ALLOWED_MIMETYPES}")
        return jsonify({"error": f"Unsupported file type. Allowed types are: {', '.join(ALLOWED_MIMETYPES)}"}), 415 # Unsupported Media Type

    try:
        # --- Specific Error Handling for File Decoding ---
        try:
            file_content = uploaded_file.read().decode("utf-8")
        except UnicodeDecodeError:
            logger.error("Failed to decode file content as UTF-8.")
            return jsonify({"error": "Could not decode file content. Please ensure it's a valid UTF-8 text file."}), 422 # Unprocessable Entity
        except Exception as e:
            logger.exception("Unexpected error during file reading/decoding.")
            return jsonify({"error": f"Error reading file: {str(e)}"}), 500

        # --- Processing steps (consider offloading to a background task queue) ---
        # The following steps are synchronous. If generate_answer is time-consuming,
        # consider offloading this block to a background task queue (e.g., Celery)
        # to improve API responsiveness and scalability. For this example, it remains synchronous.
        logger.debug("Chunking text...")
        chunks = chunk_text(file_content)
        logger.debug(f"Generated {len(chunks)} chunks.")

        logger.debug("Retrieving top K chunks...")
        top_chunks = get_top_k_chunks(question, chunks, k=5)
        logger.debug(f"Retrieved {len(top_chunks)} top chunks.")

        logger.debug("Generating answer...")
        answer, prompt, debug_info, _ = generate_answer(question, top_chunks, return_debug=True)
        logger.info("Answer generated successfully.")

    except Exception as e:
        # --- General Error Handling for processing steps ---
        logger.exception(f"Error during context processing or answer generation: {str(e)}")
        return jsonify({"error": f"An error occurred during processing: {str(e)}"}), 500

    return jsonify({
        "answer": answer,
        "prompt": prompt,
        "debug_info": debug_info
    })

if __name__ == "__main__":
    logger.info(f"Starting Flask app in DEBUG mode: {DEBUG}")
    # Run the app, listening on all public IPs (0.0.0.0) on port 5000
    # In production, use a WSGI server like Gunicorn or uWSGI
    app.run(debug=DEBUG, host="0.0.0.0", port=5000)