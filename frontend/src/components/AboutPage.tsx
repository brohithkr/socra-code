interface AboutPageProps {
  onBack: () => void;
}

const team = [
  { name: "H S Vishal", roll: "22BD1A050H", color: "var(--violet-2)" },
  { name: "B Rohith Kumar", roll: "22BD1A0505", color: "var(--sky)" },
  { name: "Jai A Parmar", roll: "22BD1A0517", color: "var(--mint)" },
  { name: "Harsha Kota", roll: "23BD5A0502", color: "var(--ember)" },
];

const archSections = [
  {
    icon: (
      <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.7" strokeLinecap="round" strokeLinejoin="round">
        <rect x="2" y="3" width="20" height="14" rx="2" />
        <path d="M8 21h8M12 17v4" />
      </svg>
    ),
    title: "Frontend",
    color: "var(--sky)",
    colorSoft: "var(--sky-soft)",
    points: ["React + Vite for fast development", "Monaco Editor for full IDE experience", "Python, Java, C++ language support", "WebSocket client for real-time sync"],
  },
  {
    icon: (
      <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.7" strokeLinecap="round" strokeLinejoin="round">
        <path d="M18 20V10M12 20V4M6 20v-6" />
      </svg>
    ),
    title: "Backend API",
    color: "var(--mint)",
    colorSoft: "var(--mint-soft)",
    points: ["FastAPI (Python) REST server", "Sandboxed code execution engine", "Problem store with bug variants", "Hint generation orchestration"],
  },
  {
    icon: (
      <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.7" strokeLinecap="round" strokeLinejoin="round">
        <path d="M12 2L2 7l10 5 10-5-10-5z" />
        <path d="M2 17l10 5 10-5M2 12l10 5 10-5" />
      </svg>
    ),
    title: "AI Engine",
    color: "var(--violet-2)",
    colorSoft: "var(--violet-soft)",
    points: ["Graph-based misconception planner", "Multi-turn Socratic conversation", "Knowledge gap tracking per student", "Claude / OpenAI LLM integration"],
  },
  {
    icon: (
      <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.7" strokeLinecap="round" strokeLinejoin="round">
        <path d="M22 12h-4l-3 9L9 3l-3 9H2" />
      </svg>
    ),
    title: "Real-time Layer",
    color: "var(--ember)",
    colorSoft: "var(--ember-soft)",
    points: ["WebSocket rooms for multiplayer", "Live code sync between players", "Score + hint broadcast events", "Room lifecycle management"],
  },
];

export default function AboutPage({ onBack }: AboutPageProps) {
  return (
    <div className="about-page">
      {/* ── Hero ─────────────────────────────────────── */}
      <section className="about-hero animate-fade-up">
        <div className="about-hero-badge">
          Team 5 · Final Year Major Project · CSE-A · KMIT · 2026
        </div>
        <h1 className="about-hero-title">SocraCode</h1>
        <p className="about-hero-sub">
          Graph-based agentic misconception planning for multi-turn Socratic code learning
        </p>
        <p className="about-hero-inst">
          Keshav Memorial Institute of Technology &nbsp;·&nbsp; Department of Computer Science &amp; Engineering
        </p>
      </section>

      {/* ── Project overview ─────────────────────────── */}
      <section className="about-section animate-fade-up-1">
        <h2 className="about-section-title">About the Project</h2>
        <p className="about-body">
          SocraCode is an AI-powered debugging learning platform grounded in the Socratic method — an ancient pedagogical technique that teaches through guided questioning rather than direct instruction. Instead of handing students the answer when they're stuck, SocraCode's AI tutor asks probing questions that lead learners to discover bugs and misconceptions on their own.
        </p>
        <p className="about-body" style={{ marginTop: "14px" }}>
          Under the hood, the system maintains a <strong>knowledge graph</strong> per student that tracks misconceptions across multi-turn conversations. This graph informs the AI's questioning strategy: if a student consistently misunderstands off-by-one errors, the tutor adapts its hints to target that specific gap without breaking the Socratic flow. The result is deeper, longer-lasting learning than traditional "give-the-answer" code assistants.
        </p>
        <p className="about-body" style={{ marginTop: "14px" }}>
          A <strong>competitive multiplayer mode</strong> lets students race each other to fix the same buggy program, with scoring weighted by speed and hints used — making debugging practice engaging and community-driven.
        </p>
      </section>

      {/* ── Features grid ────────────────────────────── */}
      <section className="about-section animate-fade-up-2">
        <h2 className="about-section-title">Key Features</h2>
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
              icon: <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M2 20h.01M7 20v-4M12 20v-8M17 20v-12M22 4v16"/></svg>,
              color: "var(--sky)", colorSoft: "var(--sky-soft)",
              title: "Misconception Tracking",
              desc: "Knowledge graph maps your recurring bugs, adapting hints to your gaps.",
            },
            {
              icon: <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round"><path d="M12 2l2.4 7.4H22l-6.2 4.5 2.4 7.4L12 17l-6.2 4.3 2.4-7.4L2 9.4h7.6z"/></svg>,
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
      </section>

      {/* ── Architecture ─────────────────────────────── */}
      <section className="about-section animate-fade-up-2">
        <h2 className="about-section-title">Architecture</h2>
        <div className="arch-grid">
          {archSections.map((a) => (
            <div
              key={a.title}
              className="arch-card"
              style={{ borderTop: `2px solid ${a.color}` }}
            >
              <div className="arch-card-header">
                <div
                  className="arch-card-icon"
                  style={{ background: a.colorSoft, color: a.color }}
                >
                  {a.icon}
                </div>
                <div className="arch-card-title" style={{ color: a.color }}>{a.title}</div>
              </div>
              <ul className="arch-card-points">
                {a.points.map((pt) => (
                  <li key={pt}>{pt}</li>
                ))}
              </ul>
            </div>
          ))}
        </div>
      </section>

      {/* ── Team ─────────────────────────────────────── */}
      <section className="about-section animate-fade-up-3">
        <h2 className="about-section-title">The Team <span style={{ fontSize: "14px", fontWeight: 500, color: "var(--text-3)", letterSpacing: "0.04em" }}>— Group 5</span></h2>
        <div className="team-grid">
          {team.map((member) => (
            <div key={member.roll} className="team-card">
              <div
                className="team-avatar"
                style={{
                  background: `linear-gradient(135deg, ${member.color}22, ${member.color}44)`,
                  border: `1px solid ${member.color}44`,
                  color: member.color,
                }}
              >
                {member.name.charAt(0)}
              </div>
              <div className="team-name">{member.name}</div>
              <div className="team-roll">{member.roll}</div>
              <div className="team-role">Student Developer</div>
            </div>
          ))}
        </div>
      </section>

      {/* ── Mentor ───────────────────────────────────── */}
      <section className="about-section animate-fade-up-4">
        <h2 className="about-section-title">Project Mentor</h2>
        <div className="mentor-card">
          <div className="mentor-avatar">PS</div>
          <div>
            <div className="mentor-name">Priyanka Saxena</div>
            <div className="mentor-title">Head of Department, Computer Science Engineering</div>
            <div className="mentor-inst">Keshav Memorial Institute of Technology</div>
          </div>
        </div>
      </section>

      {/* ── Back CTA ─────────────────────────────────── */}
      <div style={{ padding: "0 0 60px", textAlign: "center" }}>
        <button className="cta-primary" onClick={onBack}>
          <svg width="14" height="14" viewBox="0 0 16 16" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <path d="M10 3L5 8L10 13" />
          </svg>
          Back to Home
        </button>
      </div>
    </div>
  );
}
