import { useEffect, useRef, useState, type ChangeEvent, type MouseEvent as ReactMouseEvent } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import EditorPane from "./EditorPane";
import Terminal from "./Terminal";
import TutorChatPanel from "./TutorChatPanel";
import Scoreboard from "./Scoreboard";
import { createGame, fetchProblem, fetchProblems, fetchRoom } from "../lib/api";
import type { ChatMessage, HintResult, Language, ProblemDetail, ProblemSummary, RoomState, RunResult, WsMessage } from "../lib/types";
import { createRoomSocket } from "../lib/ws";

declare global {
  interface ImportMeta {
    env: { VITE_API_URL?: string };
  }
}

const templates: Record<Language, string> = {
  python: "def sum_list(values):\n    total = 0\n    for i in range(len(values)): \n        total += values[i]\n    return total\n\nprint(sum_list([1, 2, 3]))\n",
  java: "public class Main {\n  public static int sumList(int[] values) {\n    int total = 0;\n    for (int i = 0; i <= values.length; i++) {\n      total += values[i];\n    }\n    return total;\n  }\n\n  public static void main(String[] args) {\n    int[] values = {1,2,3};\n    System.out.println(sumList(values));\n  }\n}\n",
  cpp: "#include <iostream>\n#include <vector>\nusing namespace std;\n\nint sumList(const vector<int>& values) {\n  int total = 0;\n  for (size_t i = 0; i <= values.size(); i++) {\n    total += values[i];\n  }\n  return total;\n}\n\nint main() {\n  vector<int> values = {1,2,3};\n  cout << sumList(values) << endl;\n  return 0;\n}\n",
};

function makeId() {
  if (typeof crypto !== "undefined" && "randomUUID" in crypto) return crypto.randomUUID();
  return Math.random().toString(36).slice(2, 10);
}

const PlayIcon = () => (
  <svg width="11" height="11" viewBox="0 0 12 12" fill="currentColor"><path d="M2.5 1.5L10 6L2.5 10.5V1.5Z" /></svg>
);
const SparkleIcon = () => (
  <svg width="12" height="12" viewBox="0 0 16 16" fill="currentColor"><path d="M8 0L9.5 6.5L16 8L9.5 9.5L8 16L6.5 9.5L0 8L6.5 6.5L8 0Z" /></svg>
);

export default function GameMode() {
  const navigate = useNavigate();
  const location = useLocation();

  // Extract room ID from URL: /game/room/<id>
  const urlRoomId = location.pathname.startsWith("/game/room/")
    ? location.pathname.slice("/game/room/".length).split("/")[0]
    : "";

  const [language, setLanguage] = useState<Language>("python");
  const [playerName, setPlayerName] = useState("Player One");
  const [roomIdInput, setRoomIdInput] = useState(urlRoomId);
  const [lobbyCode, setLobbyCode] = useState(templates.python);

  const [problems, setProblems] = useState<ProblemSummary[]>([]);
  const [problemsLoading, setProblemsLoading] = useState(true);
  const [selectedProblemId, setSelectedProblemId] = useState("");
  const [problemDetail, setProblemDetail] = useState<ProblemDetail | null>(null);

  const [roomState, setRoomState] = useState<RoomState | null>(null);
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
  const [terminalHeight, setTerminalHeight] = useState(192);
  const [elapsed, setElapsed] = useState(0);
  const [joinError, setJoinError] = useState("");

  // Load problems when language changes
  useEffect(() => {
    setProblemsLoading(true);
    fetchProblems(language, "buggy", 200)
      .then(setProblems)
      .catch(() => setProblems([]))
      .finally(() => setProblemsLoading(false));
  }, [language]);

  useEffect(() => {
    if (!selectedProblemId) setLobbyCode(templates[language]);
  }, [language, selectedProblemId]);

  useEffect(() => {
    if (!selectedProblemId) { setProblemDetail(null); return; }
    fetchProblem(selectedProblemId)
      .then((detail) => {
        setProblemDetail(detail);
        if (detail.language === "python" || detail.language === "java" || detail.language === "cpp") {
          setLanguage(detail.language);
        }
        setLobbyCode(detail.buggy_code || detail.starter_code || templates.python);
      })
      .catch(() => setProblemDetail(null));
  }, [selectedProblemId]);

  // Elapsed timer
  useEffect(() => {
    if (!roomState) { setElapsed(0); return; }
    const tick = () => setElapsed(Math.max(0, Math.floor(Date.now() / 1000 - roomState.started_at)));
    tick();
    const id = setInterval(tick, 1000);
    return () => clearInterval(id);
  }, [roomState?.started_at]);

  // Reset room state when URL no longer has a room ID (e.g. Back pressed)
  useEffect(() => {
    if (!urlRoomId && roomState) {
      (socketRef.current as any)?.close?.();
      socketRef.current = null;
      setRoomState(null);
    }
  }, [urlRoomId]);

  // Cleanup socket on unmount
  useEffect(() => {
    return () => { (socketRef.current as any)?.close?.(); };
  }, []);

  const handleTerminalResize = (event: ReactMouseEvent<HTMLDivElement>) => {
    event.preventDefault();
    const startY = event.clientY;
    const startHeight = terminalHeight;
    const onMove = (e: MouseEvent) => {
      setTerminalHeight(Math.max(80, Math.min(600, startHeight + (startY - e.clientY))));
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
    setJoinError("");
    navigate(`/game/room/${state.room_id}`, { replace: true });
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
        if (payload.message) {
          setGameChatMessages((prev) => [...prev, { role: "tutor", content: payload.message! }]);
        }
        setGameChatting(false);
        setGameAnalyzing(false);
        setGameRunning(false);
      }
    });
  };

  const handleCreateGame = async () => {
    try {
      const state = await createGame(language, lobbyCode);
      connectRoom(state);
    } catch (err) {
      setJoinError(err instanceof Error ? err.message : "Failed to create room");
    }
  };

  const handleJoinGame = async () => {
    const id = roomIdInput.trim();
    if (!id) return;
    try {
      const state = await fetchRoom(id);
      connectRoom(state);
    } catch (err) {
      setJoinError(err instanceof Error ? err.message : "Room not found");
    }
  };

  const handleDirectJoin = async () => {
    if (!urlRoomId) return;
    setJoinError("");
    try {
      const state = await fetchRoom(urlRoomId);
      connectRoom(state);
    } catch {
      setJoinError("Room not found or has expired.");
    }
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

  const gameBusy = gameChatting || gameAnalyzing;

  /* ── Direct URL access: /game/room/<id> without roomState ── */
  if (!roomState && urlRoomId) {
    return (
      <div style={{ flex: 1, display: "flex", alignItems: "center", justifyContent: "center", padding: "40px 24px" }}>
        <div className="lobby-card" style={{ width: "100%", maxWidth: "420px" }}>
          <div style={{ display: "flex", alignItems: "center", gap: "8px", marginBottom: "6px" }}>
            <span style={{ fontSize: "18px" }}>🔗</span>
            <h3 style={{ fontFamily: "'Bricolage Grotesque', ui-sans-serif", fontWeight: 600, fontSize: "18px", letterSpacing: "-0.02em", color: "var(--text)" }}>
              Join Room
            </h3>
          </div>
          <p style={{ fontSize: "12px", color: "var(--text-2)", marginBottom: "22px", lineHeight: "1.6" }}>
            You were invited to join room{" "}
            <code style={{ fontFamily: "'JetBrains Mono', ui-monospace", fontSize: "11px", background: "var(--surface-3)", padding: "2px 6px", borderRadius: "4px", color: "var(--sky)" }}>
              {urlRoomId}
            </code>
          </p>
          <div style={{ marginBottom: "14px" }}>
            <label className="section-label" style={{ display: "block", marginBottom: "6px" }}>Your Name</label>
            <input
              className="ui-input"
              style={{ width: "100%", padding: "9px 12px", height: "38px", boxSizing: "border-box" }}
              value={playerName}
              onChange={(e: ChangeEvent<HTMLInputElement>) => setPlayerName(e.target.value)}
              placeholder="Display name…"
              onKeyDown={(e) => e.key === "Enter" && handleDirectJoin()}
              autoFocus
            />
          </div>
          {joinError && (
            <p style={{ fontSize: "12px", color: "var(--rose)", marginBottom: "12px" }}>{joinError}</p>
          )}
          <button
            className="btn btn-primary"
            style={{ width: "100%", padding: "10px 16px", justifyContent: "center", marginBottom: "10px" }}
            onClick={handleDirectJoin}
          >
            Connect to Room
          </button>
          <button
            className="btn btn-ghost"
            style={{ width: "100%", padding: "10px 16px", justifyContent: "center" }}
            onClick={() => navigate("/game")}
          >
            Back to Lobby
          </button>
        </div>
      </div>
    );
  }

  /* ── Lobby ───────────────────────────────────────────────── */
  if (!roomState) {
    return (
      <div style={{ flex: 1, overflow: "auto", display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center", padding: "40px 24px" }}>
        <div style={{ width: "100%", maxWidth: "860px", display: "flex", flexDirection: "column", gap: "20px" }}>

          {/* Problem selector row */}
          <div style={{ display: "flex", gap: "12px", alignItems: "center", padding: "14px 18px", background: "var(--surface)", border: "1px solid var(--border-2)", borderRadius: "var(--r-xl)" }}>
            <div style={{ fontSize: "10px", fontWeight: 600, letterSpacing: "0.12em", textTransform: "uppercase" as const, color: "var(--text-3)", flexShrink: 0 }}>
              Problem
            </div>
            <select
              className="ui-select"
              style={{ padding: "7px 32px 7px 12px", height: "36px", flexShrink: 0 }}
              value={language}
              onChange={(e: ChangeEvent<HTMLSelectElement>) => setLanguage(e.target.value as Language)}
            >
              <option value="python">Python</option>
              <option value="java">Java</option>
              <option value="cpp">C++</option>
            </select>
            <select
              className="ui-select"
              style={{ flex: 1, padding: "7px 32px 7px 12px", height: "36px", minWidth: 0 }}
              value={selectedProblemId}
              onChange={(e: ChangeEvent<HTMLSelectElement>) => setSelectedProblemId(e.target.value)}
              disabled={problemsLoading}
            >
              <option value="">
                {problemsLoading ? "Loading problems…" : problems.length === 0 ? "No problems available" : "No problem — use template"}
              </option>
              {problems.map((p) => (
                <option key={p.id} value={p.id}>{p.title}</option>
              ))}
            </select>
            {problemDetail && (
              <div style={{ display: "flex", gap: "6px", flexShrink: 0 }}>
                {problemDetail.topic && <span className="editor-info-badge editor-badge-topic">{problemDetail.topic}</span>}
                {problemDetail.kind && <span className="editor-info-badge editor-badge-kind">{problemDetail.kind}</span>}
              </div>
            )}
            {!problemsLoading && problems.length > 0 && !selectedProblemId && (
              <span style={{ fontSize: "11px", color: "var(--text-3)", flexShrink: 0 }}>
                {problems.length} available
              </span>
            )}
          </div>

          {joinError && (
            <div style={{ padding: "12px 16px", background: "var(--rose-soft)", border: "1px solid rgba(244,63,94,0.25)", borderRadius: "var(--r-md)", fontSize: "13px", color: "var(--rose)" }}>
              {joinError}
            </div>
          )}

          {/* Create / Join cards */}
          <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "20px" }}>
            {/* Create */}
            <div className="lobby-card">
              <div style={{ display: "flex", alignItems: "center", gap: "8px", marginBottom: "6px" }}>
                <span style={{ fontSize: "18px" }}>🎮</span>
                <h3 style={{ fontFamily: "'Bricolage Grotesque', ui-sans-serif", fontWeight: 600, fontSize: "18px", letterSpacing: "-0.02em", color: "var(--text)" }}>
                  Create a Room
                </h3>
              </div>
              <p style={{ fontSize: "12px", color: "var(--text-2)", marginBottom: "22px", lineHeight: "1.6" }}>
                Start a new game room and invite others with the link.
                {selectedProblemId && problemDetail && (
                  <> Room starts with <strong style={{ color: "var(--text)" }}>{problemDetail.title}</strong>.</>
                )}
              </p>
              <button
                className="btn btn-primary"
                style={{ width: "100%", padding: "10px 16px", justifyContent: "center" }}
                onClick={handleCreateGame}
              >
                Create Game
              </button>
              <p style={{ fontSize: "11px", color: "var(--text-3)", marginTop: "10px" }}>
                {selectedProblemId ? "Uses selected problem's buggy code." : "Uses template code for selected language."}
              </p>
            </div>

            {/* Join */}
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
                  style={{ width: "100%", padding: "9px 12px", height: "38px", boxSizing: "border-box" }}
                  placeholder="Paste room ID…"
                  value={roomIdInput}
                  onChange={(e: ChangeEvent<HTMLInputElement>) => setRoomIdInput(e.target.value)}
                />
              </div>
              <div style={{ marginBottom: "14px" }}>
                <label className="section-label" style={{ display: "block", marginBottom: "6px" }}>Your Name</label>
                <input
                  className="ui-input"
                  style={{ width: "100%", padding: "9px 12px", height: "38px", boxSizing: "border-box" }}
                  value={playerName}
                  onChange={(e: ChangeEvent<HTMLInputElement>) => setPlayerName(e.target.value)}
                  placeholder="Display name…"
                />
              </div>
              <button
                className="btn btn-ghost"
                style={{ width: "100%", padding: "10px 16px", justifyContent: "center", border: "1px solid var(--border-2)" }}
                onClick={handleJoinGame}
                disabled={!roomIdInput.trim()}
              >
                Join Room
              </button>
            </div>
          </div>
        </div>
      </div>
    );
  }

  /* ── In-game ─────────────────────────────────────────────── */
  return (
    <div style={{ display: "flex", flex: 1, minHeight: 0, overflow: "hidden" }}>
      {/* Problem panel */}
      <div className="problem-panel" style={{ width: "280px", flexShrink: 0 }}>
        <div className="panel-header">
          <div className="panel-icon" style={{ background: "var(--ember-soft)", color: "var(--ember)" }}>
            <svg width="11" height="11" viewBox="0 0 16 16" fill="currentColor">
              <path d="M8 1a7 7 0 100 14A7 7 0 008 1zm0 2a5 5 0 110 10A5 5 0 018 3zm0 3a1 1 0 00-1 1v3a1 1 0 002 0V7a1 1 0 00-1-1zm0-2a1 1 0 100 2 1 1 0 000-2z" />
            </svg>
          </div>
          <span className="panel-header-title">Problem</span>
        </div>
        <div className="problem-content">
          {problemDetail ? (
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
              <div style={{ fontSize: "28px", marginBottom: "12px" }}>🎮</div>
              <p style={{ fontSize: "12px", color: "var(--text-2)", lineHeight: "1.6" }}>
                No problem was selected for this room.
              </p>
            </div>
          )}
        </div>
      </div>

      {/* Editor + Terminal */}
      <div style={{ flex: 1, minWidth: 0, display: "flex", flexDirection: "column", overflow: "hidden", borderLeft: "1px solid var(--border)", borderRight: "1px solid var(--border)" }}>
        {/* Room strip */}
        <div className="room-strip">
          <span className="room-id-badge">{roomState.room_id}</span>
          <span className="elapsed-badge">⏱ {elapsed}s</span>
          <div style={{ flex: 1 }} />
          <button className="btn btn-run" style={{ padding: "5px 12px", height: "32px" }} onClick={runGame} disabled={gameRunning}>
            <PlayIcon />
            {gameRunning ? "Running…" : "Run"}
          </button>
          <button className="btn btn-hint" style={{ padding: "5px 12px", height: "32px" }} onClick={hintGame} disabled={gameBusy}>
            <SparkleIcon />
            {gameBusy ? "Thinking…" : "Ask AI"}
          </button>
        </div>

        {/* Editor info bar */}
        <div className="editor-info-bar">
          <div className="editor-info-left">
            {problemDetail ? (
              <>
                <span className="editor-problem-title">{problemDetail.title}</span>
                {problemDetail.topic && <span className="editor-info-badge editor-badge-topic">{problemDetail.topic}</span>}
                {problemDetail.kind && <span className="editor-info-badge editor-badge-kind">{problemDetail.kind}</span>}
              </>
            ) : (
              <span className="editor-info-placeholder">No problem — free-form room</span>
            )}
          </div>
          <div className="editor-info-right">
            <span className="editor-info-badge editor-badge-lang">{roomState.language}</span>
          </div>
        </div>

        <div style={{ flex: 1, minHeight: 0, overflow: "hidden", background: "#0a0a12" }}>
          <EditorPane language={roomState.language} code={roomState.code} onChange={updateGameCode} height="100%" />
        </div>
        <div className="terminal-resize-handle" onMouseDown={handleTerminalResize} />
        <div style={{ height: `${terminalHeight}px`, flexShrink: 0 }}>
          <Terminal output={gameRun?.stdout ?? ""} error={gameRun?.stderr} exitCode={gameRun?.exit_code} durationMs={gameRun?.duration_ms} />
        </div>
      </div>

      {/* Right sidebar: scoreboard + tutor */}
      <div style={{ width: "320px", flexShrink: 0, display: "flex", flexDirection: "column", overflow: "hidden" }}>
        <Scoreboard players={roomState.players} scores={roomState.scores} hints={roomState.hints_used} />
        <div style={{ flex: 1, minHeight: 0, display: "flex", flexDirection: "column", overflow: "hidden", borderTop: "1px solid var(--border)" }}>
          <div className="panel-header">
            <div className="ai-badge"><span style={{ fontSize: "12px" }}>✦</span></div>
            <div>
              <div style={{ fontSize: "13px", fontWeight: 600, color: "var(--text)" }}>AI Tutor</div>
              <div style={{ fontSize: "10px", color: "var(--text-3)", letterSpacing: "0.06em" }}>
                {(gameHint as any)?.score ? `Score: ${(gameHint as any).score}` : "Room Tutor"}
              </div>
            </div>
          </div>
          <div style={{ flex: 1, minHeight: 0, overflow: "hidden" }}>
            <TutorChatPanel messages={gameChatMessages} input={gameChatInput} busy={gameBusy} onInputChange={setGameChatInput} onSubmit={handleGameTutorChat} />
          </div>
        </div>
      </div>
    </div>
  );
}
