import warnings
warnings.filterwarnings("ignore")

from flask import Flask, request, jsonify
from easycontext_cpu.chunk import chunk_text
from easycontext_cpu.retrieve_chunks import get_top_k_chunks
from easycontext_cpu.infer_model import generate_answer
from flask_cors import CORS
from easycontext_cpu.file_processing import process_file

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

@app.route("/", methods=["POST"])
def index():
    answer = None
    prompt = None
    debug_info = None

    uploaded_file = request.files.get("file")
    question = request.form.get("question")
    history_str = request.form.get("history", "[]")

    if uploaded_file and question:
        try:
            # Parse history
            import json
            history = json.loads(history_str)
            
            # Construct context-aware query
            # We prepend the last few turns to the query to give the model context
            context_context = ""
            if history:
                # Take last 3 exchanges
                recent = history[-3:] 
                for msg in recent:
                    role = "User" if msg['role'] == 'user' else "Assistant"
                    context_context += f"{role}: {msg['content']}\n"
            
            full_query = f"{context_context}\nCurrent Question: {question}"

            # process_file handles extracted text from PDF, DOCX, or TXT
            file_content = process_file(uploaded_file, uploaded_file.filename)
            chunks = chunk_text(file_content)
            
            # We use the raw question for retrieval to avoid noise, 
            # BUT for generation we pass the full context-aware query.
            # Actually, using full_query for retrieval might be better if "it" is used.
            # Let's use full_query for both to be safe.
            top_chunks = get_top_k_chunks(full_query, chunks, k=5)
            answer, prompt, debug_info, _ = generate_answer(full_query, top_chunks, return_debug=True)
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
