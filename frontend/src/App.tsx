import { useEffect, useMemo, useRef, useState, type ChangeEvent } from "react";
import TopBar from "./components/TopBar";
import ModeCard from "./components/ModeCard";
import EditorPane from "./components/EditorPane";
import Terminal from "./components/Terminal";
import HintPanel from "./components/HintPanel";
import Scoreboard from "./components/Scoreboard";
import { createGame, fetchProblem, fetchProblems, fetchRoom, requestHint, runCode } from "./lib/api";
import type { HintResult, Language, RoomState, RunResult, WsMessage, ProblemDetail, ProblemSummary } from "./lib/types";
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

export default function App() {
  const [mode, setMode] = useState<"home" | "practice" | "game">("home");

  const [language, setLanguage] = useState<Language>("python");
  const [code, setCode] = useState<string>(templates.python);
  const [runResult, setRunResult] = useState<RunResult | null>(null);
  const [hint, setHint] = useState<HintResult | null>(null);
  const [history, setHistory] = useState<string[]>([]);
  const [running, setRunning] = useState(false);
  const [analyzing, setAnalyzing] = useState(false);

  const [problems, setProblems] = useState<ProblemSummary[]>([]);
  const [selectedProblemId, setSelectedProblemId] = useState<string>("");
  const [problemDetail, setProblemDetail] = useState<ProblemDetail | null>(null);

  const [roomState, setRoomState] = useState<RoomState | null>(null);
  const [roomId, setRoomId] = useState<string>("");
  const [playerName, setPlayerName] = useState<string>("Player One");
  const playerIdRef = useRef(makeId());
  const socketRef = useRef<ReturnType<typeof createRoomSocket> | null>(null);
  const [gameHint, setGameHint] = useState<HintResult | null>(null);
  const [gameRun, setGameRun] = useState<RunResult | null>(null);

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
        const nextCode = detail.buggy_code || detail.starter_code || templates.python;
        setCode(nextCode);
        setHistory([]);
        setHint(null);
      })
      .catch(() => {
        setProblemDetail(null);
      });
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
      setRunResult({
        ok: false,
        stdout: "",
        stderr: err instanceof Error ? err.message : "Run failed",
        exit_code: 1,
        duration_ms: 0,
      });
    } finally {
      setRunning(false);
    }
  };

  const handleHint = async () => {
    setAnalyzing(true);
    try {
      const output = runResult ? (runResult.stdout + runResult.stderr).trim() || undefined : undefined;
      const result = await requestHint(language, code, output, history);
      setHint(result);
      setHistory((prev: string[]) => [...prev, result.hint]);
    } catch (err) {
      setHint({
        hint: err instanceof Error ? err.message : "Hint failed",
      });
    } finally {
      setAnalyzing(false);
    }
  };

  const connectRoom = (state: RoomState) => {
    setRoomState(state);
    const baseUrl = import.meta.env.VITE_API_URL ?? "http://localhost:8000";
    const socket = createRoomSocket(baseUrl, state.room_id, playerIdRef.current, playerName);
    socketRef.current = socket;
    socket.onMessage((message: WsMessage) => {
      if (message.type === "room_state") {
        setRoomState(message.payload.state as RoomState);
      }
      if (message.type === "code_update") {
        setRoomState((prev: RoomState | null) => (prev ? { ...prev, code: message.payload.code } : prev));
      }
      if (message.type === "score_update") {
        setRoomState((prev: RoomState | null) => (prev ? { ...prev, scores: message.payload.scores } : prev));
      }
      if (message.type === "hint_result") {
        setGameHint(message.payload as HintResult);
      }
      if (message.type === "run_result") {
        setGameRun(message.payload as RunResult);
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

  const sendGameMessage = (message: WsMessage) => {
    socketRef.current?.send(message);
  };

  const updateGameCode = (value: string) => {
    setRoomState((prev: RoomState | null) => (prev ? { ...prev, code: value } : prev));
    sendGameMessage({ type: "code_update", payload: { code: value } });
  };

  const runGame = () => {
    if (!roomState) return;
    sendGameMessage({ type: "run_request", payload: { code: roomState.code, language: roomState.language } });
  };

  const hintGame = () => {
    if (!roomState) return;
    sendGameMessage({
      type: "hint_request",
      payload: { code: roomState.code, language: roomState.language, output: gameRun ? (gameRun.stdout + gameRun.stderr).trim() || undefined : undefined, history: [] },
    });
  };

  return (
    <div className="h-screen overflow-hidden p-0 text-white">
      <div className="app-shell mx-auto flex h-full max-w-[1500px] flex-col overflow-hidden p-0">
        <TopBar
          mode={mode}
          onBack={mode === "home" ? undefined : () => setMode("home")}
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
                }
              : undefined
          }
          running={running}
          analyzing={analyzing}
        />

        {mode === "home" && (
          <div className="grid flex-1 gap-0 overflow-auto p-0 xl:grid-cols-[1.1fr_0.9fr]">
            <section className="glass-panel hero-grid soft-grid overflow-hidden p-6 md:p-8">
              <div className="relative">
                <div className="inline-flex rounded-full border border-blue-500/20 bg-blue-500/10 px-4 py-2 text-[11px] font-medium uppercase tracking-[0.24em] text-blue-300">
                  Socratic Tutor Workspace
                </div>
                <h1 className="mt-6 max-w-2xl text-4xl font-semibold tracking-tight text-white md:text-5xl">
                  Practice debugging in a studio built for questions, not answers.
                </h1>
                <p className="mt-5 max-w-2xl text-base leading-8 text-white/65">
                  Run code, inspect failures, and ask the tutor for guided hints inside a darker, focused coding workflow.
                </p>
                <div className="mt-8 flex flex-wrap gap-3">
                  <button
                    className="ui-button rounded-xl bg-blue-600 px-5 py-3 text-sm font-semibold text-white shadow-[0_10px_30px_rgba(37,99,235,0.35)]"
                    onClick={() => setMode("practice")}
                  >
                    Open Practice Studio
                  </button>
                  <button
                    className="ui-button rounded-xl border border-white/10 bg-white/[0.03] px-5 py-3 text-sm font-semibold text-white/85"
                    onClick={() => setMode("game")}
                  >
                    Open Multiplayer Room
                  </button>
                </div>
              </div>
            </section>
            <div className="grid gap-0 md:grid-cols-2 xl:grid-cols-1">
              <ModeCard
                title="Practice Mode"
                description="Work solo with Socratic hints. Run code, track errors, and learn through guided questions."
                action="Enter practice"
                onClick={() => setMode("practice")}
              />
              <ModeCard
                title="Game Mode"
                description="Create or join a room, sync code in real-time, and compete on hints vs speed."
                action="Enter game"
                onClick={() => setMode("game")}
              />
            </div>
          </div>
        )}

        {mode === "practice" && (
          <div className="flex min-h-0 flex-1 gap-0 overflow-hidden">
            {/* Left column: Problem statement */}
            <div className="glass-panel w-80 flex-none flex-col overflow-y-auto border-r border-white/5 p-3">
              {selectedProblemId && problemDetail ? (
                <>
                  <div className="whitespace-pre-wrap text-sm leading-7 text-white/72">
                    {problemDetail.statement}
                  </div>
                  {problemDetail.bug_desc && (
                    <div className="mt-4 rounded-lg bg-emerald-500/8 px-3 py-2 text-xs leading-6 text-emerald-200/85">
                      <div className="font-semibold text-emerald-300 mb-1">Bug Description</div>
                      {problemDetail.bug_desc}
                    </div>
                  )}
                </>
              ) : (
                <div className="flex flex-col items-center justify-center text-center">
                  <div className="text-sm text-white/50 mb-2">📝</div>
                  <p className="text-sm text-white/65">
                    {selectedProblemId ? "Loading problem..." : "Select a problem from the top menu"}
                  </p>
                </div>
              )}
            </div>

            {/* Center column: Editor + Terminal */}
            <div className="flex min-w-0 flex-1 flex-col gap-0">
              <div className="relative min-h-0 flex-1 overflow-hidden bg-neutral-900">
                <EditorPane language={language} code={code} onChange={setCode} height="100%" />
              </div>
              <div className="h-48 flex-none border-t border-white/5">
                <Terminal output={runResult?.stdout ?? ""} error={runResult?.stderr} />
              </div>
            </div>

            {/* Right column: Tutor/Hint panel */}
            <div className="glass-panel w-96 flex-none flex-col overflow-hidden border-l border-white/5">
              <div className="flex-none border-b border-white/5 bg-neutral-900/50 px-3 py-2">
                <div className="flex items-center gap-2">
                  <div className="flex h-6 w-6 items-center justify-center rounded-full bg-gradient-to-br from-blue-500 to-purple-600 text-white">
                    <span className="text-xs">✦</span>
                  </div>
                  <div>
                    <div className="text-sm font-semibold text-gray-100">AI Teacher</div>
                    <div className="text-[10px] text-gray-400">
                      {hint?.score ? `Score: ${hint.score}` : "Socratic Mode"}
                    </div>
                  </div>
                </div>
              </div>
              <div className="flex-1 overflow-y-auto bg-gray-950/50 p-0">
                <HintPanel hint={hint?.hint ?? ""} intent={hint?.intent} score={hint?.score} />
              </div>
            </div>
          </div>
        )}

        {mode === "game" && (
          <div className="grid gap-0 p-0 flex-1">
            {!roomState && (
              <div className="grid gap-6 lg:grid-cols-[2fr_1fr] p-6">
                <div className="glass-panel p-6">
                  <div className="text-sm text-white/70">Start a room</div>
                  <div className="mt-4 flex flex-wrap gap-3">
                    <select
                      className="ui-select rounded-xl px-4 py-2.5 text-sm"
                      value={language}
                      onChange={(e: ChangeEvent<HTMLSelectElement>) => setLanguage(e.target.value as Language)}
                    >
                      <option value="python">Python</option>
                      <option value="java">Java</option>
                      <option value="cpp">C++</option>
                    </select>
                    <button
                      className="ui-button rounded-xl bg-blue-600 px-4 py-2.5 text-sm font-semibold text-white"
                      onClick={handleCreateGame}
                    >
                      Create game
                    </button>
                  </div>
                  <div className="mt-6 text-xs text-white/45">Seed code will use the current editor snippet.</div>
                </div>
                <div className="glass-panel p-6">
                  <div className="text-sm text-white/70">Join existing room</div>
                  <div className="mt-4 flex flex-wrap gap-3">
                    <input
                      className="ui-input rounded-xl px-4 py-2.5 text-sm"
                      placeholder="Room ID"
                      value={roomId}
                      onChange={(e: ChangeEvent<HTMLInputElement>) => setRoomId(e.target.value)}
                    />
                    <button
                      className="ui-button rounded-xl border border-white/10 px-4 py-2.5 text-sm text-white/85"
                      onClick={handleJoinGame}
                    >
                      Join
                    </button>
                  </div>
                  <div className="mt-4 text-sm text-white/70">Your name</div>
                  <input
                    className="ui-input mt-2 w-full rounded-xl px-4 py-2.5 text-sm"
                    value={playerName}
                    onChange={(e: ChangeEvent<HTMLInputElement>) => setPlayerName(e.target.value)}
                  />
                </div>
              </div>
            )}

            {roomState && (
              <div className="grid gap-6 lg:grid-cols-[2fr_1fr] p-6">
                <div className="space-y-4">
                  <div className="flex flex-wrap items-center gap-3">
                    <div className="status-pill rounded-xl px-4 py-2 text-sm text-white/78">
                      Room <span className="font-semibold text-blue-300">{roomState.room_id}</span>
                    </div>
                    <div className="status-pill rounded-xl px-4 py-2 text-sm text-white/78">
                      Elapsed {elapsed}s
                    </div>
                    <button
                      className="ui-button rounded-xl border border-emerald-500/25 bg-emerald-500/10 px-4 py-2.5 text-sm font-semibold text-emerald-300"
                      onClick={runGame}
                    >
                      Run
                    </button>
                    <button
                      className="ui-button rounded-xl border border-blue-500/25 bg-blue-500/10 px-4 py-2.5 text-sm font-semibold text-blue-300"
                      onClick={hintGame}
                    >
                      Hint
                    </button>
                  </div>
                  <EditorPane
                    language={roomState.language}
                    code={roomState.code}
                    onChange={updateGameCode}
                    height="480px"
                  />
                </div>
                <div className="grid gap-4">
                  <Scoreboard
                    players={roomState.players}
                    scores={roomState.scores}
                    hints={roomState.hints_used}
                  />
                  <Terminal output={gameRun?.stdout ?? ""} error={gameRun?.stderr} />
                  <HintPanel hint={gameHint?.hint ?? ""} intent={gameHint?.intent} score={gameHint?.score} />
                </div>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
