### DocuSense: Document-Based Q&A Retrieval System
DocuSense is an intelligent document question-answering system that allows users to upload a PDF, ask questions in natural language, and receive context-aware answers. It leverages semantic search and large language models (LLMs) to extract relevant information from unstructured documents efficiently.

---

### Features
• **Intelligent PDF Reading**: Upload PDF documents to enable an intelligent Q&A session.

• **Semantic Search**: Utilizes SentenceTransformers and FAISS for fast and accurate semantic search.

• **AI-Generated Answers**: Employs Hugging Face Transformers to provide context-aware answers derived directly from the document.

• **Interactive UI**: A clean, responsive Q&A interface is built with React.js.

• **Scalable Backend**: The Flask backend handles all the logic for embeddings, search, and LLM responses, and is easily extendable for cloud deployment.

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

### Future Improvements
1. Expanded File Support: Add support for .docx and .txt file formats.
2. Multi-Document Context: Allow users to upload multiple documents and maintain a single Q&A context across them.
3. Authentication: Implement user authentication for handling private and secure documents.
4. Dockerization: Containerize the application using Docker for a more seamless and portable deployment experience.

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
