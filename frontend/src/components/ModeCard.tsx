interface ModeCardProps {
  title: string;
  description: string;
  action: string;
  onClick: () => void;
}

export default function ModeCard({ title, description, action, onClick }: ModeCardProps) {
  return (
    <button
      className="glass-panel hero-grid ui-button soft-grid p-7 text-left"
      onClick={onClick}
    >
      <div className="text-[11px] font-medium uppercase tracking-[0.24em] text-white/45">Mode</div>
      <h3 className="mt-3 text-2xl font-semibold tracking-tight text-white">{title}</h3>
      <p className="mt-3 max-w-md text-sm leading-6 text-white/62">{description}</p>
      <div className="mt-8 inline-flex items-center gap-2 rounded-full border border-blue-500/20 bg-blue-500/10 px-4 py-2 text-sm font-medium text-blue-300">
        {action}
        <span aria-hidden>→</span>
      </div>
    </button>
  );
}
