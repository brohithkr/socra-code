import { useLocation, useNavigate, Navigate } from "react-router-dom";
import TopBar from "./components/TopBar";
import ModeCard from "./components/ModeCard";
import PracticeMode from "./components/PracticeMode";
import GameMode from "./components/GameMode";
import AboutPage from "./components/AboutPage";

export default function App() {
  const location = useLocation();
  const navigate = useNavigate();

  const { pathname } = location;
  const isGameRoom = pathname.startsWith("/game/room/");

  const mode: "home" | "practice" | "game" | "about" | null =
    pathname === "/"
      ? "home"
      : pathname === "/practice"
        ? "practice"
        : (pathname === "/game" || isGameRoom)
          ? "game"
          : pathname === "/about"
            ? "about"
            : null;

  if (mode === null) return <Navigate to="/" replace />;

  const handleBack = mode === "home"
    ? undefined
    : () => { if (isGameRoom) navigate("/game"); else navigate("/"); };

  return (
    <div className="app-shell">
      <TopBar
        mode={mode}
        onBack={handleBack}
        onAbout={mode === "home" ? () => navigate("/about") : undefined}
      />

      {/* ── Home ──────────────────────────────────────────── */}
      {mode === "home" && (
        <div style={{ display: "grid", gridTemplateColumns: "1fr 360px", flex: 1, overflow: "hidden" }}>
          {/* Scrollable hero column */}
          <section className="hero-section" style={{ overflowY: "auto", padding: "0" }}>
            <div className="hero-grid-bg" />
            <div className="hero-glow" />

            <div style={{ position: "relative", zIndex: 1, padding: "56px 56px 48px" }}>
              <div className="accent-chip animate-fade-up">
                <span className="chip-dot" />
                Team 5 · Final Year Major Project · CSE-A · KMIT · 2026
              </div>
              <h1 className="hero-headline animate-fade-up-1" style={{ marginTop: "24px" }}>
                SocraCode
              </h1>
              <p className="animate-fade-up-1" style={{ marginTop: "10px", fontSize: "15px", fontWeight: 500, color: "var(--text-2)", letterSpacing: "-0.01em", maxWidth: "500px" }}>
                Graph-based agentic misconception planning for multi-turn Socratic code learning
              </p>
              <p className="hero-sub animate-fade-up-2" style={{ marginTop: "16px" }}>
                Run code, inspect failures, and get guided Socratic hints from an AI tutor — without being handed the solution. Learn to debug, not just fix.
              </p>
              <div className="animate-fade-up-3" style={{ display: "flex", gap: "12px", marginTop: "32px", flexWrap: "wrap" }}>
                <button className="cta-primary" onClick={() => navigate("/practice")}>
                  Open Practice Studio
                  <svg width="14" height="14" viewBox="0 0 16 16" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                    <path d="M3 8H13M9 4L13 8L9 12" />
                  </svg>
                </button>
                <button className="cta-secondary" onClick={() => navigate("/game")}>
                  Multiplayer Room
                </button>
              </div>
            </div>

            {/* Feature highlights */}
            <div style={{ position: "relative", zIndex: 1, padding: "0 56px 48px", borderTop: "1px solid var(--border)" }}>
              <div className="home-section-label" style={{ paddingTop: "40px" }}>Features</div>
              <div className="features-grid">
                {[
                  {
                    icon: <svg width="16" height="16" viewBox="0 0 16 16" fill="currentColor"><path d="M8 0L9.5 6.5L16 8L9.5 9.5L8 16L6.5 9.5L0 8L6.5 6.5L8 0Z" /></svg>,
                    color: "var(--violet-2)", colorSoft: "var(--violet-soft)",
                    title: "Socratic AI Tutor",
                    desc: "Guided questions, never direct answers — learn to think like a debugger.",
                  },
                  {
                    icon: <svg width="16" height="16" viewBox="0 0 12 12" fill="currentColor"><path d="M2.5 1.5L10 6L2.5 10.5V1.5Z" /></svg>,
                    color: "var(--mint)", colorSoft: "var(--mint-soft)",
                    title: "Real Code Execution",
                    desc: "Run Python, Java and C++ in a sandboxed environment with instant output.",
                  },
                  {
                    icon: <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M2 20h.01M7 20v-4M12 20v-8M17 20v-12M22 4v16" /></svg>,
                    color: "var(--sky)", colorSoft: "var(--sky-soft)",
                    title: "Misconception Tracking",
                    desc: "Knowledge graph maps your recurring bugs, adapting hints to your gaps.",
                  },
                  {
                    icon: <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round"><path d="M12 2l2.4 7.4H22l-6.2 4.5 2.4 7.4L12 17l-6.2 4.3 2.4-7.4L2 9.4h7.6z" /></svg>,
                    color: "var(--ember)", colorSoft: "var(--ember-soft)",
                    title: "Competitive Mode",
                    desc: "Real-time multiplayer debugging races — compete on speed and hint efficiency.",
                  },
                ].map((f) => (
                  <div key={f.title} className="feature-card">
                    <div className="feature-card-header">
                      <div className="feature-card-icon" style={{ background: f.colorSoft, color: f.color }}>{f.icon}</div>
                      <div className="feature-card-title">{f.title}</div>
                    </div>
                    <div className="feature-card-desc">{f.desc}</div>
                  </div>
                ))}
              </div>
            </div>

            {/* Why Socratic learning */}
            <div style={{ position: "relative", zIndex: 1, padding: "0 56px 48px", borderTop: "1px solid var(--border)" }}>
              <div className="home-section-label" style={{ paddingTop: "40px" }}>Why Socratic Learning?</div>
              <p style={{ fontSize: "13px", color: "var(--text-2)", lineHeight: "1.7", marginTop: "10px", maxWidth: "480px" }}>
                The Socratic method is proven to build deeper, lasting understanding. Instead of copying an answer, you reason your way to it — with guidance at each step.
              </p>
              <div className="benefits-list">
                {[
                  { label: "Deeper retention", desc: "Understanding a bug beats memorising its fix." },
                  { label: "Active reasoning", desc: "You find the bug — AI only asks the right questions." },
                  { label: "Metacognition", desc: "Learn how to debug, not just this one program." },
                ].map((b) => (
                  <div key={b.label} className="benefit-row">
                    <span className="benefit-dot" />
                    <div>
                      <span className="benefit-label">{b.label}</span>
                      <span className="benefit-desc"> — {b.desc}</span>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Footer credit strip */}
            <div className="home-footer-strip" style={{ borderTop: "1px solid var(--border)" }}>
              <span>Built by the SocraCode team at KMIT</span>
              <button className="home-footer-link" onClick={() => navigate("/about")}>
                Meet the team
                <svg width="11" height="11" viewBox="0 0 16 16" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                  <path d="M3 8H13M9 4L13 8L9 12" />
                </svg>
              </button>
            </div>
          </section>

          {/* Mode cards column */}
          <div style={{ display: "flex", flexDirection: "column", borderLeft: "1px solid var(--border)", overflow: "hidden" }}>
            <ModeCard
              num="01"
              variant="practice"
              title="Practice Mode"
              description="Work solo with a Socratic AI tutor. Run code, inspect errors, and learn through guided questions — not copy-paste answers."
              action="Enter practice"
              onClick={() => navigate("/practice")}
            />
            <div style={{ height: "1px", background: "var(--border)", flexShrink: 0 }} />
            <ModeCard
              num="02"
              variant="game"
              title="Game Mode"
              description="Create or join a room, sync code in real-time with teammates, and compete on speed vs. hint usage."
              action="Enter game"
              onClick={() => navigate("/game")}
            />
          </div>
        </div>
      )}

      {/* ── Practice ──────────────────────────────────────── */}
      {mode === "practice" && <PracticeMode />}

      {/* ── Game ──────────────────────────────────────────── */}
      {mode === "game" && <GameMode />}

      {/* ── About ─────────────────────────────────────────── */}
      {mode === "about" && <AboutPage onBack={() => navigate("/")} />}
    </div>
  );
}
