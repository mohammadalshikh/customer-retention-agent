const TABS = ["Home", "Client", "Playground", "Agent"] as const;
export type Tab = (typeof TABS)[number];

export function TabNav({ active, onChange }: { active: Tab; onChange: (t: Tab) => void }) {
  return (
    <nav className="tab-nav">
      {TABS.map((tab) => (
        <button
          key={tab}
          className={`tab-btn ${active === tab ? "active" : ""}`}
          onClick={() => onChange(tab)}
        >
          {tab}
        </button>
      ))}
    </nav>
  );
}
