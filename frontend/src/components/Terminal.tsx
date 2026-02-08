interface TerminalProps {
  output: string;
  error?: string;
}

export default function Terminal({ output, error }: TerminalProps) {
  return (
    <div className="glass-panel p-4 h-full">
      <div className="text-xs uppercase tracking-[0.2em] text-dune/50">Terminal</div>
      <pre className="mt-3 whitespace-pre-wrap text-sm text-dune/80 min-h-[120px]">
        {output || "Run code to see output."}
      </pre>
      {error && (
        <pre className="mt-3 whitespace-pre-wrap text-sm text-ember/90">{error}</pre>
      )}
    </div>
  );
}
