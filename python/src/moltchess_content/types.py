from __future__ import annotations

from dataclasses import dataclass
from typing import Literal


TargetType = Literal["game", "tournament", "agent", "human", "all"]
WaitUntilState = Literal["load", "domcontentloaded", "networkidle", "commit"]


@dataclass(slots=True)
class StreamTarget:
    type: TargetType
    value: str | None = None


@dataclass(slots=True)
class StreamRoute:
    target: StreamTarget
    base_url: str = "https://moltchess.com"
    replay: bool = False
    timestep_seconds: float | None = None
    rotate_seconds: float | None = None


@dataclass(slots=True)
class BrowserLaunchOptions:
    headless: bool = True
    channel: str | None = None
    width: int = 1920
    height: int = 1080
    wait_until: WaitUntilState = "networkidle"
    ready_selector: str | None = None
    ready_timeout_ms: int = 30_000


@dataclass(slots=True)
class ObsConnectionOptions:
    address: str = "127.0.0.1"
    port: int = 4455
    password: str | None = None
    scene_name: str | None = None
    source_name: str | None = None
    browser_width: int = 1920
    browser_height: int = 1080
    auto_start_record: bool = False
    auto_start_stream: bool = False
    auto_stop_record: bool = False
    auto_stop_stream: bool = False


@dataclass(slots=True)
class ObsProcessOptions:
    use_xvfb: bool = True
    xvfb_command: str = "xvfb-run"
    xvfb_screen: str = "-screen 0 1920x1080x24"
    obs_command: str = "obs"
    obs_args: tuple[str, ...] = ("--minimize-to-tray", "--disable-shutdown-check")
    startup_delay_ms: int = 4000
