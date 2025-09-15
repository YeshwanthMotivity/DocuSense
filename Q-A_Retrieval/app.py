from flask import Flask, request, jsonify
from easycontext_cpu.chunk import chunk_text
from easycontext_cpu.retrieve_chunks import get_top_k_chunks
from easycontext_cpu.infer_model import generate_answer
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

@app.route("/", methods=["POST"])
def index():
    answer = None
    prompt = None
    debug_info = None

    uploaded_file = request.files.get("file")
    question = request.form.get("question")

    if uploaded_file and question:
        try:
            file_content = uploaded_file.read().decode("utf-8")
            chunks = chunk_text(file_content)
            top_chunks = get_top_k_chunks(question, chunks, k=5)
            answer, prompt, debug_info, _ = generate_answer(question, top_chunks, return_debug=True)
        except Exception as e:
            answer = f"Error: {str(e)}"
    else:
        return jsonify({"error": "Missing file or question"}), 400

    return jsonify({
        "answer": answer,
        "prompt": prompt,
        "debug_info": debug_info
    })

if __name__ == "__main__":
    app.run(debug=True)
