import clsx from "clsx";

interface TopBarProps {
  mode: "home" | "practice" | "game";
  onBack?: () => void;
}

export default function TopBar({ mode, onBack }: TopBarProps) {
  return (
    <header className="flex items-center justify-between py-4">
      <div className="flex items-center gap-3">
        <div className="h-10 w-10 rounded-xl bg-ember/20 text-ember flex items-center justify-center font-display text-lg">
          SS
        </div>
        <div>
          <div className="font-display text-xl">Socratic Sprint</div>
          <div className="text-xs text-dune/60">Pedagogy-first coding practice</div>
        </div>
      </div>
      <div className="flex items-center gap-3">
        <span
          className={clsx(
            "rounded-full px-3 py-1 text-xs uppercase tracking-[0.2em]",
            mode === "practice" && "bg-mint/20 text-mint",
            mode === "game" && "bg-sky/20 text-sky",
            mode === "home" && "bg-dune/10 text-dune/60"
          )}
        >
          {mode}
        </span>
        {onBack && (
          <button
            className="rounded-full border border-dune/20 px-4 py-2 text-sm hover:border-dune/40"
            onClick={onBack}
          >
            Back
          </button>
        )}
      </div>
    </header>
  );
}
