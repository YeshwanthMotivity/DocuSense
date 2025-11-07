import React, { useState } from "react";
import "./App.css"; // Centralize Styling

// Externalize API Endpoint
const API_URL = process.env.REACT_APP_API_URL || "http://127.0.0.1:5000/";

// Consider Component Splitting: QuestionForm Component
function QuestionForm({
  file,
  setFile,
  question,
  setQuestion,
  loading,
  handleSubmit,
}) {
  return (
    <form onSubmit={handleSubmit}>
      <div className="form-group">
        <label htmlFor="file" className="label">
          Upload a text file:
        </label>
        <input
          id="file"
          type="file"
          accept=".txt"
          className="file-input"
          onChange={(e) => setFile(e.target.files[0])}
          disabled={loading}
          required
        />
      </div>

      <div className="form-group">
        <label htmlFor="question" className="label">
          Enter your question:
        </label>
        <input
          id="question"
          type="text"
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          placeholder="Type your question here..."
          className="text-input"
          disabled={loading}
          required
        />
      </div>

      <button type="submit" disabled={loading} className="button">
        {loading ? "Asking..." : "Ask"}
      </button>
    </form>
  );
}

// Consider Component Splitting: AnswerDisplay Component
function AnswerDisplay({ answer, prompt, debugInfo }) {
  if (!answer) return null;

  return (
    <div className="result-container">
      <h2 className="section-title">Answer:</h2>
      <p>{answer}</p>

      <h3 className="section-title">Prompt Used:</h3>
      <pre className="preformatted">{prompt}</pre>

      <h3 className="section-title">Raw Output (Debug):</h3>
      <pre className="preformatted">{debugInfo}</pre>
    </div>
  );
}

function App() {
  const [file, setFile] = useState(null);
  const [question, setQuestion] = useState("");
  const [answer, setAnswer] = useState(null);
  const [prompt, setPrompt] = useState(null);
  const [debugInfo, setDebugInfo] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError(null);
    setAnswer(null);
    setPrompt(null);
    setDebugInfo(null);

    if (!file || !question) {
      setError("Please upload a file and enter a question.");
      return;
    }

    const formData = new FormData();
    formData.append("file", file);
    formData.append("question", question);

    setLoading(true);

    try {
      const response = await fetch(API_URL, {
        method: "POST",
        body: formData,
      });

      if (!response.ok) {
        // Improve Error Messaging: Log detailed error, display generic to user
        const errorData = await response.json().catch(() => ({})); // Try to parse error body
        console.error(
          "Server response error:",
          response.status,
          response.statusText,
          errorData.detail || errorData.error || "No detailed error message"
        );
        setError("An unexpected server error occurred. Please try again.");
        return;
      }

      const data = await response.json();
      if (data.error) {
        // Improve Error Messaging: Log detailed error, display generic or specific error from server
        console.error("API returned an error:", data.error);
        setError("Error processing your request: " + data.error); // Display server-provided error if present
      } else {
        setAnswer(data.answer);
        setPrompt(data.prompt);
        setDebugInfo(data.debug_info);
      }
    } catch (err) {
      // Improve Error Messaging: Log detailed error, display generic to user
      console.error("Failed to fetch answer:", err);
      setError(
        "Failed to connect to the server or process your request. Please check your internet connection and try again."
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="container">
      <h1 className="heading">Ask a Question from Your Document</h1>

      <QuestionForm
        file={file}
        setFile={setFile}
        question={question}
        setQuestion={setQuestion}
        loading={loading}
        handleSubmit={handleSubmit}
      />

      {error && <p className="error-text">{error}</p>}

      <AnswerDisplay answer={answer} prompt={prompt} debugInfo={debugInfo} />
    </div>
  );
}

export default App;