interface ModeCardProps {
  title: string;
  description: string;
  action: string;
  onClick: () => void;
  variant?: "practice" | "game";
  num?: string;
}

const PracticeIcon = () => (
  <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" strokeLinejoin="round">
    <path d="M2 3h6a4 4 0 0 1 4 4v14a3 3 0 0 0-3-3H2z" />
    <path d="M22 3h-6a4 4 0 0 0-4 4v14a3 3 0 0 1 3-3h7z" />
  </svg>
);

const GameIcon = () => (
  <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" strokeLinejoin="round">
    <path d="M6 9H4.5a2.5 2.5 0 0 0 0 5H6" />
    <path d="M18 9h1.5a2.5 2.5 0 0 1 0 5H18" />
    <path d="M4 9h16v10a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V9Z" />
    <path d="m10 13 2 2 2-2" />
    <path d="M12 8v7" />
  </svg>
);

export default function ModeCard({
  title,
  description,
  action,
  onClick,
  variant = "practice",
  num = "01",
}: ModeCardProps) {
  return (
    <button
      className={`mode-card ${variant}-card`}
      style={{ flex: 1, display: "flex", flexDirection: "column" }}
      onClick={onClick}
    >
      <div className="mode-card-num">{num}</div>
      <div className="mode-card-header">
        <div className={`mode-card-icon-wrap ${variant}-icon`}>
          {variant === "practice" ? <PracticeIcon /> : <GameIcon />}
        </div>
        <h3 className="mode-card-title">{title}</h3>
      </div>
      <p className="mode-card-desc">{description}</p>
      <span className="mode-card-action" style={{ marginTop: "auto" }}>
        {action}
        <svg width="12" height="12" viewBox="0 0 16 16" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round">
          <path d="M3 8H13M9 4L13 8L9 12" />
        </svg>
      </span>
    </button>
  );
}
