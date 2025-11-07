import os
import logging
import uuid
import threading

from flask import Flask, request, jsonify
from easycontext_cpu.chunk import chunk_text
from easycontext_cpu.retrieve_chunks import get_top_k_chunks
from easycontext_cpu.infer_model import generate_answer
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app.config['DEBUG'] = os.environ.get('FLASK_DEBUG') == '1'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
app.config['K_CHUNKS'] = int(os.environ.get('K_CHUNKS', 5))

task_results = {}

def process_question_task(job_id, file_content_bytes, question, k_chunks):
    task_results[job_id] = {'status': 'processing'}
    answer = None
    prompt = None
    debug_info = None
    error_message = None

    try:
        try:
            file_content = file_content_bytes.decode("utf-8")
        except UnicodeDecodeError as e:
            error_message = f"Error decoding file content: {e}. Please ensure it's a valid UTF-8 text file."
            logger.error(f"Job {job_id}: {error_message}", exc_info=True)
            task_results[job_id] = {
                'status': 'failed',
                'result': {'error': error_message},
                'status_code': 400
            }
            return

        chunks = chunk_text(file_content)
        top_chunks = get_top_k_chunks(question, chunks, k=k_chunks)
        answer, prompt, debug_info, _ = generate_answer(question, top_chunks, return_debug=True)

        task_results[job_id] = {
            'status': 'completed',
            'result': {
                "answer": answer,
                "prompt": prompt,
                "debug_info": debug_info
            },
            'status_code': 200
        }

    except Exception as e:
        error_message = f"An unexpected error occurred during processing: {str(e)}"
        logger.error(f"Job {job_id}: {error_message}", exc_info=True)
        task_results[job_id] = {
            'status': 'failed',
            'result': {'error': error_message},
            'status_code': 500
        }

@app.route("/submit_question", methods=["POST"])
def submit_question():
    uploaded_file = request.files.get("file")
    question = request.form.get("question")

    if not uploaded_file or not question:
        logger.warning("Missing file or question in submission.")
        return jsonify({"error": "Missing file or question"}), 400

    job_id = str(uuid.uuid4())
    logger.info(f"Received job submission: {job_id}")

    try:
        file_content_bytes = uploaded_file.read()
        task_results[job_id] = {'status': 'pending'}
        thread = threading.Thread(
            target=process_question_task,
            args=(job_id, file_content_bytes, question, app.config['K_CHUNKS'])
        )
        thread.start()
        logger.info(f"Job {job_id} submitted for background processing.")

        return jsonify({
            "job_id": job_id,
            "message": "Processing started. You can poll /results/<job_id> for status."
        }), 202

    except Exception as e:
        logger.exception("Failed to submit job due to an unexpected error.")
        return jsonify({"error": f"Failed to submit job: {str(e)}"}), 500

@app.route("/results/<job_id>", methods=["GET"])
def get_results(job_id):
    result = task_results.get(job_id)

    if result is None:
        logger.warning(f"Attempted to retrieve results for unknown job ID: {job_id}")
        return jsonify({"error": "Job ID not found."}), 404

    status = result.get('status')
    if status == 'completed':
        logger.info(f"Job {job_id}: Results retrieved successfully.")
        return jsonify(result['result']), result.get('status_code', 200)
    elif status == 'failed':
        logger.error(f"Job {job_id}: Failed results retrieved.")
        return jsonify(result['result']), result.get('status_code', 500)
    else:
        logger.info(f"Job {job_id}: Status is '{status}'. Still processing.")
        return jsonify({"status": status, "message": "Processing in progress..."}), 200

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)