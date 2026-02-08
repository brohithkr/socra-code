interface HintPanelProps {
  hint: string;
  intent?: string;
  score?: number;
}

export default function HintPanel({ hint, intent, score }: HintPanelProps) {
  return (
    <div className="glass-panel p-4 h-full">
      <div className="flex items-center justify-between text-xs uppercase tracking-[0.2em] text-dune/50">
        <span>Hint</span>
        {intent && <span className="text-mint">{intent}</span>}
      </div>
      <p className="mt-4 text-sm text-dune/80 min-h-[120px]">
        {hint || "Ask for a hint when you get stuck."}
      </p>
      {score !== undefined && (
        <div className="mt-4 text-xs text-dune/50">Verifier score: {score.toFixed(1)}</div>
      )}
    </div>
  );
}
