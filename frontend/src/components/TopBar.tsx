interface TopBarProps {
  mode: "home" | "practice" | "game" | "about";
  onBack?: () => void;
  onAbout?: () => void;
}

const ArrowLeftIcon = () => (
  <svg width="13" height="13" viewBox="0 0 16 16" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <path d="M10 3L5 8L10 13" />
  </svg>
);

const InfoIcon = () => (
  <svg width="12" height="12" viewBox="0 0 16 16" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <circle cx="8" cy="8" r="7" />
    <path d="M8 7v5M8 5v.5" />
  </svg>
);

export default function TopBar({ mode, onBack, onAbout }: TopBarProps) {
  return (
    <header className="topbar">
      {/* Left: brand + optional back */}
      <div className="flex items-center gap-3">
        {onBack && (
          <button
            className="btn btn-ghost"
            style={{ padding: "5px 10px", fontSize: "12px" }}
            onClick={onBack}
          >
            <ArrowLeftIcon />
            Back
          </button>
        )}
        <div className="logo-mark">S</div>
        <div>
          <div className="brand-name">SocraCode</div>
          <div className="brand-sub">Socratic Code Learning</div>
        </div>
      </div>

      {/* Right: about link + mode badge */}
      <div className="flex items-center gap-2">
        {mode === "home" && onAbout && (
          <button
            className="btn btn-ghost"
            style={{ padding: "5px 12px", height: "32px", fontSize: "12px" }}
            onClick={onAbout}
          >
            <InfoIcon />
            About
          </button>
        )}
        <span className={`mode-badge mode-${mode}`}>
          {mode !== "home" && mode !== "about" && <span className="dot" />}
          {mode}
        </span>
      </div>
    </header>
  );
}
