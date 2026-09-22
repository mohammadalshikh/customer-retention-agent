import os
import requests

JSONBIN_BASE = "https://api.jsonbin.io/v3/b"
_bin_id = os.environ.get("JSONBIN_BIN_ID")
_api_key = os.environ.get("JSONBIN_API_KEY")


def _headers() -> dict:
    return {"Content-Type": "application/json", "X-Master-Key": _api_key}


def save_state(state_dict: dict) -> None:
    if not _bin_id or not _api_key:
        return  # storage is optional
    try:
        requests.put(f"{JSONBIN_BASE}/{_bin_id}", json=state_dict, headers=_headers(), timeout=5)
    except requests.RequestException as e:
        print(f"[storage] save failed (continuing in-memory only): {e}")


def load_state() -> dict | None:
    if not _bin_id or not _api_key:
        return None
    try:
        resp = requests.get(f"{JSONBIN_BASE}/{_bin_id}/latest", headers=_headers(), timeout=5)
        resp.raise_for_status()
        return resp.json().get("record")
    except requests.RequestException as e:
        print(f"[storage] load failed: {e}")
        return None
