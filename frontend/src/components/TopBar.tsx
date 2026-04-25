import { type ChangeEvent } from "react";
import type { ProblemSummary, Language } from "../lib/types";

interface TopBarProps {
  mode: "home" | "practice" | "game" | "about";
  onBack?: () => void;
  onAbout?: () => void;
  language?: Language;
  onLanguageChange?: (language: Language) => void;
  problems?: ProblemSummary[];
  selectedProblemId?: string;
  onProblemSelect?: (id: string) => void;
  onRun?: () => void;
  onAsk?: () => void;
  onClear?: () => void;
  running?: boolean;
  analyzing?: boolean;
}

const PlayIcon = () => (
  <svg width="11" height="11" viewBox="0 0 12 12" fill="currentColor">
    <path d="M2.5 1.5L10 6L2.5 10.5V1.5Z" />
  </svg>
);

const SparkleIcon = () => (
  <svg width="12" height="12" viewBox="0 0 16 16" fill="currentColor">
    <path d="M8 0L9.5 6.5L16 8L9.5 9.5L8 16L6.5 9.5L0 8L6.5 6.5L8 0Z" />
  </svg>
);

const ArrowLeftIcon = () => (
  <svg width="13" height="13" viewBox="0 0 16 16" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <path d="M10 3L5 8L10 13" />
  </svg>
);

const XIcon = () => (
  <svg width="11" height="11" viewBox="0 0 16 16" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round">
    <path d="M3 3L13 13M13 3L3 13" />
  </svg>
);

const InfoIcon = () => (
  <svg width="12" height="12" viewBox="0 0 16 16" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <circle cx="8" cy="8" r="7" />
    <path d="M8 7v5M8 5v.5" />
  </svg>
);

export default function TopBar({
  mode,
  onBack,
  onAbout,
  language,
  onLanguageChange,
  problems = [],
  selectedProblemId = "",
  onProblemSelect,
  onRun,
  onAsk,
  onClear,
  running = false,
  analyzing = false,
}: TopBarProps) {
  return (
    <header className="topbar">
      {/* Left: brand */}
      <div className="flex items-center gap-3">
        {onBack && (
          <button
            className="btn btn-ghost"
            style={{ padding: "5px 10px", fontSize: "12px" }}
            onClick={onBack}
          >
            <ArrowLeftIcon />
            Back
          </button>
        )}
        <div className="logo-mark">S</div>
        <div>
          <div className="brand-name">SocraCode</div>
          <div className="brand-sub">Socratic Code Learning</div>
        </div>
      </div>

      {/* Right: controls */}
      <div className="flex items-center gap-2 flex-wrap justify-end">
        {mode === "practice" && language && onLanguageChange && (
          <>
            <select
              className="ui-select"
              style={{ padding: "5px 28px 5px 10px", height: "32px" }}
              value={language}
              onChange={(e: ChangeEvent<HTMLSelectElement>) => onLanguageChange(e.target.value as Language)}
            >
              <option value="python">Python</option>
              <option value="java">Java</option>
              <option value="cpp">C++</option>
            </select>
            <select
              className="ui-select"
              style={{ padding: "5px 28px 5px 10px", height: "32px", maxWidth: "200px" }}
              value={selectedProblemId}
              onChange={(e: ChangeEvent<HTMLSelectElement>) => onProblemSelect?.(e.target.value)}
            >
              <option value="">Select a problem…</option>
              {problems.map((p) => (
                <option key={p.id} value={p.id}>
                  {p.title}
                </option>
              ))}
            </select>
            <div style={{ width: "1px", height: "20px", background: "var(--border-2)", margin: "0 2px" }} />
            {onRun && (
              <button
                className="btn btn-run"
                style={{ padding: "5px 12px", height: "32px" }}
                onClick={onRun}
                disabled={running}
              >
                <PlayIcon />
                {running ? "Running…" : "Run"}
              </button>
            )}
            {onAsk && (
              <button
                className="btn btn-hint"
                style={{ padding: "5px 12px", height: "32px" }}
                onClick={onAsk}
                disabled={analyzing}
              >
                <SparkleIcon />
                {analyzing ? "Thinking…" : "Ask AI"}
              </button>
            )}
            {onClear && (
              <button
                className="btn btn-ghost"
                style={{ padding: "5px 10px", height: "32px" }}
                onClick={onClear}
                title="Clear session"
              >
                <XIcon />
              </button>
            )}
          </>
        )}

        {mode === "home" && onAbout && (
          <button
            className="btn btn-ghost"
            style={{ padding: "5px 12px", height: "32px", fontSize: "12px" }}
            onClick={onAbout}
          >
            <InfoIcon />
            About
          </button>
        )}

        <span className={`mode-badge mode-${mode}`}>
          {mode !== "home" && mode !== "about" && <span className="dot" />}
          {mode}
        </span>
      </div>
    </header>
  );
}
