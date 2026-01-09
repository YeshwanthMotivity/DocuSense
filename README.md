# DocuSense AI

**DocuSense** is an intelligent, document-based Q&A system that allows you to chat with your files (PDF, DOCX, TXT) using advanced local LLMs. It features a modern chat interface, voice interaction, and conversation memory.

## Features

-   **📄 Multi-Format Support**: Upload and analyze **PDF**, **DOCX**, and **TXT** files.
-   **🗣️ Voice Interaction**:
    -   **Voice Input**: Speak your questions using the microphone button.
    -   **Voice Output**: Listen to the AI's answers with the speaker button.
-   **🧠 Conversation Memory**: Ask follow-up questions (e.g., "Summarize *it*") with context awareness.
-   **🎨 Modern UI**: Beautiful, responsive "Glassmorphism" interface with Dark/Light accents.
-   **🔒 Local Privacy**: Powered by **Ollama**, ensuring your documents stay on your machine.
-   **Semantic Search**: Utilizes SentenceTransformers and FAISS for fast and accurate semantic search.

---
### Tech Stack

|     Layer      |                      Tools Used                      |
| -------------- | ---------------------------------------------------- |
| **Frontend**   | `React.js`, `HTML`, `CSS`                            |
| **Backend**    | `Flask`, `PyMuPDF` (fitz), `Transformers`            |
| **NLP Models** | `SentenceTransformers` (MiniLM), `Hugging Face LLMs` |
| **Search**     | `FAISS`                                              |
| **Deployment** | `Flask API` (local, extendable to Render/Heroku)     |

---
### Architecture Diagram
<img width="877" height="663" alt="arc" src="https://github.com/user-attachments/assets/b868e97d-8662-413e-90b7-4caeae6a9e27" />

---

### Project Workflow

1. **Document Upload**: A user uploads a PDF file via the React UI.
2. **Text Extraction**: The Flask backend parses and chunks the PDF's content using PyMuPDF.
3. **Embedding**: Each text chunk is converted into a vector using a SentenceTransformer.
4. **Semantic Search**: When the user asks a question, the system performs a semantic search using FAISS to retrieve the most relevant text chunks.
5. **Answer Generation**: The retrieved context and the user's question are provided to an LLM, which generates a precise answer.
6. **Response**: The answer is sent back to the frontend and displayed to the user in real-time.

---
### Project Structure 

```
DocuSense/
├── backend/                  # Flask backend logic
│   ├── app.py                # Main Flask application
│   ├── embedding_utils.py    # FAISS and model logic
│   └── requirements.txt      # Python dependencies
├── frontend/                 # React frontend
│   ├── src/
│   │   └── components/
│   │       └── UploadForm.js # File upload and Q&A UI
│   └── package.json
└── README.md
```
---
### Running Locally

To get the project up and running on your local machine, follow these steps.

### 1. Backend (Flask)
Navigate to the backend directory, install the required dependencies, and start the Flask server.
```
cd backend
pip install -r requirements.txt
python app.py
```

### 2. Frontend (React)
Open a new terminal, navigate to the frontend directory, install the Node.js packages, and start the development server.
```
cd frontend
npm install
npm start

```
---

## Usage

1.  Open the frontend in your browser.
2.  **Upload** a document (Drag & drop or Click).
3.  **Type** or **Speak** your question.
4.  View the answer and click **Show Debug Info** to see the underlying prompt.
---

## Author

• Mentor / Manager: Mr. Venkata Ramana Sudhakar Polavarapu

• Mudimala Yeshwanth Goud

 🛠️ Passionate about AI/ML, NLP, RAG, Data Science, system programming, full-stack development, and intelligent assistant systems.

---

## Contact
For any questions or collaboration, feel free to reach out:

Email: yeshwanth.mudimala@motivitylabs.com

---
