import React, { useReducer, useCallback } from "react";
import styles from "./App.module.css";
import useApiQuery from "./useApiQuery";
import DocumentUploadForm from "./DocumentUploadForm";
import QueryResultDisplay from "./QueryResultDisplay";

const initialAppState = {
  file: null,
  question: "",
  answer: null,
  prompt: null,
  debugInfo: null,
  localError: null, // For validation errors before API call
};

function appReducer(state, action) {
  switch (action.type) {
    case "SET_FILE":
      return { ...state, file: action.payload, localError: null };
    case "SET_QUESTION":
      return { ...state, question: action.payload, localError: null };
    case "SET_API_RESULT":
      return {
        ...state,
        answer: action.payload.answer,
        prompt: action.payload.prompt,
        debugInfo: action.payload.debug_info,
        localError: null,
      };
    case "SET_LOCAL_ERROR":
      return { ...state, localError: action.payload };
    case "RESET_RESULTS":
      return { ...state, answer: null, prompt: null, debugInfo: null, localError: null };
    default:
      return state;
  }
}

function App() {
  const [state, dispatch] = useReducer(appReducer, initialAppState);
  const { file, question, answer, prompt, debugInfo, localError } = state;

  const {
    execute: executeApiQuery,
    loading: apiLoading,
    error: apiError,
    reset: resetApiQuery,
  } = useApiQuery("http://127.0.0.1:5000/", "POST");

  const handleSubmit = useCallback(
    async (e) => {
      e.preventDefault();
      dispatch({ type: "RESET_RESULTS" }); // Clear previous results and local error
      resetApiQuery(); // Clear previous API errors and data

      if (!file || !question.trim()) {
        dispatch({
          type: "SET_LOCAL_ERROR",
          payload: "Please upload a file and enter a question.",
        });
        return;
      }

      const formData = new FormData();
      formData.append("file", file);
      formData.append("question", question);

      try {
        const data = await executeApiQuery(formData);
        dispatch({ type: "SET_API_RESULT", payload: data });
      } catch (err) {
        // API error is handled by useApiQuery hook, its error state will update.
        // No need to dispatch a local error here as apiError will reflect it.
      }
    },
    [file, question, executeApiQuery, resetApiQuery]
  );

  const handleFileChange = useCallback((e) => {
    dispatch({ type: "SET_FILE", payload: e.target.files[0] });
  }, []);

  const handleQuestionChange = useCallback((e) => {
    dispatch({ type: "SET_QUESTION", payload: e.target.value });
  }, []);

  const currentError = localError || apiError;
  const isLoading = apiLoading;

  return (
    <div className={styles.container} aria-busy={isLoading ? "true" : "false"}>
      <h1 className={styles.heading}>Ask a Question from Your Document</h1>

      <DocumentUploadForm
        file={file}
        question={question}
        onFileChange={handleFileChange}
        onQuestionChange={handleQuestionChange}
        onSubmit={handleSubmit}
        loading={isLoading}
        error={currentError} // Pass combined error
      />

      <QueryResultDisplay answer={answer} prompt={prompt} debugInfo={debugInfo} />
    </div>
  );
}

export default App;