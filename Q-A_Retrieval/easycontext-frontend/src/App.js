import React, { useState, useRef, useEffect, useCallback } from "react";
import {
  FileText,
  Send,
  UploadCloud,
  Bot,
  User,
  ChevronDown,
  ChevronUp,
  FileCheck,
  Mic,
  Volume2,
  StopCircle
} from "lucide-react";

/**
 * Enhanced DocuSense AI Frontend
 * Features: Drag & Drop, Smooth Scrolling, Glassmorphism UI, Responsive Design, Voice I/O
 */

const App = () => {
  const [file, setFile] = useState(null);
  const [input, setInput] = useState("");
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(false);
  const [isDragging, setIsDragging] = useState(false);
  const [isListening, setIsListening] = useState(false);

  const messagesEndRef = useRef(null);
  const fileInputRef = useRef(null);

  const scrollToBottom = useCallback(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, []);

  useEffect(() => {
    scrollToBottom();
  }, [messages, loading, scrollToBottom]);

  // Voice Input Handler
  const startListening = () => {
    if (!('webkitSpeechRecognition' in window)) {
      alert("Voice input is not supported in this browser. Please use Chrome.");
      return;
    }
    const recognition = new window.webkitSpeechRecognition();
    recognition.continuous = false;
    recognition.interimResults = false;
    recognition.lang = 'en-US';

    recognition.onstart = () => setIsListening(true);
    recognition.onend = () => setIsListening(false);

    recognition.onresult = (event) => {
      const transcript = event.results[0][0].transcript;
      setInput(prev => prev + " " + transcript);
    };

    recognition.start();
  };

  // Voice Output Handler
  const speakText = (text) => {
    const utterance = new SpeechSynthesisUtterance(text);
    window.speechSynthesis.speak(utterance);
  };

  // File Handlers
  const handleFileChange = (e) => {
    const selectedFile = e.target.files?.[0];
    if (selectedFile) setFile(selectedFile);
  };

  const onDragOver = (e) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const onDragLeave = () => setIsDragging(false);

  const onDrop = (e) => {
    e.preventDefault();
    setIsDragging(false);
    const droppedFile = e.dataTransfer.files?.[0];
    if (droppedFile) setFile(droppedFile);
  };

  const handleSend = async (e) => {
    e.preventDefault();

    if (!input.trim()) return;

    if (!file && messages.length === 0) {
      const errorMsg = {
        role: "system",
        content: "Please upload a document before asking questions.",
        type: "error"
      };
      setMessages(prev => [...prev, errorMsg]);
      return;
    }

    const userMessage = { role: "user", content: input };
    setMessages((prev) => [...prev, userMessage]);

    // Prepare history for backend
    const history = messages.map(m => ({ role: m.role, content: m.content }));

    setInput("");
    setLoading(true);

    const formData = new FormData();
    if (file) formData.append("file", file);
    formData.append("question", userMessage.content);
    formData.append("history", JSON.stringify(history));

    try {
      const response = await fetch("http://127.0.0.1:5000/", {
        method: "POST",
        body: formData,
      });

      if (!response.ok) throw new Error(`Server status: ${response.status}`);

      const data = await response.json();
      const botMessage = {
        role: "bot",
        content: data.error ? `Error: ${data.error}` : data.answer,
        details: data.error ? null : { prompt: data.prompt, debug: data.debug_info }
      };

      setMessages((prev) => [...prev, botMessage]);
    } catch (err) {
      setMessages((prev) => [
        ...prev,
        { role: "bot", content: `Connection Error: ${err.message}`, type: "error" }
      ]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="app-wrapper">
      <div className="App">
        {/* Header Section */}
        <header className="app-header">
          <div className="logo-area">
            <div className="logo-icon">
              <Bot size={32} strokeWidth={2.5} />
            </div>
            <div>
              <h1 className="app-title">DocuSense AI</h1>
              <p className="app-subtitle">Intelligent Document Q&A</p>
            </div>
          </div>
        </header>

        <main className="main-container">
          {/* Enhanced Upload Section */}
          <div
            className={`upload-section ${isDragging ? "dragging" : ""} ${file ? "has-file" : ""}`}
            onDragOver={onDragOver}
            onDragLeave={onDragLeave}
            onDrop={onDrop}
            onClick={() => fileInputRef.current?.click()}
          >
            <input
              type="file"
              ref={fileInputRef}
              className="hidden-input"
              accept=".txt,.pdf,.docx,.doc"
              onChange={handleFileChange}
            />

            <div className="upload-content">
              {file ? (
                <>
                  <FileCheck className="icon-success" size={24} />
                  <span className="file-name">{file.name}</span>
                  <span className="upload-hint">(Click to change)</span>
                </>
              ) : (
                <>
                  <UploadCloud size={24} />
                  <span className="upload-text">Drop document or click to browse</span>
                  <span className="upload-hint">Supports PDF, DOCX, TXT</span>
                </>
              )}
            </div>
          </div>

          {/* Chat Window */}
          <div className="chat-window">
            {messages.length === 0 && !loading && (
              <div className="empty-state">
                <FileText size={48} className="empty-icon" />
                <h3>Ready to Analyze</h3>
                <p>Upload a document and ask your first question to begin the extraction process.</p>
              </div>
            )}

            {messages.map((msg, index) => (
              <div key={index} className={`message-wrapper ${msg.role}`}>
                <div className="avatar">
                  {msg.role === "user" ? <User size={18} /> : <Bot size={18} />}
                </div>
                <div className={`message-bubble ${msg.type === 'error' ? 'error' : ''}`}>
                  <div className="message-content">{msg.content}</div>

                  {msg.role === 'bot' && !msg.type && (
                    <div className="message-actions">
                      <button onClick={() => speakText(msg.content)} className="action-btn" title="Read Aloud">
                        <Volume2 size={14} />
                      </button>
                    </div>
                  )}

                  {msg.details && <DetailsBox details={msg.details} />}
                </div>
              </div>
            ))}

            {loading && (
              <div className="message-wrapper bot">
                <div className="avatar">
                  <Bot size={18} />
                </div>
                <div className="typing-indicator">
                  <span className="dot"></span>
                  <span className="dot"></span>
                  <span className="dot"></span>
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>

          {/* Persistent Input Bar */}
          <form className="input-area" onSubmit={handleSend}>
            <button
              type="button"
              className={`mic-button ${isListening ? 'listening' : ''}`}
              onClick={startListening}
              title="Voice Input"
            >
              {isListening ? <StopCircle size={20} /> : <Mic size={20} />}
            </button>
            <input
              type="text"
              className="chat-input"
              placeholder={file ? "Ask about the document..." : "Upload a file first..."}
              value={input}
              onChange={(e) => setInput(e.target.value)}
              disabled={loading}
            />
            <button
              type="submit"
              className="send-button"
              disabled={loading || !input.trim()}
            >
              <Send size={20} />
            </button>
          </form>
        </main>
      </div>

      <style>{`
        :root {
          --primary: #6366f1;
          --primary-hover: #4f46e5;
          --bg-gradient: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);
          --glass-bg: rgba(255, 255, 255, 0.8);
          --glass-border: rgba(255, 255, 255, 0.4);
          --text-main: #1e293b;
          --text-muted: #64748b;
          --user-bubble: #6366f1;
          --bot-bubble: #ffffff;
          --radius: 16px;
          --shadow-lg: 0 10px 25px -5px rgba(0, 0, 0, 0.1), 0 8px 10px -6px rgba(0, 0, 0, 0.1);
        }

        .app-wrapper {
          min-height: 100vh;
          background: var(--bg-gradient);
          padding: 20px;
          display: flex;
          justify-content: center;
          font-family: 'Inter', system-ui, -apple-system, sans-serif;
        }

        .App {
          width: 100%;
          max-width: 1000px;
          display: flex;
          flex-direction: column;
          height: calc(100vh - 40px);
        }

        .app-header {
          margin-bottom: 20px;
          display: flex;
          justify-content: center;
        }

        .logo-area {
          display: flex;
          align-items: center;
          gap: 16px;
          background: var(--glass-bg);
          padding: 12px 24px;
          border-radius: 50px;
          border: 1px solid var(--glass-border);
          box-shadow: var(--shadow-lg);
          backdrop-filter: blur(10px);
        }

        .logo-icon {
          background: var(--primary);
          color: white;
          padding: 10px;
          border-radius: 14px;
          display: flex;
          align-items: center;
          justify-content: center;
        }

        .app-title {
          margin: 0;
          font-size: 1.5rem;
          font-weight: 800;
          color: var(--text-main);
          letter-spacing: -0.025em;
        }

        .app-subtitle {
          margin: 0;
          font-size: 0.85rem;
          color: var(--text-muted);
          font-weight: 500;
        }

        .main-container {
          flex: 1;
          background: var(--glass-bg);
          backdrop-filter: blur(12px);
          border: 1px solid var(--glass-border);
          border-radius: var(--radius);
          box-shadow: var(--shadow-lg);
          display: flex;
          flex-direction: column;
          overflow: hidden;
        }

        /* Upload Styling */
        .upload-section {
          padding: 16px;
          border-bottom: 1px solid rgba(0,0,0,0.05);
          transition: all 0.3s ease;
          cursor: pointer;
          background: rgba(255,255,255,0.4);
        }

        .upload-section.dragging {
          background: rgba(99, 102, 241, 0.1);
          border-bottom: 1px solid var(--primary);
        }

        .upload-content {
          display: flex;
          align-items: center;
          justify-content: center;
          gap: 12px;
          color: var(--text-muted);
        }

        .hidden-input { display: none; }

        .file-name {
          color: var(--primary);
          font-weight: 600;
          font-size: 0.95rem;
        }

        .icon-success { color: #10b981; }

        .upload-hint {
          font-size: 0.75rem;
          opacity: 0.6;
        }

        /* Chat Window */
        .chat-window {
          flex: 1;
          padding: 24px;
          overflow-y: auto;
          display: flex;
          flex-direction: column;
          gap: 20px;
          scroll-behavior: smooth;
        }

        .empty-state {
          text-align: center;
          margin: auto;
          color: var(--text-muted);
          max-width: 300px;
        }

        .empty-icon {
          margin-bottom: 16px;
          opacity: 0.2;
          color: var(--primary);
        }

        .message-wrapper {
          display: flex;
          gap: 12px;
          max-width: 85%;
          animation: slideUp 0.3s ease-out;
        }

        .message-wrapper.user {
          align-self: flex-end;
          flex-direction: row-reverse;
        }

        .avatar {
          width: 34px;
          height: 34px;
          border-radius: 10px;
          display: flex;
          align-items: center;
          justify-content: center;
          flex-shrink: 0;
        }

        .user .avatar { background: #e0e7ff; color: var(--primary); }
        .bot .avatar { background: #f1f5f9; color: var(--text-muted); }

        .message-bubble {
          padding: 12px 16px;
          border-radius: var(--radius);
          font-size: 0.95rem;
          line-height: 1.5;
          box-shadow: 0 2px 4px rgba(0,0,0,0.02);
        }

        .user .message-bubble {
          background: var(--user-bubble);
          color: white;
          border-top-right-radius: 4px;
        }

        .bot .message-bubble {
          background: var(--bot-bubble);
          color: var(--text-main);
          border: 1px solid rgba(0,0,0,0.05);
          border-top-left-radius: 4px;
        }

        .error { border: 1px solid #fee2e2 !important; background: #fffafb !important; color: #b91c1c !important; }

        .message-actions {
            margin-top: 8px;
            display: flex;
            justify-content: flex-end;
        }
        
        .action-btn {
            background: none;
            border: none;
            cursor: pointer;
            color: var(--text-muted);
            opacity: 0.6;
            transition: opacity 0.2s;
            padding: 2px;
        }
        
        .action-btn:hover {
            opacity: 1;
            color: var(--primary);
        }

        /* Input Area */
        .input-area {
          padding: 20px;
          background: white;
          display: flex;
          gap: 12px;
          border-top: 1px solid rgba(0,0,0,0.05);
        }
        
        .mic-button {
            background: #f1f5f9;
            border: none;
            color: var(--text-muted);
            border-radius: 12px;
            width: 48px;
            display: flex;
            align-items: center;
            justify-content: center;
            cursor: pointer;
            transition: all 0.2s;
        }
        
        .mic-button:hover {
            background: #e2e8f0;
            color: var(--text-main);
        }
        
        .mic-button.listening {
            background: #fee2e2;
            color: #ef4444;
            animation: pulse 1.5s infinite;
        }
        
        @keyframes pulse {
            0% { box-shadow: 0 0 0 0 rgba(239, 68, 68, 0.4); }
            70% { box-shadow: 0 0 0 10px rgba(239, 68, 68, 0); }
            100% { box-shadow: 0 0 0 0 rgba(239, 68, 68, 0); }
        }

        .chat-input {
          flex: 1;
          background: #f8fafc;
          border: 1px solid #e2e8f0;
          border-radius: 12px;
          padding: 12px 16px;
          font-size: 1rem;
          transition: all 0.2s;
        }

        .chat-input:focus {
          outline: none;
          border-color: var(--primary);
          background: white;
          box-shadow: 0 0 0 4px rgba(99, 102, 241, 0.1);
        }

        .send-button {
          background: var(--primary);
          color: white;
          border: none;
          border-radius: 12px;
          width: 48px;
          display: flex;
          align-items: center;
          justify-content: center;
          cursor: pointer;
          transition: transform 0.2s, background 0.2s;
        }

        .send-button:hover:not(:disabled) {
          background: var(--primary-hover);
          transform: translateY(-1px);
        }

        .send-button:disabled { opacity: 0.5; cursor: not-allowed; }

        /* Typing Indicator */
        .typing-indicator {
          display: flex;
          gap: 4px;
          padding: 12px 16px;
          background: #f1f5f9;
          border-radius: var(--radius);
        }

        .dot {
          width: 6px;
          height: 6px;
          background: #94a3b8;
          border-radius: 50%;
          animation: typingDot 1.4s infinite;
        }
        .dot:nth-child(2) { animation-delay: 0.2s; }
        .dot:nth-child(3) { animation-delay: 0.4s; }

        @keyframes typingDot {
          0%, 60%, 100% { transform: translateY(0); }
          30% { transform: translateY(-4px); }
        }

        @keyframes slideUp {
          from { opacity: 0; transform: translateY(10px); }
          to { opacity: 1; transform: translateY(0); }
        }

        /* Scrollbar */
        .chat-window::-webkit-scrollbar { width: 6px; }
        .chat-window::-webkit-scrollbar-thumb { background: #cbd5e1; border-radius: 10px; }
      `}</style>
    </div>
  );
};

const DetailsBox = ({ details }) => {
  const [isOpen, setIsOpen] = useState(false);

  return (
    <div className="details-container">
      <button
        type="button"
        onClick={() => setIsOpen(!isOpen)}
        className="details-toggle"
      >
        {isOpen ? <ChevronUp size={14} /> : <ChevronDown size={14} />}
        {isOpen ? "Hide Debug Info" : "Show Debug Info"}
      </button>

      {isOpen && (
        <div className="details-content">
          <div className="detail-section">
            <h6>Prompt Construction</h6>
            <pre>{details.prompt}</pre>
          </div>
          <div className="detail-section">
            <h6>Model Analysis</h6>
            <code>{details.debug}</code>
          </div>
        </div>
      )}

      <style>{`
        .details-container {
          margin-top: 10px;
          border-top: 1px solid rgba(0,0,0,0.05);
          padding-top: 8px;
        }
        .details-toggle {
          background: none;
          border: none;
          color: var(--text-muted);
          font-size: 0.75rem;
          font-weight: 600;
          cursor: pointer;
          display: flex;
          align-items: center;
          gap: 4px;
          padding: 4px 0;
        }
        .details-toggle:hover { color: var(--primary); }
        .details-content {
          background: #f8fafc;
          border-radius: 8px;
          padding: 10px;
          margin-top: 8px;
          font-size: 0.7rem;
          border: 1px solid rgba(0,0,0,0.05);
        }
        .detail-section h6 {
          margin: 0 0 4px 0;
          color: var(--text-main);
          text-transform: uppercase;
          letter-spacing: 0.05em;
          font-size: 0.65rem;
        }
        .detail-section pre, .detail-section code {
          display: block;
          white-space: pre-wrap;
          word-break: break-all;
          color: var(--text-muted);
          font-family: 'JetBrains Mono', monospace;
        }
        .detail-section:not(:last-child) { margin-bottom: 8px; }
      `}</style>
    </div>
  );
};

export default App;
