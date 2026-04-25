interface ScoreboardProps {
  players: Record<string, string>;
  scores: Record<string, number>;
  hints: Record<string, number>;
}

const RANK_LABELS = ["1", "2", "3"];

export default function Scoreboard({ players, scores, hints }: ScoreboardProps) {
  const entries = Object.entries(players)
    .map(([id, name]) => ({ id, name, score: scores[id] ?? 0, hints: hints[id] ?? 0 }))
    .sort((a, b) => b.score - a.score);

  return (
    <div className="scoreboard">
      <div className="panel-header">
        <div className="panel-icon" style={{ background: "var(--ember-soft)", color: "var(--ember)" }}>
          <svg width="11" height="11" viewBox="0 0 16 16" fill="currentColor">
            <path d="M8 1L10 6H15L11 9.5L12.5 15L8 12L3.5 15L5 9.5L1 6H6L8 1Z" />
          </svg>
        </div>
        <span className="panel-header-title">Scoreboard</span>
      </div>
      <div>
        {entries.length === 0 ? (
          <div style={{ padding: "18px 16px", fontSize: "12px", color: "var(--text-3)" }}>
            No players yet — waiting for connections…
          </div>
        ) : (
          entries.map((entry, i) => (
            <div key={entry.id} className="score-row">
              <span className={`score-rank ${i < 3 ? `rank-${i + 1}` : ""}`}>
                {RANK_LABELS[i] ?? i + 1}
              </span>
              <div style={{ flex: 1, minWidth: 0 }}>
                <div className="score-name">{entry.name}</div>
                <div className="score-hints">{entry.hints} hint{entry.hints !== 1 ? "s" : ""} used</div>
              </div>
              <div className="score-val">{entry.score}</div>
            </div>
          ))
        )}
      </div>
    </div>
  );
}
