import type { FormEvent } from "react";
import type { ChatMessage } from "../lib/types";

interface TutorChatPanelProps {
  messages: ChatMessage[];
  input: string;
  busy?: boolean;
  placeholder?: string;
  onInputChange: (value: string) => void;
  onSubmit: () => void;
}

export default function TutorChatPanel({
  messages,
  input,
  busy = false,
  placeholder = "Ask a doubt...",
  onInputChange,
  onSubmit,
}: TutorChatPanelProps) {
  const handleSubmit = (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    onSubmit();
  };

  return (
    <div className="flex h-full min-h-0 flex-col bg-gray-950/50">
      <div className="flex-1 space-y-3 overflow-y-auto px-3 py-4">
        {messages.length === 0 ? (
          <div className="rounded-lg border border-white/8 bg-white/[0.03] px-3 py-4 text-sm leading-6 text-white/55">
            Ask for a hint or type a doubt to start.
          </div>
        ) : (
          messages.map((message, index) => (
            <div
              key={`${message.role}-${index}-${message.content.slice(0, 12)}`}
              className={`flex ${message.role === "student" ? "justify-end" : "justify-start"}`}
            >
              <div
                className={`max-w-[88%] rounded-lg px-3 py-2 text-sm leading-6 ${
                  message.role === "student"
                    ? "bg-blue-600/20 text-blue-50"
                    : "bg-white/[0.05] text-white/78"
                }`}
              >
                <div className="mb-1 text-[10px] font-medium uppercase tracking-[0.18em] text-white/38">
                  {message.role === "student" ? "You" : "Tutor"}
                </div>
                <div className="whitespace-pre-wrap break-words">{message.content}</div>
              </div>
            </div>
          ))
        )}
        {busy && (
          <div className="max-w-[88%] rounded-lg bg-white/[0.04] px-3 py-2 text-sm text-white/45">
            Thinking...
          </div>
        )}
      </div>

      <form className="flex-none border-t border-white/5 bg-neutral-950/75 p-3" onSubmit={handleSubmit}>
        <div className="relative">
          <textarea
            className="ui-textarea min-h-[64px] max-h-[112px] w-full resize-none rounded-lg px-3 py-2 pr-20 text-sm leading-5"
            value={input}
            placeholder={placeholder}
            onChange={(event) => onInputChange(event.target.value)}
            disabled={busy}
          />
          <button
            className="ui-button absolute bottom-2.5 right-2.5 rounded-md bg-blue-600 px-3 py-1.5 text-xs font-semibold text-white disabled:opacity-50"
            type="submit"
            disabled={busy || !input.trim()}
          >
            Send
          </button>
        </div>
      </form>
    </div>
  );
}
