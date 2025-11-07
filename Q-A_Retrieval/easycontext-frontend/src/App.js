import React, { useState } from "react";
import styles from "./App.module.css";
import FileUploadInput from "./components/FileUploadInput";
import QuestionInput from "./components/QuestionInput";
import AnswerDisplay from "./components/AnswerDisplay";

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
      const response = await fetch("http://127.0.0.1:5000/", {
        method: "POST",
        body: formData,
      });

      if (!response.ok) {
        throw new Error(`Server error: ${response.statusText}`);
      }

      const data = await response.json();
      if (data.error) {
        setError(data.error);
      } else {
        setAnswer(data.answer);
        setPrompt(data.prompt);
        setDebugInfo(data.debug_info);
      }
    } catch (err) {
      setError("Failed to fetch answer. Please try again."); // Generalized error message
      console.error("Detailed error:", err); // Log detailed error internally
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className={styles.container}>
      <h1 className={styles.heading}>Ask a Question from Your Document</h1>

      <form onSubmit={handleSubmit}>
        <FileUploadInput onFileChange={setFile} disabled={loading} />
        <QuestionInput
          question={question}
          onQuestionChange={setQuestion}
          disabled={loading}
        />

        <button
          type="submit"
          disabled={loading}
          className={styles.button}
        >
          {loading ? "Asking..." : "Ask"}
        </button>
      </form>

      {error && <p className={styles.errorText}>{error}</p>}

      <AnswerDisplay answer={answer} prompt={prompt} debugInfo={debugInfo} />
    </div>
  );
}

export default App;