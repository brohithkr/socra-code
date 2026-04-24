interface ScoreboardProps {
  players: Record<string, string>;
  scores: Record<string, number>;
  hints: Record<string, number>;
}

export default function Scoreboard({ players, scores, hints }: ScoreboardProps) {
  const entries = Object.entries(players);
  return (
    <div className="glass-panel p-5">
      <div className="text-[11px] uppercase tracking-[0.22em] text-white/42">Scoreboard</div>
      <div className="mt-4 space-y-3">
        {entries.length === 0 && <div className="text-sm text-white/55">No players yet.</div>}
        {entries.map(([id, name]) => (
          <div key={id} className="flex items-center justify-between rounded-2xl border border-white/5 bg-white/[0.025] px-4 py-3 text-sm">
            <div>
              <div className="font-medium text-white">{name}</div>
              <div className="text-xs text-white/48">Hints: {hints[id] ?? 0}</div>
            </div>
            <div className="text-xl font-semibold tracking-tight text-blue-300">{scores[id] ?? 0}</div>
          </div>
        ))}
      </div>
    </div>
  );
}
