interface HintPanelProps {
  hint: string;
  intent?: string;
  score?: number;
}

export default function HintPanel({ hint, intent, score }: HintPanelProps) {
  return (
    <div className="glass-panel h-full p-0">
      <div className="flex items-center justify-between px-3 pt-3 text-[11px] font-medium uppercase tracking-[0.22em] text-white/42">
        <span>Hint</span>
        {intent && <span className="bg-emerald-500/10 px-2 py-1 text-emerald-300">{intent}</span>}
      </div>
      <p className="min-h-[140px] px-3 pt-3 text-sm leading-7 text-white/78">
        {hint || "Ask for a hint when you get stuck."}
      </p>
      {score !== undefined && (
        <div className="px-3 py-2 text-xs text-white/42">Verifier score: {score.toFixed(1)}</div>
      )}
    </div>
  );
}
