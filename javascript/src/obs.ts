import { spawn } from "node:child_process";
import { setTimeout as delay } from "node:timers/promises";
import OBSWebSocket from "obs-websocket-js";
import type { ObsConnectionOptions, ObsProcessHandle, ObsProcessOptions, ObsSessionController } from "./types.js";

async function stopObsActionSafely(action: () => Promise<unknown>) {
  try {
    await action();
  } catch {
    // OBS may already be stopped or idle.
  }
}

export async function launchObsProcess(options: ObsProcessOptions = {}): Promise<ObsProcessHandle> {
  const obsCommand = options.obsCommand ?? "obs";
  const obsArgs = options.obsArgs ?? ["--minimize-to-tray", "--disable-shutdown-check"];
  const useXvfb = options.useXvfb ?? true;
  const command = useXvfb ? options.xvfbCommand ?? "xvfb-run" : obsCommand;
  const args = useXvfb
    ? ["-a", "-s", options.xvfbScreen ?? "-screen 0 1920x1080x24", obsCommand, ...obsArgs]
    : obsArgs;

  const childProcess = spawn(command, args, {
    cwd: options.cwd,
    env: options.env ?? globalThis.process.env,
    stdio: "ignore",
  });

  await delay(options.startupDelayMs ?? 4_000);

  return {
    process: childProcess,
    stop: async () => {
      if (childProcess.killed || childProcess.exitCode != null) return;
      childProcess.kill("SIGTERM");
      await delay(1_000);
      if (childProcess.exitCode == null) {
        childProcess.kill("SIGKILL");
      }
    },
  };
}

export async function connectObs(options: ObsConnectionOptions = {}): Promise<ObsSessionController> {
  const client = new OBSWebSocket();
  const address = options.address ?? "ws://127.0.0.1:4455";
  const retryMs = options.connectRetryMs ?? 1_000;
  const timeoutMs = options.connectTimeoutMs ?? 30_000;
  const startedAt = Date.now();

  while (true) {
    try {
      await client.connect(address, options.password);
      break;
    } catch (error) {
      if (Date.now() - startedAt >= timeoutMs) {
        throw error;
      }
      await delay(retryMs);
    }
  }

  return {
    client,
    setScene: async (sceneName: string) => {
      await client.call("SetCurrentProgramScene", { sceneName });
    },
    setBrowserSourceUrl: async (inputName: string, url: string, width = 1920, height = 1080) => {
      await client.call("SetInputSettings", {
        inputName,
        inputSettings: {
          url,
          width,
          height,
        },
        overlay: true,
      });
    },
    startRecord: async () => {
      await client.call("StartRecord");
    },
    stopRecord: async () => {
      await stopObsActionSafely(() => client.call("StopRecord"));
    },
    startStream: async () => {
      await client.call("StartStream");
    },
    stopStream: async () => {
      await stopObsActionSafely(() => client.call("StopStream"));
    },
    disconnect: async () => {
      await client.disconnect();
    },
  };
}
