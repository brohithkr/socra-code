import type { HintResult, Language, RunResult, RoomState, ProblemSummary, ProblemDetail } from "./types";

const API_URL = import.meta.env.VITE_API_URL ?? "http://localhost:8000";

export async function runCode(language: Language, code: string, stdin?: string): Promise<RunResult> {
  const resp = await fetch(`${API_URL}/run`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ language, code, stdin }),
  });
  if (!resp.ok) {
    throw new Error("Run failed");
  }
  return resp.json();
}

export async function requestHint(language: Language, code: string, output?: string, history: string[] = []): Promise<HintResult> {
  const resp = await fetch(`${API_URL}/hint`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ language, code, output, history }),
  });
  if (!resp.ok) {
    throw new Error("Hint failed");
  }
  return resp.json();
}

export async function createGame(language: Language, seed_code: string): Promise<RoomState> {
  const resp = await fetch(`${API_URL}/create-game`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ language, seed_code }),
  });
  if (!resp.ok) {
    throw new Error("Create game failed");
  }
  const data = await resp.json();
  return data.state as RoomState;
}

export async function fetchRoom(roomId: string): Promise<RoomState> {
  const resp = await fetch(`${API_URL}/room/${roomId}`);
  if (!resp.ok) {
    throw new Error("Room not found");
  }
  const data = await resp.json();
  return data.state as RoomState;
}

export async function fetchProblems(language?: string, kind: string = "buggy", limit: number = 50): Promise<ProblemSummary[]> {
  const params = new URLSearchParams();
  if (language) params.set("language", language);
  if (kind) params.set("kind", kind);
  params.set("limit", String(limit));
  const resp = await fetch(`${API_URL}/problems?${params.toString()}`);
  if (!resp.ok) {
    throw new Error("Failed to load problems");
  }
  const data = await resp.json();
  return data.items as ProblemSummary[];
}

export async function fetchProblem(problemId: string): Promise<ProblemDetail> {
  const resp = await fetch(`${API_URL}/problems/${problemId}`);
  if (!resp.ok) {
    throw new Error("Problem not found");
  }
  return resp.json();
}
