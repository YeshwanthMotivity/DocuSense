import os
import logging
from flask import Flask, request, jsonify
from easycontext_cpu.chunk import chunk_text
from easycontext_cpu.retrieve_chunks import get_top_k_chunks
from easycontext_cpu.infer_model import generate_answer
from flask_cors import CORS
from typing import Tuple, Dict, Any, Optional

# --- Configuration ---
# Move configuration parameters into environment variables for easier management
K_CHUNKS = int(os.getenv("K_CHUNKS", "5"))
SHOW_DEBUG_INFO = os.getenv("SHOW_DEBUG_INFO", "0").lower() == "1"

# --- Logging Setup ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

@app.route("/", methods=["POST"])
def index() -> Tuple[Dict[str, Any], int]:
    """
    Processes an uploaded text file and a question to generate an answer
    using easycontext_cpu functions.

    Expects a POST request with:
    - 'file': An uploaded text file.
    - 'question': The question string.

    Returns:
        A JSON response containing the generated 'answer', 'prompt', and optionally
        'debug_info'. Returns an error message and a 400 status if inputs are missing
        or an internal server error (500) if processing fails.
    """
    answer: Optional[str] = None
    prompt: Optional[str] = None
    debug_info_data: Optional[Dict[str, Any]] = None
    status_code: int = 200

    uploaded_file = request.files.get("file")
    question = request.form.get("question")

    if not uploaded_file or not question:
        logger.warning("Missing 'file' or 'question' in request.")
        return jsonify({"error": "Missing file or question"}), 400

    try:
        file_content: str
        try:
            # Read file content. For very large files, consider reading in chunks
            # if easycontext_cpu.chunk_text supported streaming input.
            # Currently, chunk_text expects a complete string.
            file_content = uploaded_file.read().decode("utf-8")
        except UnicodeDecodeError as e:
            logger.error(f"Failed to decode file content with UTF-8: {e}", exc_info=True)
            return jsonify({"error": f"Failed to decode file content: {e}. Ensure it's valid UTF-8."}), 400
        except Exception as e:
            logger.error(f"An unexpected error occurred while reading or decoding the uploaded file: {e}", exc_info=True)
            return jsonify({"error": f"Error reading or decoding file: {str(e)}"}), 500

        logger.info(f"Processing request for question: '{question}' with file: '{uploaded_file.filename}'")

        chunks = chunk_text(file_content)
        top_chunks = get_top_k_chunks(question, chunks, k=K_CHUNKS)
        answer, prompt, debug_info_raw, _ = generate_answer(question, top_chunks, return_debug=True)
        
        # Conditionally include debug_info in the response
        if SHOW_DEBUG_INFO:
            debug_info_data = debug_info_raw

        logger.info(f"Successfully generated answer for question: '{question}'")

    except Exception as e:
        logger.error(f"An error occurred during context processing or answer generation: {e}", exc_info=True)
        answer = "An internal server error occurred while processing your request." # Provide a generic error to the user
        status_code = 500

    response_data = {
        "answer": answer,
        "prompt": prompt,
    }
    if SHOW_DEBUG_INFO:
        response_data["debug_info"] = debug_info_data

    return jsonify(response_data), status_code

if __name__ == "__main__":
    # For production deployment, ensure debug=False and use a production-ready WSGI server
    # (e.g., Gunicorn, uWSGI) instead of Flask's built-in development server.
    # Example for Gunicorn: gunicorn -w 4 -b 0.0.0.0:5000 app:app
    debug_mode = os.getenv('FLASK_DEBUG', '0') == '1'
    logger.info(f"Starting Flask app in debug mode: {debug_mode}")
    app.run(debug=debug_mode)