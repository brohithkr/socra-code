import { useEffect, useMemo, useRef, useState, type ChangeEvent, type MouseEvent as ReactMouseEvent } from "react";
import { Navigate, useLocation, useNavigate } from "react-router-dom";
import TopBar from "./components/TopBar";
import ModeCard from "./components/ModeCard";
import EditorPane from "./components/EditorPane";
import Terminal from "./components/Terminal";
import TutorChatPanel from "./components/TutorChatPanel";
import Scoreboard from "./components/Scoreboard";
import AboutPage from "./components/AboutPage";
import { createGame, fetchProblem, fetchProblems, fetchRoom, runCode, sendTutorChat } from "./lib/api";
import type { ChatMessage, HintResult, Language, RoomState, RunResult, WsMessage, ProblemDetail, ProblemSummary } from "./lib/types";
import { createRoomSocket } from "./lib/ws";

declare global {
  interface ImportMeta {
    env: {
      VITE_API_URL?: string;
    };
  }
}

const templates: Record<Language, string> = {
  python: "def sum_list(values):\n    total = 0\n    for i in range(len(values)): \n        total += values[i]\n    return total\n\nprint(sum_list([1, 2, 3]))\n",
  java: "public class Main {\n  public static int sumList(int[] values) {\n    int total = 0;\n    for (int i = 0; i <= values.length; i++) {\n      total += values[i];\n    }\n    return total;\n  }\n\n  public static void main(String[] args) {\n    int[] values = {1,2,3};\n    System.out.println(sumList(values));\n  }\n}\n",
  cpp: "#include <iostream>\n#include <vector>\nusing namespace std;\n\nint sumList(const vector<int>& values) {\n  int total = 0;\n  for (size_t i = 0; i <= values.size(); i++) {\n    total += values[i];\n  }\n  return total;\n}\n\nint main() {\n  vector<int> values = {1,2,3};\n  cout << sumList(values) << endl;\n  return 0;\n}\n",
};

function makeId() {
  if (typeof crypto !== "undefined" && "randomUUID" in crypto) {
    return crypto.randomUUID();
  }
  return Math.random().toString(36).slice(2, 10);
}

const PlayIcon = () => (
  <svg width="12" height="12" viewBox="0 0 12 12" fill="currentColor">
    <path d="M2.5 1.5L10 6L2.5 10.5V1.5Z" />
  </svg>
);

const SparkleIcon = () => (
  <svg width="13" height="13" viewBox="0 0 16 16" fill="currentColor">
    <path d="M8 0L9.5 6.5L16 8L9.5 9.5L8 16L6.5 9.5L0 8L6.5 6.5L8 0Z" />
  </svg>
);

export default function App() {
  const location = useLocation();
  const navigate = useNavigate();

  const mode: "home" | "practice" | "game" | "about" | null =
    location.pathname === "/"
      ? "home"
      : location.pathname === "/practice"
        ? "practice"
        : location.pathname === "/game"
          ? "game"
          : location.pathname === "/about"
            ? "about"
            : null;

  const [language, setLanguage] = useState<Language>("python");
  const [code, setCode] = useState<string>(templates.python);
  const [runResult, setRunResult] = useState<RunResult | null>(null);
  const [hint, setHint] = useState<HintResult | null>(null);
  const [history, setHistory] = useState<string[]>([]);
  const [chatMessages, setChatMessages] = useState<ChatMessage[]>([]);
  const [chatInput, setChatInput] = useState("");
  const [chatting, setChatting] = useState(false);
  const [running, setRunning] = useState(false);
  const [analyzing, setAnalyzing] = useState(false);

  const [problems, setProblems] = useState<ProblemSummary[]>([]);
  const [selectedProblemId, setSelectedProblemId] = useState<string>("");
  const [problemDetail, setProblemDetail] = useState<ProblemDetail | null>(null);
  const [sessionId, setSessionId] = useState<string>(() => makeId());
  const [terminalHeight, setTerminalHeight] = useState<number>(192);

  const handleTerminalResize = (event: ReactMouseEvent<HTMLDivElement>) => {
    event.preventDefault();
    const startY = event.clientY;
    const startHeight = terminalHeight;
    const onMove = (moveEvent: MouseEvent) => {
      const next = startHeight + (startY - moveEvent.clientY);
      setTerminalHeight(Math.max(80, Math.min(600, next)));
    };
    const onUp = () => {
      window.removeEventListener("mousemove", onMove);
      window.removeEventListener("mouseup", onUp);
      document.body.style.cursor = "";
      document.body.style.userSelect = "";
    };
    window.addEventListener("mousemove", onMove);
    window.addEventListener("mouseup", onUp);
    document.body.style.cursor = "row-resize";
    document.body.style.userSelect = "none";
  };

  const [roomState, setRoomState] = useState<RoomState | null>(null);
  const [roomId, setRoomId] = useState<string>("");
  const [playerName, setPlayerName] = useState<string>("Player One");
  const playerIdRef = useRef(makeId());
  const socketRef = useRef<ReturnType<typeof createRoomSocket> | null>(null);
  const [gameHint, setGameHint] = useState<HintResult | null>(null);
  const [gameRun, setGameRun] = useState<RunResult | null>(null);
  const [gameHistory, setGameHistory] = useState<string[]>([]);
  const [gameChatMessages, setGameChatMessages] = useState<ChatMessage[]>([]);
  const [gameChatInput, setGameChatInput] = useState("");
  const [gameChatting, setGameChatting] = useState(false);
  const [gameRunning, setGameRunning] = useState(false);
  const [gameAnalyzing, setGameAnalyzing] = useState(false);

  useEffect(() => {
    if (!selectedProblemId) {
      setCode(templates[language]);
    }
  }, [language, selectedProblemId]);

  useEffect(() => {
    fetchProblems(language, "buggy", 200)
      .then(setProblems)
      .catch(() => setProblems([]));
  }, [language]);

  useEffect(() => {
    if (!selectedProblemId) {
      setProblemDetail(null);
      return;
    }
    fetchProblem(selectedProblemId)
      .then((detail) => {
        setProblemDetail(detail);
        if (detail.language === "python" || detail.language === "java" || detail.language === "cpp") {
          setLanguage(detail.language);
        }
        setCode(detail.buggy_code || detail.starter_code || templates.python);
        setHistory([]);
        setHint(null);
        setChatMessages([]);
        setChatInput("");
        setSessionId(makeId());
      })
      .catch(() => setProblemDetail(null));
  }, [selectedProblemId]);

  const elapsed = useMemo(() => {
    if (!roomState) return 0;
    return Math.max(0, Math.floor(Date.now() / 1000 - roomState.started_at));
  }, [roomState]);

  const handleRun = async () => {
    setRunning(true);
    try {
      const result = await runCode(language, code);
      setRunResult(result);
    } catch (err) {
      setRunResult({ ok: false, stdout: "", stderr: err instanceof Error ? err.message : "Run failed", exit_code: 1, duration_ms: 0 });
    } finally {
      setRunning(false);
    }
  };

  const handleHint = async () => {
    if (analyzing || chatting) return;
    setAnalyzing(true);
    try {
      const output = runResult ? (runResult.stdout + runResult.stderr).trim() || undefined : undefined;
      // Route through /chat so that problem_id (and thus socratic mode) is honored.
      const result = await sendTutorChat(
        language,
        code,
        "",
        sessionId,
        selectedProblemId || undefined,
        output,
        history,
        chatMessages,
      );
      setHint(result);
      setHistory((prev) => [...prev, result.hint]);
      setChatMessages((prev) => [...prev, { role: "tutor", content: result.hint }]);
    } catch (err) {
      const message = err instanceof Error ? err.message : "Hint failed";
      setHint({ hint: message });
      setChatMessages((prev) => [...prev, { role: "tutor", content: message }]);
    } finally {
      setAnalyzing(false);
    }
  };

  const handleTutorChat = async () => {
    const userMessage = chatInput.trim();
    if (!userMessage || chatting || analyzing) return;
    const output = runResult ? (runResult.stdout + runResult.stderr).trim() || undefined : undefined;
    const nextMessages: ChatMessage[] = [...chatMessages, { role: "student", content: userMessage }];
    setChatMessages(nextMessages);
    setChatInput("");
    setChatting(true);
    try {
      const result = await sendTutorChat(
        language,
        code,
        userMessage,
        sessionId,
        selectedProblemId || undefined,
        output,
        history,
        chatMessages,
      );
      setHint(result);
      setHistory((prev) => [...prev, result.hint]);
      setChatMessages((prev) => [...prev, { role: "tutor", content: result.hint }]);
    } catch (err) {
      const message = err instanceof Error ? err.message : "Chat failed";
      setChatMessages((prev) => [...prev, { role: "tutor", content: message }]);
    } finally {
      setChatting(false);
    }
  };

  const connectRoom = (state: RoomState) => {
    setRoomState(state);
    setGameHint(null);
    setGameRun(null);
    setGameHistory([]);
    setGameChatMessages([]);
    setGameChatInput("");
    setGameChatting(false);
    setGameRunning(false);
    setGameAnalyzing(false);
    const baseUrl = import.meta.env.VITE_API_URL ?? "http://localhost:8000";
    const socket = createRoomSocket(baseUrl, state.room_id, playerIdRef.current, playerName);
    socketRef.current = socket;
    socket.onMessage((message: WsMessage) => {
      if (message.type === "room_state") setRoomState(message.payload.state as RoomState);
      if (message.type === "code_update") setRoomState((prev) => prev ? { ...prev, code: message.payload.code } : prev);
      if (message.type === "score_update") setRoomState((prev) => prev ? { ...prev, scores: message.payload.scores } : prev);
      if (message.type === "hint_result") {
        const payload = message.payload as HintResult;
        setGameHint(payload);
        setGameHistory((prev) => [...prev, payload.hint]);
        setGameChatMessages((prev) => [...prev, { role: "tutor", content: payload.hint }]);
        setGameAnalyzing(false);
      }
      if (message.type === "chat_response") {
        const payload = message.payload as HintResult;
        setGameHint(payload);
        setGameHistory((prev) => [...prev, payload.hint]);
        setGameChatMessages((prev) => [...prev, { role: "tutor", content: payload.hint }]);
        setGameChatting(false);
      }
      if (message.type === "run_result") {
        setGameRun(message.payload as RunResult);
        setGameRunning(false);
      }
      if (message.type === "error") {
        const payload = message.payload as { message?: string };
        if (payload.message && (gameChatting || gameAnalyzing)) {
          setGameChatMessages((prev) => [...prev, { role: "tutor", content: payload.message! }]);
        }
        setGameChatting(false);
        setGameAnalyzing(false);
        setGameRunning(false);
      }
    });
  };

  const handleCreateGame = async () => {
    const state = await createGame(language, code);
    setRoomId(state.room_id);
    connectRoom(state);
  };

  const handleJoinGame = async () => {
    const state = await fetchRoom(roomId);
    connectRoom(state);
  };

  const sendGameMessage = (message: WsMessage) => socketRef.current?.send(message);

  const updateGameCode = (value: string) => {
    setRoomState((prev) => prev ? { ...prev, code: value } : prev);
    sendGameMessage({ type: "code_update", payload: { code: value } });
  };

  const runGame = () => {
    if (!roomState || gameRunning) return;
    setGameRunning(true);
    sendGameMessage({ type: "run_request", payload: { code: roomState.code, language: roomState.language } });
  };

  const hintGame = () => {
    if (!roomState || gameAnalyzing || gameChatting) return;
    setGameAnalyzing(true);
    sendGameMessage({
      type: "hint_request",
      payload: {
        code: roomState.code,
        language: roomState.language,
        output: gameRun ? (gameRun.stdout + gameRun.stderr).trim() || undefined : undefined,
        history: gameHistory,
        chat_history: gameChatMessages,
      },
    });
  };

  const handleGameTutorChat = () => {
    if (!roomState) return;
    const userMessage = gameChatInput.trim();
    if (!userMessage || gameChatting || gameAnalyzing) return;
    setGameChatMessages((prev) => [...prev, { role: "student", content: userMessage }]);
    setGameChatInput("");
    setGameChatting(true);
    sendGameMessage({
      type: "chat_message",
      payload: {
        code: roomState.code,
        language: roomState.language,
        output: gameRun ? (gameRun.stdout + gameRun.stderr).trim() || undefined : undefined,
        history: gameHistory,
        user_message: userMessage,
        chat_history: gameChatMessages,
      },
    });
  };

  if (mode === null) return <Navigate to="/" replace />;

  return (
    <div className="app-shell">
      <TopBar
        mode={mode ?? "home"}
        onBack={mode === "home" || mode === null ? undefined : () => navigate("/")}
        onAbout={mode === "home" ? () => navigate("/about") : undefined}
        language={language}
        onLanguageChange={setLanguage}
        problems={problems}
        selectedProblemId={selectedProblemId}
        onProblemSelect={setSelectedProblemId}
        onRun={mode === "practice" ? handleRun : undefined}
        onAsk={mode === "practice" ? handleHint : undefined}
        onClear={
          mode === "practice"
            ? () => {
                setSelectedProblemId("");
                setProblemDetail(null);
                setHistory([]);
                setHint(null);
                setChatMessages([]);
                setChatInput("");
                setSessionId(makeId());
              }
            : undefined
        }
        running={running}
        analyzing={analyzing || chatting}
      />

      {/* ── Home ──────────────────────────────────────── */}
      {mode === "home" && (
        <div style={{ display: "grid", gridTemplateColumns: "1fr 360px", flex: 1, overflow: "hidden" }}>
          {/* Scrollable hero column */}
          <section className="hero-section" style={{ overflowY: "auto", padding: "0" }}>
            <div className="hero-grid-bg" />
            <div className="hero-glow" />

            {/* Hero content */}
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
                    desc: "Guided questions, never direct answers — learn to think like a debugger."
                  },
                  {
                    icon: <svg width="16" height="16" viewBox="0 0 12 12" fill="currentColor"><path d="M2.5 1.5L10 6L2.5 10.5V1.5Z" /></svg>,
                    color: "var(--mint)", colorSoft: "var(--mint-soft)",
                    title: "Real Code Execution",
                    desc: "Run Python, Java and C++ in a sandboxed environment with instant output."
                  },
                  {
                    icon: <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M2 20h.01M7 20v-4M12 20v-8M17 20v-12M22 4v16"/></svg>,
                    color: "var(--sky)", colorSoft: "var(--sky-soft)",
                    title: "Misconception Tracking",
                    desc: "Knowledge graph maps your recurring bugs, adapting hints to your gaps."
                  },
                  {
                    icon: <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round"><path d="M12 2l2.4 7.4H22l-6.2 4.5 2.4 7.4L12 17l-6.2 4.3 2.4-7.4L2 9.4h7.6z"/></svg>,
                    color: "var(--ember)", colorSoft: "var(--ember-soft)",
                    title: "Competitive Mode",
                    desc: "Real-time multiplayer debugging races — compete on speed and hint efficiency."
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

      {/* ── Practice ──────────────────────────────────── */}
      {mode === "practice" && (
        <div style={{ display: "flex", flex: 1, minHeight: 0, overflow: "hidden" }}>
          {/* Problem panel */}
          <div className="problem-panel" style={{ width: "280px", flexShrink: 0 }}>
            <div className="panel-header">
              <div className="panel-icon" style={{ background: "var(--sky-soft)", color: "var(--sky)" }}>
                <svg width="11" height="11" viewBox="0 0 16 16" fill="currentColor">
                  <path d="M8 1a7 7 0 100 14A7 7 0 008 1zm0 2a5 5 0 110 10A5 5 0 018 3zm0 3a1 1 0 00-1 1v3a1 1 0 002 0V7a1 1 0 00-1-1zm0-2a1 1 0 100 2 1 1 0 000-2z" />
                </svg>
              </div>
              <span className="panel-header-title">Problem</span>
            </div>
            <div className="problem-content">
              {selectedProblemId && problemDetail ? (
                <>
                  <p className="problem-statement">{problemDetail.statement}</p>
                  {problemDetail.bug_desc && (
                    <div className="bug-info-box">
                      <div className="bug-info-label">Bug hint</div>
                      <p className="bug-info-text">{problemDetail.bug_desc}</p>
                    </div>
                  )}
                </>
              ) : (
                <div style={{ paddingTop: "40px", textAlign: "center" }}>
                  <div style={{ fontSize: "28px", marginBottom: "12px", filter: "grayscale(0.3)" }}>📋</div>
                  <p style={{ fontSize: "12px", color: "var(--text-2)", lineHeight: "1.6" }}>
                    {selectedProblemId ? "Loading…" : "Select a problem from the top bar to get started."}
                  </p>
                </div>
              )}
            </div>
          </div>

          {/* Editor + Terminal */}
          <div style={{ flex: 1, minWidth: 0, display: "flex", flexDirection: "column", overflow: "hidden", borderLeft: "1px solid var(--border)", borderRight: "1px solid var(--border)" }}>
            {/* Problem info bar */}
            <div className="editor-info-bar">
              <div className="editor-info-left">
                {problemDetail ? (
                  <>
                    <span className="editor-problem-title">{problemDetail.title}</span>
                    {problemDetail.topic && (
                      <span className="editor-info-badge editor-badge-topic">{problemDetail.topic}</span>
                    )}
                    {problemDetail.kind && (
                      <span className="editor-info-badge editor-badge-kind">{problemDetail.kind}</span>
                    )}
                  </>
                ) : (
                  <span className="editor-info-placeholder">No problem selected — using template</span>
                )}
              </div>
              <div className="editor-info-right">
                <span className="editor-info-badge editor-badge-lang">{language}</span>
              </div>
            </div>
            <div style={{ flex: 1, minHeight: 0, overflow: "hidden", background: "#0a0a12" }}>
              <EditorPane language={language} code={code} onChange={setCode} height="100%" />
            </div>
            <div className="terminal-resize-handle" onMouseDown={handleTerminalResize} />
            <div style={{ height: `${terminalHeight}px`, flexShrink: 0 }}>
              <Terminal
                output={runResult?.stdout ?? ""}
                error={runResult?.stderr}
                exitCode={runResult?.exit_code}
                durationMs={runResult?.duration_ms}
              />
            </div>
          </div>

          {/* AI Tutor panel */}
          <div style={{ width: "340px", flexShrink: 0, display: "flex", flexDirection: "column", overflow: "hidden" }}>
            <div className="panel-header">
              <div className="ai-badge">
                <span style={{ fontSize: "12px" }}>✦</span>
              </div>
              <div>
                <div style={{ fontSize: "13px", fontWeight: 600, color: "var(--text)" }}>AI Tutor</div>
                <div style={{ fontSize: "10px", color: "var(--text-3)", letterSpacing: "0.06em" }}>
                  {(hint as any)?.score ? `Score: ${(hint as any).score}` : "Socratic Mode"}
                </div>
              </div>
            </div>
            <div style={{ flex: 1, minHeight: 0, overflow: "hidden" }}>
              <TutorChatPanel
                messages={chatMessages}
                input={chatInput}
                busy={chatting || analyzing}
                onInputChange={setChatInput}
                onSubmit={handleTutorChat}
              />
            </div>
          </div>
        </div>
      )}

      {/* ── About ─────────────────────────────────────── */}
      {mode === "about" && <AboutPage onBack={() => navigate("/")} />}

      {/* ── Game ──────────────────────────────────────── */}
      {mode === "game" && (
        <div style={{ flex: 1, overflow: "auto", display: "flex", flexDirection: "column" }}>
          {!roomState && (
            <div style={{
              flex: 1,
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              padding: "40px 24px",
            }}>
              <div style={{ width: "100%", maxWidth: "800px", display: "grid", gridTemplateColumns: "1fr 1fr", gap: "20px" }}>
                {/* Create game */}
                <div className="lobby-card">
                  <div style={{ display: "flex", alignItems: "center", gap: "8px", marginBottom: "6px" }}>
                    <span style={{ fontSize: "18px" }}>🎮</span>
                    <h3 style={{ fontFamily: "'Bricolage Grotesque', ui-sans-serif", fontWeight: 600, fontSize: "18px", letterSpacing: "-0.02em", color: "var(--text)" }}>
                      Create a Room
                    </h3>
                  </div>
                  <p style={{ fontSize: "12px", color: "var(--text-2)", marginBottom: "22px", lineHeight: "1.6" }}>
                    Start a new game room and invite others to join using the room ID.
                  </p>
                  <div style={{ marginBottom: "14px" }}>
                    <label className="section-label" style={{ display: "block", marginBottom: "6px" }}>Language</label>
                    <select
                      className="ui-select"
                      style={{ width: "100%", padding: "9px 32px 9px 12px", height: "38px" }}
                      value={language}
                      onChange={(e: ChangeEvent<HTMLSelectElement>) => setLanguage(e.target.value as Language)}
                    >
                      <option value="python">Python</option>
                      <option value="java">Java</option>
                      <option value="cpp">C++</option>
                    </select>
                  </div>
                  <button
                    className="btn btn-primary"
                    style={{ width: "100%", padding: "10px 16px", justifyContent: "center" }}
                    onClick={handleCreateGame}
                  >
                    Create Game
                  </button>
                  <p style={{ fontSize: "11px", color: "var(--text-3)", marginTop: "10px" }}>
                    Seed code uses the current editor snippet.
                  </p>
                </div>

                {/* Join game */}
                <div className="lobby-card">
                  <div style={{ display: "flex", alignItems: "center", gap: "8px", marginBottom: "6px" }}>
                    <span style={{ fontSize: "18px" }}>🔗</span>
                    <h3 style={{ fontFamily: "'Bricolage Grotesque', ui-sans-serif", fontWeight: 600, fontSize: "18px", letterSpacing: "-0.02em", color: "var(--text)" }}>
                      Join a Room
                    </h3>
                  </div>
                  <p style={{ fontSize: "12px", color: "var(--text-2)", marginBottom: "22px", lineHeight: "1.6" }}>
                    Enter a room ID shared by your opponent to join their session.
                  </p>
                  <div style={{ marginBottom: "14px" }}>
                    <label className="section-label" style={{ display: "block", marginBottom: "6px" }}>Room ID</label>
                    <input
                      className="ui-input"
                      style={{ width: "100%", padding: "9px 12px", height: "38px" }}
                      placeholder="Paste room ID…"
                      value={roomId}
                      onChange={(e: ChangeEvent<HTMLInputElement>) => setRoomId(e.target.value)}
                    />
                  </div>
                  <div style={{ marginBottom: "14px" }}>
                    <label className="section-label" style={{ display: "block", marginBottom: "6px" }}>Your Name</label>
                    <input
                      className="ui-input"
                      style={{ width: "100%", padding: "9px 12px", height: "38px" }}
                      value={playerName}
                      onChange={(e: ChangeEvent<HTMLInputElement>) => setPlayerName(e.target.value)}
                      placeholder="Display name…"
                    />
                  </div>
                  <button
                    className="btn btn-ghost"
                    style={{ width: "100%", padding: "10px 16px", justifyContent: "center", border: "1px solid var(--border-2)" }}
                    onClick={handleJoinGame}
                    disabled={!roomId.trim()}
                  >
                    Join Room
                  </button>
                </div>
              </div>
            </div>
          )}

          {roomState && (
            <div style={{ flex: 1, display: "grid", gridTemplateColumns: "1fr 320px", minHeight: 0 }}>
              {/* Editor column */}
              <div style={{ display: "flex", flexDirection: "column", overflow: "hidden", borderRight: "1px solid var(--border)" }}>
                {/* Room strip */}
                <div className="room-strip">
                  <span className="room-id-badge">{roomState.room_id}</span>
                  <span className="elapsed-badge">⏱ {elapsed}s</span>
                  <div style={{ flex: 1 }} />
                  <button
                    className="btn btn-run"
                    style={{ padding: "6px 14px" }}
                    onClick={runGame}
                    disabled={gameRunning}
                  >
                    <svg width="11" height="11" viewBox="0 0 12 12" fill="currentColor"><path d="M2.5 1.5L10 6L2.5 10.5V1.5Z" /></svg>
                    {gameRunning ? "Running…" : "Run"}
                  </button>
                  <button
                    className="btn btn-hint"
                    style={{ padding: "6px 14px" }}
                    onClick={hintGame}
                    disabled={gameAnalyzing || gameChatting}
                  >
                    <svg width="13" height="13" viewBox="0 0 16 16" fill="currentColor"><path d="M8 0L9.5 6.5L16 8L9.5 9.5L8 16L6.5 9.5L0 8L6.5 6.5L8 0Z" /></svg>
                    {gameAnalyzing ? "Asking…" : "Hint"}
                  </button>
                </div>

                {/* Editor */}
                <div style={{ flex: 1, minHeight: 0, background: "#0a0a12" }}>
                  <EditorPane
                    language={roomState.language}
                    code={roomState.code}
                    onChange={updateGameCode}
                    height="100%"
                  />
                </div>

                {/* Terminal */}
                <div className="terminal-resize-handle" onMouseDown={handleTerminalResize} />
                <div style={{ height: `${terminalHeight}px`, flexShrink: 0 }}>
                  <Terminal
                    output={gameRun?.stdout ?? ""}
                    error={gameRun?.stderr}
                    exitCode={gameRun?.exit_code}
                    durationMs={gameRun?.duration_ms}
                  />
                </div>
              </div>

              {/* Right sidebar: scoreboard + tutor */}
              <div style={{ display: "flex", flexDirection: "column", overflow: "hidden" }}>
                <Scoreboard
                  players={roomState.players}
                  scores={roomState.scores}
                  hints={roomState.hints_used}
                />
                <div style={{ flex: 1, minHeight: 0, display: "flex", flexDirection: "column", overflow: "hidden", borderTop: "1px solid var(--border)" }}>
                  <div className="panel-header">
                    <div className="ai-badge">
                      <span style={{ fontSize: "12px" }}>✦</span>
                    </div>
                    <div>
                      <div style={{ fontSize: "13px", fontWeight: 600, color: "var(--text)" }}>AI Tutor</div>
                      <div style={{ fontSize: "10px", color: "var(--text-3)", letterSpacing: "0.06em" }}>
                        {(gameHint as any)?.score ? `Score: ${(gameHint as any).score}` : "Room Tutor"}
                      </div>
                    </div>
                  </div>
                  <div style={{ flex: 1, minHeight: 0, overflow: "hidden" }}>
                    <TutorChatPanel
                      messages={gameChatMessages}
                      input={gameChatInput}
                      busy={gameChatting || gameAnalyzing}
                      onInputChange={setGameChatInput}
                      onSubmit={handleGameTutorChat}
                    />
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
