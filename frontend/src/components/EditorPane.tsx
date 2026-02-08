import Editor from "@monaco-editor/react";
import type { Language } from "../lib/types";

interface EditorPaneProps {
  language: Language;
  code: string;
  onChange: (value: string) => void;
  height?: string;
}

const languageMap: Record<Language, string> = {
  python: "python",
  java: "java",
  cpp: "cpp",
};

export default function EditorPane({ language, code, onChange, height = "420px" }: EditorPaneProps) {
  return (
    <div className="monaco-wrap shadow-glow">
      <Editor
        height={height}
        language={languageMap[language]}
        theme="vs-dark"
        value={code}
        onChange={(value) => onChange(value ?? "")}
        options={{
          fontFamily: "'IBM Plex Mono', ui-monospace",
          fontSize: 14,
          minimap: { enabled: false },
          scrollBeyondLastLine: false,
        }}
      />
    </div>
  );
}
