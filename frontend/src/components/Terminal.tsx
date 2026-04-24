interface TerminalProps {
  output: string;
  error?: string;
}

export default function Terminal({ output, error }: TerminalProps) {
  const primaryOutput = output || error || "// Output will appear here...";

  return (
    <div className="terminal-shell h-full">
      <div className="terminal-head flex items-center justify-between px-4 py-2">
        <span className="text-[11px] font-mono uppercase tracking-[0.24em] text-white/40">Console Output</span>
        <div className="flex gap-1.5">
          <div className="h-2.5 w-2.5 rounded-full bg-red-500/25" />
          <div className="h-2.5 w-2.5 rounded-full bg-yellow-500/25" />
          <div className="h-2.5 w-2.5 rounded-full bg-emerald-500/25" />
        </div>
      </div>
      <pre className="console-good min-h-[140px] whitespace-pre-wrap p-4 font-['Geist_Mono'] text-xs leading-6">
        {primaryOutput}
      </pre>
      {error && output && (
        <pre className="console-bad whitespace-pre-wrap border-t border-white/5 px-4 py-3 font-['Geist_Mono'] text-xs leading-6">
          {error}
        </pre>
      )}
    </div>
  );
}
