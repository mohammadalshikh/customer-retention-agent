import { useEffect, useState } from "react";
import { TabNav, type Tab } from "./components/TabNav";
import { HomeTab } from "./components/HomeTab";
import { ClientTab } from "./components/ClientTab";
import { PlaygroundTab } from "./components/PlaygroundTab";
import { AgentTab } from "./components/AgentTab";
import { useSimulation } from "./hooks/useSimulation";

export default function App() {
  const [tab, setTab] = useState<Tab>("Home");
  const sim = useSimulation();

  useEffect(() => {
    sim.init();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  return (
    <div className="app-shell">
      <div className="app-header">
        <div>
          <div className="app-title">Retention Agents</div>
          <div className="app-subtitle">Live, turn-based customer + retention agent simulation</div>
        </div>
      </div>

      <TabNav active={tab} onChange={setTab} />

      {tab === "Home" && <HomeTab onStart={() => { sim.init(); setTab("Playground"); }} />}
      {tab === "Client" && <ClientTab state={sim.state} />}
      {tab === "Playground" && (
        <PlaygroundTab
          state={sim.state}
          isPlaying={sim.isPlaying}
          thinkingActor={sim.thinkingActor}
          onPlay={sim.play}
          onPause={sim.pause}
          onStep={sim.stepOnce}
        />
      )}
      {tab === "Agent" && <AgentTab state={sim.state} />}
    </div>
  );
}
