import React, { useState } from "react";
import styles from "./App.module.css"; // Import CSS module

// FormControl component for modularizing form elements
const FormControl = ({ id, label, children, error }) => (
  <div className={styles.formGroup}>
    <label htmlFor={id} className={styles.label}>
      {label}
    </label>
    {children}
    {error && <p className={styles.errorText}>{error}</p>}
  </div>
);

function App() {
  const [file, setFile] = useState(null);
  const [question, setQuestion] = useState("");
  const [answer, setAnswer] = useState(null);
  const [prompt, setPrompt] = useState(null);
  const [debugInfo, setDebugInfo] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  // Externalize API endpoint
  const API_URL = process.env.REACT_APP_API_URL || "http://127.0.0.1:5000/";

  const handleFileChange = (e) => {
    const selectedFile = e.target.files[0];
    if (selectedFile) {
      // Client-side validation for file type
      if (selectedFile.type !== "text/plain") {
        setError("Only .txt files are allowed.");
        setFile(null); // Clear file selection
        e.target.value = null; // Reset file input visually
      } else {
        setError(null);
        setFile(selectedFile);
      }
    } else {
      setFile(null); // Clear file if nothing is selected (e.g., user cancels file dialog)
      setError(null);
    }
  };

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

    if (file.type !== "text/plain") { // Double-check in case validation was bypassed
      setError("Only .txt files are allowed. Please upload a valid file.");
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
      setError("Failed to fetch answer: " + err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
     <div className={styles.container}>
      <h1 className={styles.heading}>Ask a Question from Your Document</h1>

      <form onSubmit={handleSubmit}>
        <FormControl id="file" label="Upload a text file:" error={error && file === null ? error : null}>
          <input
            id="file"
            type="file"
            accept=".txt"
            className={styles.fileInput}
            onChange={handleFileChange}
            disabled={loading}
            required
          />
        </FormControl>

        <FormControl id="question" label="Enter your question:">
          <input
            id="question"
            type="text"
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            placeholder="Type your question here..."
            className={styles.textInput}
            disabled={loading}
            required
          />
        </FormControl>

        <button
          type="submit"
          disabled={loading}
          className={styles.button}
        >
          {loading ? "Asking..." : "Ask"}
        </button>
      </form>

      {error && !file && !question && <p className={styles.errorText}>{error}</p>} {/* Show general errors */}

      {answer && (
        <div className={styles.resultContainer}>
          <h2 className={styles.sectionTitle}>Answer:</h2>
          <p>{answer}</p>

          {/* Conditionally render 'Prompt Used' section */}
          {prompt && (
            <>
              <h3 className={styles.sectionTitle}>Prompt Used:</h3>
              <pre className={styles.preformatted}>{prompt}</pre>
            </>
          )}

          {/* Conditionally render 'Raw Output (Debug)' section */}
          {debugInfo && (
            <>
              <h3 className={styles.sectionTitle}>Raw Output (Debug):</h3>
              <pre className={styles.preformatted}>{debugInfo}</pre>
            </>
          )}
        </div>
      )}
    </div>
  );
}

export default App;