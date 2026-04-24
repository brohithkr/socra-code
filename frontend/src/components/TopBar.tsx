import React, { type ChangeEvent } from "react";
import clsx from "clsx";
import type { ProblemSummary, Language } from "../lib/types";

interface TopBarProps {
  mode: "home" | "practice" | "game";
  onBack?: () => void;
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

export default function TopBar({
  mode,
  onBack,
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
    <header className="flex items-center justify-between bg-white/[0.03] px-2 py-2 backdrop-blur-sm">
      <div className="flex items-center gap-3">
        <div className="flex h-11 w-11 items-center justify-center rounded-xl border border-blue-400/20 bg-gradient-to-br from-blue-500/80 to-indigo-500 text-lg font-semibold text-white shadow-[inset_0_1px_0_rgba(255,255,255,0.2)]">
          S
        </div>
        <div>
          <div className="text-lg font-semibold tracking-tight text-white">Socratic Sprint</div>
          <div className="text-[11px] font-medium uppercase tracking-[0.24em] text-white/45">Socratic Tutor</div>
        </div>
      </div>
      <div className="flex flex-wrap items-center justify-end gap-2">
        {mode === "practice" && language && onLanguageChange && (
          <>
            <select
              className="ui-select rounded-lg px-3 py-1.5 text-xs text-neutral-300"
              value={language}
              onChange={(e: ChangeEvent<HTMLSelectElement>) => onLanguageChange(e.target.value as Language)}
            >
              <option value="python">Python</option>
              <option value="java">Java</option>
              <option value="cpp">C++</option>
            </select>
            <select
              className="ui-select max-w-[220px] rounded-lg px-3 py-1.5 text-xs text-neutral-300"
              value={selectedProblemId}
              onChange={(e: ChangeEvent<HTMLSelectElement>) => onProblemSelect?.(e.target.value)}
            >
              <option value="">Select a problem</option>
              {problems.map((problem) => (
                <option key={problem.id} value={problem.id}>
                  {problem.title}
                </option>
              ))}
            </select>
            {onRun && (
              <button
                className="ui-button rounded-lg bg-emerald-500/10 px-3 py-1.5 text-xs font-semibold text-emerald-300 border border-emerald-500/25"
                onClick={onRun}
                disabled={running}
              >
                {running ? "Running..." : "Run"}
              </button>
            )}
            {onAsk && (
              <button
                className="ui-button rounded-lg bg-blue-500/10 px-3 py-1.5 text-xs font-semibold text-blue-300 border border-blue-500/25"
                onClick={onAsk}
                disabled={analyzing}
              >
                {analyzing ? "Asking..." : "Ask AI"}
              </button>
            )}
            {onClear && (
              <button
                className="ui-button rounded-lg bg-white/[0.03] px-3 py-1.5 text-xs font-semibold text-white/85 border border-white/10"
                onClick={onClear}
              >
                Clear
              </button>
            )}
          </>
        )}
        <span
          className={clsx(
            "status-pill px-2 py-1 text-[11px] font-medium uppercase tracking-[0.22em]",
            mode === "practice" && "border-blue-500/20 bg-blue-500/10 text-blue-300",
            mode === "game" && "border-emerald-500/20 bg-emerald-500/10 text-emerald-300",
            mode === "home" && "text-white/60"
          )}
        >
          {mode}
        </span>
        {onBack && (
          <button
            className="ui-button bg-white/[0.03] px-3 py-2 text-sm text-white/85"
            onClick={onBack}
          >
            Back
          </button>
        )}
      </div>
    </header>
  );
}
