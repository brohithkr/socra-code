export type Language = "python" | "java" | "cpp";

export interface RunResult {
  ok: boolean;
  stdout: string;
  stderr: string;
  exit_code: number;
  duration_ms: number;
}

export interface HintResult {
  hint: string;
}

export interface ChatMessage {
  role: "student" | "tutor";
  content: string;
}

export interface RoomState {
  room_id: string;
  language: Language;
  code: string;
  players: Record<string, string>;
  scores: Record<string, number>;
  hints_used: Record<string, number>;
  started_at: number;
  updated_at: number;
}

export interface WsMessage<T = any> {
  type: string;
  payload: T;
}

export interface ProblemSummary {
  id: string;
  title: string;
  language: string;
  topic?: string;
  source: string;
  kind: string;
}

export interface ProblemDetail extends ProblemSummary {
  statement: string;
  starter_code: string;
  buggy_code?: string;
  bug_desc?: string;
  bug_fixes?: string;
}
