import type { ProblemDetail } from "../lib/types";

interface ProblemPanelProps {
  problem?: ProblemDetail | null;
}

export default function ProblemPanel({ problem }: ProblemPanelProps) {
  if (!problem) {
    return (
      <div className="glass-panel p-5 text-sm text-dune/70">
        Select a problem to load the statement and buggy code.
      </div>
    );
  }

  return (
    <div className="glass-panel p-5 text-sm text-dune/80">
      <div className="text-xs uppercase text-dune/50">{problem.source}</div>
      <h3 className="mt-2 text-lg font-semibold text-dune">{problem.title}</h3>
      <div className="mt-3 whitespace-pre-wrap text-sm leading-6">{problem.statement}</div>
      {problem.bug_desc && (
        <div className="mt-4 text-xs text-mint">Bug description: {problem.bug_desc}</div>
      )}
    </div>
  );
}
