import type { ProblemSummary } from "../lib/types";

interface ProblemPickerProps {
  problems: ProblemSummary[];
  selectedId?: string;
  onSelect: (id: string) => void;
}

export default function ProblemPicker({ problems, selectedId, onSelect }: ProblemPickerProps) {
  return (
    <select
      className="rounded-full border border-dune/20 bg-transparent px-4 py-2 text-sm"
      value={selectedId ?? ""}
      onChange={(e) => onSelect(e.target.value)}
    >
      <option value="">Select a problem</option>
      {problems.map((problem) => (
        <option key={problem.id} value={problem.id}>
          {problem.title}
        </option>
      ))}
    </select>
  );
}
