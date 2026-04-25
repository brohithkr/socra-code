import { useEffect, useRef, type KeyboardEvent } from "react";
import type { ChatMessage } from "../lib/types";

interface TutorChatPanelProps {
  messages: ChatMessage[];
  input: string;
  busy?: boolean;
  placeholder?: string;
  onInputChange: (value: string) => void;
  onSubmit: () => void;
}

const SendIcon = () => (
  <svg width="14" height="14" viewBox="0 0 16 16" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round">
    <path d="M3 8H13M9 4L13 8L9 12" />
  </svg>
);

export default function TutorChatPanel({
  messages,
  input,
  busy = false,
  placeholder = "Ask a question… (Enter to send)",
  onInputChange,
  onSubmit,
}: TutorChatPanelProps) {
  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [messages, busy]);

  const handleKeyDown = (e: KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      if (!busy && input.trim()) onSubmit();
    }
  };

  return (
    <div className="chat-panel">
      <div className="chat-messages" ref={scrollRef}>
        {messages.length === 0 && !busy ? (
          <div className="chat-empty">
            <div className="chat-empty-icon">✦</div>
            <p className="chat-empty-text">
              Ask for a hint using <strong>Ask AI</strong> above, or type a specific question below.
            </p>
          </div>
        ) : (
          messages.map((msg, i) => (
            <div
              key={`${msg.role}-${i}`}
              className={`chat-bubble-wrap ${msg.role}`}
            >
              <div className={`chat-avatar ${msg.role}`}>
                {msg.role === "tutor" ? "✦" : "U"}
              </div>
              <div>
                <div className="chat-role-label">
                  {msg.role === "tutor" ? "AI Tutor" : "You"}
                </div>
                <div className={`chat-bubble ${msg.role}`}>
                  {msg.content}
                </div>
              </div>
            </div>
          ))
        )}

        {busy && (
          <div className="chat-bubble-wrap tutor">
            <div className="chat-avatar tutor">✦</div>
            <div>
              <div className="chat-role-label">AI Tutor</div>
              <div className="typing-indicator">
                <div className="typing-dot" />
                <div className="typing-dot" />
                <div className="typing-dot" />
              </div>
            </div>
          </div>
        )}
      </div>

      <div className="chat-input-area">
        <div className="chat-input-row">
          <textarea
            className="chat-textarea"
            value={input}
            placeholder={placeholder}
            disabled={busy}
            onChange={(e) => onInputChange(e.target.value)}
            onKeyDown={handleKeyDown}
            rows={1}
          />
          <button
            className="chat-send-btn"
            onClick={onSubmit}
            disabled={busy || !input.trim()}
            title="Send (Enter)"
          >
            <SendIcon />
          </button>
        </div>
        <p style={{ fontSize: "10px", color: "var(--text-3)", marginTop: "5px", paddingLeft: "2px" }}>
          Enter to send · Shift+Enter for new line
        </p>
      </div>
    </div>
  );
}
