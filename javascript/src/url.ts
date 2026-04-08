import type { StreamRouteOptions, StreamTarget } from "./types.js";

const DEFAULT_BASE_URL = "https://moltchess.com";

function applyTargetParams(params: URLSearchParams, target: StreamTarget) {
  switch (target.type) {
    case "game":
      params.set("game", target.gameId);
      break;
    case "tournament":
      params.set("tournament", target.tournamentId);
      break;
    case "agent":
      params.set("agent", target.handle);
      break;
    case "human":
      params.set("human", target.username);
      break;
    case "all":
      break;
  }
}

export function buildStreamUrl(options: StreamRouteOptions): string {
  const baseUrl = (options.baseUrl ?? DEFAULT_BASE_URL).replace(/\/$/, "");
  const url = new URL(`${baseUrl}/stream`);
  applyTargetParams(url.searchParams, options.target);

  if (options.replay) {
    url.searchParams.set("replay", "1");
  }
  if (options.timestepSeconds != null) {
    url.searchParams.set("timestep", String(options.timestepSeconds));
  }
  if (options.rotateSeconds != null) {
    url.searchParams.set("rotate", String(options.rotateSeconds));
  }

  return url.toString();
}
