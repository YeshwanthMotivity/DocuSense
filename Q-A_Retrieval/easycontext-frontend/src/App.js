import React, { useState } from "react";
import useDocumentQnA from "./useDocumentQnA";
import FileUploadForm from "./FileUploadForm";
import ResultDisplay from "./ResultDisplay";
import styles from "./App.module.css";

function App() {
  const [file, setFile] = useState(null);
  const [question, setQuestion] = useState("");
  const { loading, error, answer, prompt, debugInfo, askQuestion } = useDocumentQnA();

  const handleSubmit = (e) => {
    e.preventDefault();
    askQuestion(file, question);
  };

  return (
    <div className={styles.container}>
      <h1 className={styles.heading}>Ask a Question from Your Document</h1>

      <FileUploadForm
        file={file}
        setFile={setFile}
        question={question}
        setQuestion={setQuestion}
        onSubmit={handleSubmit}
        loading={loading}
      />

      <div
        aria-live="polite"
        aria-atomic="true"
        className={styles.statusRegion}
      >
        {loading && <p className={styles.loadingText}>Loading...</p>}
        {error && <p className={styles.errorText}>{error}</p>}
      </div>

      <ResultDisplay
        answer={answer}
        prompt={prompt}
        debugInfo={debugInfo}
      />
    </div>
  );
}

export default App;