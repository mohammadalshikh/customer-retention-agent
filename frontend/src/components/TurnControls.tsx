interface Props {
  tick: number;
  isPlaying: boolean;
  thinkingActor: string | null;
  isComplete: boolean;
  onPlay: () => void;
  onPause: () => void;
  onStep: () => void;
}

export function TurnControls({ tick, isPlaying, thinkingActor, isComplete, onPlay, onPause, onStep }: Props) {
  return (
    <div className="turn-controls panel">
      <span style={{ fontSize: 13, color: "var(--text-dim)" }}>Tick {tick}</span>
      {isPlaying ? (
        <button className="btn" onClick={onPause}>Pause</button>
      ) : (
        <button className="btn primary" onClick={onPlay} disabled={isComplete}>Play</button>
      )}
      <button className="btn" onClick={onStep} disabled={isPlaying || isComplete}>Next Turn</button>
      {thinkingActor && (
        <span className="thinking-indicator">
          <span className="dot" />
          {thinkingActor.startsWith("retention:")
            ? `Retention agent investigating ${thinkingActor.split(":")[1]}...`
            : `${thinkingActor} is deciding...`}
        </span>
      )}
      {isComplete && <span style={{ fontSize: 13, color: "var(--text-dim)" }}>Simulation complete.</span>}
    </div>
  );
}
