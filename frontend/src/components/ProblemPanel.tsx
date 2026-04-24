import type { ProblemDetail } from "../lib/types";

interface ProblemPanelProps {
  problem?: ProblemDetail | null;
}

export default function ProblemPanel({ problem }: ProblemPanelProps) {
  if (!problem) {
    return (
      <div className="glass-panel p-0 text-sm text-white/58">
        Select a problem to load the statement and buggy code.
      </div>
    );
  }

  return (
    <div className="glass-panel p-0 text-sm text-white/78">
      <div className="px-3 pt-3 text-[11px] uppercase tracking-[0.22em] text-white/42">{problem.source}</div>
      <h3 className="px-3 pt-2 text-lg font-semibold text-white">{problem.title}</h3>
      <div className="whitespace-pre-wrap px-3 pt-3 text-sm leading-7 text-white/68">{problem.statement}</div>
      {problem.bug_desc && (
        <div className="mt-3 bg-emerald-500/8 px-3 py-2 text-xs leading-6 text-emerald-200/85">
          Bug description: {problem.bug_desc}
        </div>
      )}
    </div>
  );
}
