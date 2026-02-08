import { useEffect, useMemo, useRef, useState } from "react";
import TopBar from "./components/TopBar";
import ModeCard from "./components/ModeCard";
import EditorPane from "./components/EditorPane";
import Terminal from "./components/Terminal";
import HintPanel from "./components/HintPanel";
import Scoreboard from "./components/Scoreboard";
import ProblemPicker from "./components/ProblemPicker";
import ProblemPanel from "./components/ProblemPanel";
import { createGame, fetchProblem, fetchProblems, fetchRoom, requestHint, runCode } from "./lib/api";
import type { HintResult, Language, RoomState, RunResult, WsMessage, ProblemDetail, ProblemSummary } from "./lib/types";
import { createRoomSocket } from "./lib/ws";

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
  const [loading, setLoading] = useState(false);

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
    setLoading(true);
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
      setLoading(false);
    }
  };

  const handleHint = async () => {
    setLoading(true);
    try {
      const result = await requestHint(language, code, runResult?.stderr, history);
      setHint(result);
      setHistory((prev) => [...prev, result.hint]);
    } catch (err) {
      setHint({
        hint: err instanceof Error ? err.message : "Hint failed",
        intent: "error",
        score: 0,
      });
    } finally {
      setLoading(false);
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
        setRoomState((prev) => (prev ? { ...prev, code: message.payload.code } : prev));
      }
      if (message.type === "score_update") {
        setRoomState((prev) => (prev ? { ...prev, scores: message.payload.scores } : prev));
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
    setRoomState((prev) => (prev ? { ...prev, code: value } : prev));
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
      payload: { code: roomState.code, language: roomState.language, error: gameRun?.stderr, history: [] },
    });
  };

  return (
    <div className="min-h-screen px-6 py-10 text-dune">
      <div className="app-shell mx-auto max-w-6xl p-8 shadow-glow">
        <TopBar mode={mode} onBack={mode === "home" ? undefined : () => setMode("home")} />

        {mode === "home" && (
          <div className="mt-10 grid gap-6 md:grid-cols-2">
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
        )}

        {mode === "practice" && (
          <div className="mt-8 grid gap-6 lg:grid-cols-[2fr_1fr]">
            <div className="space-y-4">
              <div className="flex flex-wrap items-center gap-3">
                <select
                  className="rounded-full border border-dune/20 bg-transparent px-4 py-2 text-sm"
                  value={language}
                  onChange={(e) => setLanguage(e.target.value as Language)}
                >
                  <option value="python">Python</option>
                  <option value="java">Java</option>
                  <option value="cpp">C++</option>
                </select>
                <ProblemPicker
                  problems={problems}
                  selectedId={selectedProblemId}
                  onSelect={setSelectedProblemId}
                />
                <button
                  className="rounded-full bg-ember px-4 py-2 text-sm font-semibold text-ink"
                  onClick={handleRun}
                  disabled={loading}
                >
                  {loading ? "Running..." : "Run"}
                </button>
                <button
                  className="rounded-full border border-mint/60 px-4 py-2 text-sm font-semibold text-mint"
                  onClick={handleHint}
                  disabled={loading}
                >
                  Request Hint
                </button>
              </div>
              <EditorPane language={language} code={code} onChange={setCode} />
            </div>
            <div className="grid gap-4">
              <ProblemPanel problem={problemDetail} />
              <Terminal output={runResult?.stdout ?? ""} error={runResult?.stderr} />
              <HintPanel hint={hint?.hint ?? ""} intent={hint?.intent} score={hint?.score} />
            </div>
          </div>
        )}

        {mode === "game" && (
          <div className="mt-8 grid gap-6">
            {!roomState && (
              <div className="grid gap-6 lg:grid-cols-[2fr_1fr]">
                <div className="glass-panel p-6">
                  <div className="text-sm text-dune/70">Start a room</div>
                  <div className="mt-4 flex flex-wrap gap-3">
                    <select
                      className="rounded-full border border-dune/20 bg-transparent px-4 py-2 text-sm"
                      value={language}
                      onChange={(e) => setLanguage(e.target.value as Language)}
                    >
                      <option value="python">Python</option>
                      <option value="java">Java</option>
                      <option value="cpp">C++</option>
                    </select>
                    <button
                      className="rounded-full bg-sky px-4 py-2 text-sm font-semibold text-ink"
                      onClick={handleCreateGame}
                    >
                      Create game
                    </button>
                  </div>
                  <div className="mt-6 text-xs text-dune/50">Seed code will use the current editor snippet.</div>
                </div>
                <div className="glass-panel p-6">
                  <div className="text-sm text-dune/70">Join existing room</div>
                  <div className="mt-4 flex flex-wrap gap-3">
                    <input
                      className="rounded-full border border-dune/20 bg-transparent px-4 py-2 text-sm"
                      placeholder="Room ID"
                      value={roomId}
                      onChange={(e) => setRoomId(e.target.value)}
                    />
                    <button
                      className="rounded-full border border-dune/40 px-4 py-2 text-sm"
                      onClick={handleJoinGame}
                    >
                      Join
                    </button>
                  </div>
                  <div className="mt-4 text-sm text-dune/70">Your name</div>
                  <input
                    className="mt-2 w-full rounded-full border border-dune/20 bg-transparent px-4 py-2 text-sm"
                    value={playerName}
                    onChange={(e) => setPlayerName(e.target.value)}
                  />
                </div>
              </div>
            )}

            {roomState && (
              <div className="grid gap-6 lg:grid-cols-[2fr_1fr]">
                <div className="space-y-4">
                  <div className="flex flex-wrap items-center gap-3">
                    <div className="rounded-full border border-dune/20 px-4 py-2 text-sm">
                      Room <span className="font-semibold text-ember">{roomState.room_id}</span>
                    </div>
                    <div className="rounded-full border border-dune/20 px-4 py-2 text-sm">
                      Elapsed {elapsed}s
                    </div>
                    <button
                      className="rounded-full bg-ember px-4 py-2 text-sm font-semibold text-ink"
                      onClick={runGame}
                    >
                      Run
                    </button>
                    <button
                      className="rounded-full border border-mint/60 px-4 py-2 text-sm font-semibold text-mint"
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
