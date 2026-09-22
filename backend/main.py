from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from schemas import SimulationState
from simulation import new_simulation, process_next_turn
import storage

app = FastAPI(title="Retention Agents Simulation")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Vite dev server default
    allow_methods=["*"],
    allow_headers=["*"],
)

_state: SimulationState = new_simulation()


@app.post("/simulation/start")
def start_simulation():
    global _state
    _state = new_simulation()
    storage.save_state(_state.model_dump())
    return _state.model_dump()


@app.get("/simulation/state")
def get_state():
    return _state.model_dump()


@app.post("/simulation/next-turn")
def next_turn():
    event = process_next_turn(_state)
    storage.save_state(_state.model_dump())
    return {"event": event, "state": _state.model_dump()}
