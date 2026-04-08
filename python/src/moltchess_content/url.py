from __future__ import annotations

from urllib.parse import urlencode

from .types import StreamRoute


def build_stream_url(route: StreamRoute) -> str:
    params: list[tuple[str, str]] = []

    if route.target.type == "game" and route.target.value:
        params.append(("game", route.target.value))
    elif route.target.type == "tournament" and route.target.value:
        params.append(("tournament", route.target.value))
    elif route.target.type == "agent" and route.target.value:
        params.append(("agent", route.target.value))
    elif route.target.type == "human" and route.target.value:
        params.append(("human", route.target.value))

    if route.replay:
        params.append(("replay", "1"))
    if route.timestep_seconds is not None:
        params.append(("timestep", str(route.timestep_seconds)))
    if route.rotate_seconds is not None:
        params.append(("rotate", str(route.rotate_seconds)))

    query = urlencode(params)
    base = route.base_url.rstrip("/")
    return f"{base}/stream" + (f"?{query}" if query else "")
