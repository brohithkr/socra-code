interface TerminalProps {
  output: string;
  error?: string;
  exitCode?: number;
  durationMs?: number;
}

export default function Terminal({ output, error, exitCode, durationMs }: TerminalProps) {
  const hasOutput = !!output;
  const hasError = !!error;
  const hasRun = hasOutput || hasError;
  const success = hasRun && exitCode === 0;
  const failure = hasRun && typeof exitCode === "number" && exitCode !== 0;

  return (
    <div className="terminal-wrap" style={{ height: "100%" }}>
      <div className="terminal-chrome">
        <div className="terminal-dots">
          <div className="terminal-dot red" />
          <div className="terminal-dot yellow" />
          <div className="terminal-dot green" />
        </div>
        <span className="terminal-label">Output</span>
        {hasRun && (
          <span style={{ marginLeft: "auto" }}>
            {success && <span className="terminal-success-badge">✓ Exit 0{durationMs !== undefined ? ` · ${durationMs}ms` : ""}</span>}
            {failure && <span className="terminal-error-badge">✗ Exit {exitCode}{durationMs !== undefined ? ` · ${durationMs}ms` : ""}</span>}
          </span>
        )}
      </div>
      <div className="terminal-body">
        {!hasRun && (
          <span className="terminal-placeholder">// Run your code to see output here</span>
        )}
        {hasOutput && (
          <span className="terminal-stdout">{output}</span>
        )}
        {hasError && (
          <span className="terminal-stderr">{hasOutput ? "\n" : ""}{error}</span>
        )}
      </div>
    </div>
  );
}
