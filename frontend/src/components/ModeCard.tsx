interface ModeCardProps {
  title: string;
  description: string;
  action: string;
  onClick: () => void;
}

export default function ModeCard({ title, description, action, onClick }: ModeCardProps) {
  return (
    <button
      className="glass-panel soft-grid p-6 text-left shadow-glow transition hover:-translate-y-1"
      onClick={onClick}
    >
      <h3 className="font-display text-lg text-dune">{title}</h3>
      <p className="mt-2 text-sm text-dune/70">{description}</p>
      <div className="mt-6 inline-flex items-center gap-2 text-sm font-semibold text-ember">
        {action}
        <span aria-hidden>→</span>
      </div>
    </button>
  );
}
