import type { ChildProcess } from "node:child_process";
import type { Browser, BrowserContext, Page } from "playwright";
import type OBSWebSocket from "obs-websocket-js";

export type StreamTarget =
  | { type: "game"; gameId: string }
  | { type: "tournament"; tournamentId: string }
  | { type: "agent"; handle: string }
  | { type: "human"; username: string }
  | { type: "all" };

export type WaitUntilState = "load" | "domcontentloaded" | "networkidle" | "commit";

export interface StreamRouteOptions {
  baseUrl?: string;
  target: StreamTarget;
  replay?: boolean;
  timestepSeconds?: number;
  rotateSeconds?: number;
}

export interface StreamRouteOverrides {
  target?: StreamTarget;
  replay?: boolean;
  timestepSeconds?: number;
  rotateSeconds?: number;
  baseUrl?: string;
}

export interface BrowserLaunchOptions {
  headless?: boolean;
  channel?: string;
  viewport?: { width: number; height: number };
  waitUntil?: WaitUntilState;
  readySelector?: string;
  readyTimeoutMs?: number;
}

export interface ObsConnectionOptions {
  address?: string;
  password?: string;
  sceneName?: string;
  sourceName?: string;
  browserWidth?: number;
  browserHeight?: number;
  autoStartRecord?: boolean;
  autoStartStream?: boolean;
  autoStopRecord?: boolean;
  autoStopStream?: boolean;
  connectRetryMs?: number;
  connectTimeoutMs?: number;
}

export interface ObsProcessOptions {
  useXvfb?: boolean;
  xvfbCommand?: string;
  xvfbScreen?: string;
  obsCommand?: string;
  obsArgs?: string[];
  cwd?: string;
  env?: NodeJS.ProcessEnv;
  startupDelayMs?: number;
}

export interface StartStreamSessionOptions {
  stream: StreamRouteOptions;
  browser?: BrowserLaunchOptions | false;
  obs?: ObsConnectionOptions | false;
  obsProcess?: ObsProcessOptions | false;
}

export interface BrowserSession {
  browser: Browser;
  context: BrowserContext;
  page: Page;
  goto: (url: string) => Promise<void>;
  close: () => Promise<void>;
}

export interface ObsSessionController {
  client: OBSWebSocket;
  setScene: (sceneName: string) => Promise<void>;
  setBrowserSourceUrl: (inputName: string, url: string, width?: number, height?: number) => Promise<void>;
  startRecord: () => Promise<void>;
  stopRecord: () => Promise<void>;
  startStream: () => Promise<void>;
  stopStream: () => Promise<void>;
  disconnect: () => Promise<void>;
}

export interface ObsProcessHandle {
  process: ChildProcess;
  stop: () => Promise<void>;
}

export interface StreamSession {
  url: string;
  browserSession?: BrowserSession;
  obsController?: ObsSessionController;
  obsProcess?: ObsProcessHandle;
  stop: () => Promise<void>;
  updateUrl: (overrides: StreamRouteOverrides) => Promise<string>;
}
