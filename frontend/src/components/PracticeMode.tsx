import { useEffect, useState, type ChangeEvent, type MouseEvent as ReactMouseEvent } from "react";
import EditorPane from "./EditorPane";
import Terminal from "./Terminal";
import TutorChatPanel from "./TutorChatPanel";
import { fetchProblem, fetchProblems, runCode, sendTutorChat } from "../lib/api";
import type { ChatMessage, HintResult, Language, ProblemDetail, ProblemSummary, RunResult } from "../lib/types";

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
const XIcon = () => (
  <svg width="11" height="11" viewBox="0 0 16 16" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round"><path d="M3 3L13 13M13 3L3 13" /></svg>
);

export default function PracticeMode() {
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
  const [terminalHeight, setTerminalHeight] = useState(192);

  useEffect(() => {
    if (!selectedProblemId) setCode(templates[language]);
  }, [language, selectedProblemId]);

  useEffect(() => {
    fetchProblems(language, "buggy", 200).then(setProblems).catch(() => setProblems([]));
  }, [language]);

  useEffect(() => {
    if (!selectedProblemId) { setProblemDetail(null); return; }
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

  const handleRun = async () => {
    setRunning(true);
    try {
      setRunResult(await runCode(language, code));
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
      const result = await sendTutorChat(language, code, "", sessionId, selectedProblemId || undefined, output, history, chatMessages);
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
    setChatMessages((prev) => [...prev, { role: "student", content: userMessage }]);
    setChatInput("");
    setChatting(true);
    try {
      const result = await sendTutorChat(language, code, userMessage, sessionId, selectedProblemId || undefined, output, history, chatMessages);
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

  const handleClear = () => {
    setSelectedProblemId("");
    setProblemDetail(null);
    setHistory([]);
    setHint(null);
    setChatMessages([]);
    setChatInput("");
    setSessionId(makeId());
  };

  const busy = chatting || analyzing;

  return (
    <div style={{ display: "flex", flex: 1, minHeight: 0, overflow: "hidden", flexDirection: "column" }}>
      {/* ── Practice toolbar ──────────────────────────── */}
      <div className="practice-toolbar">
        {/* Left: label + selects */}
        <div style={{ fontSize: "10px", fontWeight: 600, letterSpacing: "0.12em", textTransform: "uppercase", color: "var(--text-3)", flexShrink: 0 }}>
          Problem
        </div>
        <select
          className="ui-select"
          style={{ padding: "5px 28px 5px 10px", height: "32px", flexShrink: 0 }}
          value={language}
          onChange={(e: ChangeEvent<HTMLSelectElement>) => setLanguage(e.target.value as Language)}
        >
          <option value="python">Python</option>
          <option value="java">Java</option>
          <option value="cpp">C++</option>
        </select>
        <select
          className="ui-select"
          style={{ padding: "5px 28px 5px 10px", height: "32px", flex: 1, minWidth: 0, maxWidth: "320px" }}
          value={selectedProblemId}
          onChange={(e: ChangeEvent<HTMLSelectElement>) => setSelectedProblemId(e.target.value)}
        >
          <option value="">Select a problem…</option>
          {problems.map((p) => (
            <option key={p.id} value={p.id}>{p.title}</option>
          ))}
        </select>

        {/* Spacer pushes buttons to the right */}
        <div style={{ flex: 1 }} />

        {/* Right: action buttons */}
        <div className="toolbar-divider" />
        <button className="btn btn-run" style={{ padding: "5px 12px", height: "32px" }} onClick={handleRun} disabled={running}>
          <PlayIcon />
          {running ? "Running…" : "Run"}
        </button>
        <button className="btn btn-hint" style={{ padding: "5px 12px", height: "32px" }} onClick={handleHint} disabled={busy}>
          <SparkleIcon />
          {busy ? "Thinking…" : "Ask AI"}
        </button>
        <button className="btn btn-ghost" style={{ padding: "5px 10px", height: "32px" }} onClick={handleClear} title="Clear session">
          <XIcon />
        </button>
      </div>

      {/* ── Three-panel layout ────────────────────────── */}
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
                <div style={{ fontSize: "28px", marginBottom: "12px" }}>📋</div>
                <p style={{ fontSize: "12px", color: "var(--text-2)", lineHeight: "1.6" }}>
                  {selectedProblemId ? "Loading…" : "Select a problem above to get started."}
                </p>
              </div>
            )}
          </div>
        </div>

        {/* Editor + Terminal */}
        <div style={{ flex: 1, minWidth: 0, display: "flex", flexDirection: "column", overflow: "hidden", borderLeft: "1px solid var(--border)", borderRight: "1px solid var(--border)" }}>
          <div className="editor-info-bar">
            <div className="editor-info-left">
              {problemDetail ? (
                <>
                  <span className="editor-problem-title">{problemDetail.title}</span>
                  {problemDetail.topic && <span className="editor-info-badge editor-badge-topic">{problemDetail.topic}</span>}
                  {problemDetail.kind && <span className="editor-info-badge editor-badge-kind">{problemDetail.kind}</span>}
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
            <Terminal output={runResult?.stdout ?? ""} error={runResult?.stderr} exitCode={runResult?.exit_code} durationMs={runResult?.duration_ms} />
          </div>
        </div>

        {/* AI Tutor panel */}
        <div style={{ width: "340px", flexShrink: 0, display: "flex", flexDirection: "column", overflow: "hidden" }}>
          <div className="panel-header">
            <div className="ai-badge"><span style={{ fontSize: "12px" }}>✦</span></div>
            <div>
              <div style={{ fontSize: "13px", fontWeight: 600, color: "var(--text)" }}>AI Tutor</div>
              <div style={{ fontSize: "10px", color: "var(--text-3)", letterSpacing: "0.06em" }}>
                {(hint as any)?.score ? `Score: ${(hint as any).score}` : "Socratic Mode"}
              </div>
            </div>
          </div>
          <div style={{ flex: 1, minHeight: 0, overflow: "hidden" }}>
            <TutorChatPanel messages={chatMessages} input={chatInput} busy={busy} onInputChange={setChatInput} onSubmit={handleTutorChat} />
          </div>
        </div>
      </div>
    </div>
  );
}
