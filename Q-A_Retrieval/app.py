import os
import logging
from flask import Flask, request, jsonify
from easycontext_cpu.chunk import chunk_text
from easycontext_cpu.retrieve_chunks import get_top_k_chunks
from easycontext_cpu.infer_model import generate_answer
from flask_cors import CORS

# --- Logging Implementation ---
# Configure basic logging for the application
# This will capture INFO level and above messages, formatted with timestamp, logger name, level, and message.
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# --- Configuration Management ---
# Get K_CHUNKS from environment variable or default to 5
try:
    K_CHUNKS = int(os.getenv("TOP_K_CHUNKS", "5"))
    app.logger.info(f"Configured TOP_K_CHUNKS: {K_CHUNKS}")
except ValueError:
    app.logger.error("Invalid value provided for TOP_K_CHUNKS environment variable. Defaulting to 5.")
    K_CHUNKS = 5

@app.route("/", methods=["POST"])
def index():
    app.logger.info("Received POST request to /")
    
    uploaded_file = request.files.get("file")
    question = request.form.get("question")

    if not uploaded_file or not question:
        # --- Error Response Consistency & Logging ---
        app.logger.warning("Client error: Missing 'file' or 'question' in the request.")
        return jsonify({"error": "Missing 'file' or 'question' in the request."}), 400

    file_name = uploaded_file.filename if uploaded_file.filename else "unknown_file"
    log_question_snippet = f"{question[:100]}{'...' if len(question) > 100 else ''}"
    app.logger.info(f"Processing request for question: '{log_question_snippet}' from file: '{file_name}'")

    try:
        file_content = uploaded_file.read().decode("utf-8")
        app.logger.debug(f"File '{file_name}' read successfully. Content length: {len(file_content)} characters.")

        chunks = chunk_text(file_content)
        app.logger.debug(f"Text chunked into {len(chunks)} chunks.")

        top_chunks = get_top_k_chunks(question, chunks, k=K_CHUNKS)
        app.logger.debug(f"Retrieved {len(top_chunks)} top chunks using k={K_CHUNKS}.")

        answer, prompt, debug_info, _ = generate_answer(question, top_chunks, return_debug=True)
        app.logger.info("Answer generated successfully.")
        log_answer_snippet = f"{answer[:200]}{'...' if len(answer) > 200 else ''}"
        app.logger.debug(f"Generated Answer: {log_answer_snippet}")

        return jsonify({
            "answer": answer,
            "prompt": prompt,
            "debug_info": debug_info
        })

    except Exception as e:
        # --- Error Response Consistency & Logging ---
        # Log the full traceback for internal server errors
        app.logger.exception(f"An internal server error occurred while processing the request for question: '{log_question_snippet}' from file: '{file_name}'.")
        return jsonify({"error": "An internal server error occurred. Please try again later."}), 500

if __name__ == "__main__":
    app.run(debug=True)