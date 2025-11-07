import os
import logging
from flask import Flask, request, jsonify
from easycontext_cpu.chunk import chunk_text
from easycontext_cpu.retrieve_chunks import get_top_k_chunks
from easycontext_cpu.infer_model import generate_answer
from flask_cors import CORS

# --- Configuration ---
# Set up logging
logging.basicConfig(level=os.getenv('LOG_LEVEL', 'INFO').upper(),
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Flask debug mode
DEBUG_MODE = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
# Top K chunks for retrieval
TOP_K_CHUNKS = int(os.getenv('TOP_K_CHUNKS', '5'))
# Max question length (example for input validation)
MAX_QUESTION_LENGTH = int(os.getenv('MAX_QUESTION_LENGTH', '500'))
# Max file size in bytes (example for input validation)
MAX_FILE_SIZE = int(os.getenv('MAX_FILE_SIZE', '10485760')) # 10MB

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Set max content length for file uploads
app.config['MAX_CONTENT_LENGTH'] = MAX_FILE_SIZE

# --- Business Logic Module/Service ---
class TextProcessingService:
    @staticmethod
    def process_document_and_answer(file_content: str, question: str, k: int = TOP_K_CHUNKS):
        logger.info("Starting document processing and answer generation.")
        try:
            chunks = chunk_text(file_content)
            logger.debug(f"Chunked document into {len(chunks)} chunks.")
            if not chunks:
                raise ValueError("No content found or chunks could be generated from the document.")

            top_chunks = get_top_k_chunks(question, chunks, k=k)
            logger.debug(f"Retrieved {len(top_chunks)} top chunks.")
            if not top_chunks:
                raise ValueError("No relevant chunks found for the given question.")

            answer, prompt, debug_info, _ = generate_answer(question, top_chunks, return_debug=True)
            logger.info("Answer generated successfully.")
            return {
                "answer": answer,
                "prompt": prompt,
                "debug_info": debug_info
            }
        except Exception as e:
            logger.error(f"Error during text processing or answer generation: {e}", exc_info=True)
            raise RuntimeError(f"Failed to process document or generate answer: {e}")

# --- Flask Routes ---
@app.route("/", methods=["POST"])
def index():
    logger.info("Received request to /")

    # --- Input Validation ---
    uploaded_file = request.files.get("file")
    question = request.form.get("question")

    if not uploaded_file:
        logger.warning("Missing file in request.")
        return jsonify({"error": "Missing file. Please upload a document."}), 400

    if not question:
        logger.warning("Missing question in request.")
        return jsonify({"error": "Missing question. Please provide a question."}), 400

    if not isinstance(question, str) or not question.strip():
        logger.warning("Invalid question format or empty question.")
        return jsonify({"error": "Invalid question. Question must be a non-empty string."}), 400

    if len(question) > MAX_QUESTION_LENGTH:
        logger.warning(f"Question exceeds max length of {MAX_QUESTION_LENGTH} characters.")
        return jsonify({"error": f"Question is too long. Max length is {MAX_QUESTION_LENGTH} characters."}), 400

    try:
        # File type/content validation
        file_content_raw = uploaded_file.read()
        if not file_content_raw:
            logger.warning("Uploaded file is empty.")
            return jsonify({"error": "Uploaded file is empty."}), 400

        try:
            file_content = file_content_raw.decode("utf-8")
        except UnicodeDecodeError as e:
            logger.error(f"File decoding error: {e}", exc_info=True)
            return jsonify({"error": f"Could not decode file as UTF-8. Please ensure it's a valid text file. Error: {e}"}), 400
        except Exception as e:
            logger.error(f"An unexpected error occurred while reading the file: {e}", exc_info=True)
            return jsonify({"error": f"An unexpected error occurred while reading the file. Error: {e}"}), 500

        # --- Call Business Logic ---
        result = TextProcessingService.process_document_and_answer(file_content, question)
        return jsonify(result), 200

    except RuntimeError as e: # Catch exceptions raised by the service layer
        logger.error(f"Service processing error: {e}", exc_info=True)
        return jsonify({"error": str(e)}), 500
    except Exception as e: # Catch any other unexpected errors
        logger.critical(f"An unhandled error occurred: {e}", exc_info=True)
        return jsonify({"error": "An unexpected server error occurred."}), 500

if __name__ == "__main__":
    logger.info(f"Starting Flask app in debug mode: {DEBUG_MODE}")
    app.run(debug=DEBUG_MODE)