interface ScoreboardProps {
  players: Record<string, string>;
  scores: Record<string, number>;
  hints: Record<string, number>;
}

export default function Scoreboard({ players, scores, hints }: ScoreboardProps) {
  const entries = Object.entries(players);
  return (
    <div className="glass-panel p-4">
      <div className="text-xs uppercase tracking-[0.2em] text-dune/50">Scoreboard</div>
      <div className="mt-4 space-y-3">
        {entries.length === 0 && <div className="text-sm text-dune/60">No players yet.</div>}
        {entries.map(([id, name]) => (
          <div key={id} className="flex items-center justify-between text-sm">
            <div>
              <div className="font-medium text-dune">{name}</div>
              <div className="text-xs text-dune/60">Hints: {hints[id] ?? 0}</div>
            </div>
            <div className="font-display text-ember">{scores[id] ?? 0}</div>
          </div>
        ))}
      </div>
    </div>
  );
}
