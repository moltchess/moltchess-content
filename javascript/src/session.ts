import { startBrowserSession } from "./browser.js";
import { connectObs, launchObsProcess } from "./obs.js";
import type { ObsConnectionOptions, ObsProcessOptions, StartStreamSessionOptions, StreamRouteOptions, StreamSession } from "./types.js";
import { buildStreamUrl } from "./url.js";

async function applyObsState(
  url: string,
  obsOptions: ObsConnectionOptions,
  obsController: NonNullable<StreamSession["obsController"]>,
) {
  if (obsOptions.sceneName) {
    await obsController.setScene(obsOptions.sceneName);
  }
  if (obsOptions.sourceName) {
    await obsController.setBrowserSourceUrl(
      obsOptions.sourceName,
      url,
      obsOptions.browserWidth,
      obsOptions.browserHeight,
    );
  }
  if (obsOptions.autoStartRecord) {
    await obsController.startRecord();
  }
  if (obsOptions.autoStartStream) {
    await obsController.startStream();
  }
}

export async function startStreamSession(options: StartStreamSessionOptions): Promise<StreamSession> {
  const url = buildStreamUrl(options.stream);
  const obsProcessOptions =
    options.obsProcess && typeof options.obsProcess === "object" ? (options.obsProcess as ObsProcessOptions) : undefined;
  const obsOptions =
    options.obs && typeof options.obs === "object" ? (options.obs as ObsConnectionOptions) : undefined;

  const obsProcess = obsProcessOptions ? await launchObsProcess(obsProcessOptions) : undefined;
  const obsController = obsOptions ? await connectObs(obsOptions) : undefined;
  const browserSession = options.browser === false ? undefined : await startBrowserSession(url, options.browser);

  if (obsController && obsOptions) {
    await applyObsState(url, obsOptions, obsController);
  }

  let stopped = false;
  const stop = async () => {
    if (stopped) return;
    stopped = true;

    if (obsController) {
      if (obsOptions?.autoStopRecord) {
        await obsController.stopRecord();
      }
      if (obsOptions?.autoStopStream) {
        await obsController.stopStream();
      }
      await obsController.disconnect();
    }

    if (browserSession) {
      await browserSession.close();
    }

    if (obsProcess) {
      await obsProcess.stop();
    }
  };

  let currentStream = options.stream;

  const updateUrl = async (overrides: Partial<StreamRouteOptions>) => {
    currentStream = { ...currentStream, ...overrides };
    const nextUrl = buildStreamUrl(currentStream);

    if (browserSession) {
      await browserSession.goto(nextUrl);
    }
    if (obsController && obsOptions?.sourceName) {
      await obsController.setBrowserSourceUrl(
        obsOptions.sourceName,
        nextUrl,
        obsOptions.browserWidth,
        obsOptions.browserHeight,
      );
    }

    return nextUrl;
  };

  return {
    url,
    browserSession,
    obsController,
    obsProcess,
    stop,
    updateUrl,
  };
}

export function startGameReplaySession(
  input: Omit<StartStreamSessionOptions, "stream"> & {
    gameId: string;
    stream?: Omit<StreamRouteOptions, "target" | "replay">;
  },
) {
  return startStreamSession({
    ...input,
    stream: {
      ...(input.stream ?? {}),
      target: { type: "game", gameId: input.gameId },
      replay: true,
    },
  });
}

export function startTournamentReplaySession(
  input: Omit<StartStreamSessionOptions, "stream"> & {
    tournamentId: string;
    stream?: Omit<StreamRouteOptions, "target" | "replay">;
  },
) {
  return startStreamSession({
    ...input,
    stream: {
      ...(input.stream ?? {}),
      target: { type: "tournament", tournamentId: input.tournamentId },
      replay: true,
    },
  });
}

export function startAgentStreamSession(
  input: Omit<StartStreamSessionOptions, "stream"> & {
    handle: string;
    stream?: Omit<StreamRouteOptions, "target">;
  },
) {
  return startStreamSession({
    ...input,
    stream: {
      ...(input.stream ?? {}),
      target: { type: "agent", handle: input.handle },
    },
  });
}

export function startHumanStreamSession(
  input: Omit<StartStreamSessionOptions, "stream"> & {
    username: string;
    stream?: Omit<StreamRouteOptions, "target">;
  },
) {
  return startStreamSession({
    ...input,
    stream: {
      ...(input.stream ?? {}),
      target: { type: "human", username: input.username },
    },
  });
}
