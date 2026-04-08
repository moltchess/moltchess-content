from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any

from .browser import BrowserSession, start_browser_session
from .obs import ObsController, ObsProcessHandle, connect_obs, launch_obs_process
from .types import BrowserLaunchOptions, ObsConnectionOptions, ObsProcessOptions, StreamRoute, StreamTarget
from .url import build_stream_url


def _route_from_mapping(stream: Mapping[str, Any]) -> StreamRoute:
    target = stream["target"]
    if isinstance(target, StreamTarget):
        target_value = target
    else:
        target_type = target["type"]
        target_value = StreamTarget(type=target_type, value=target.get("value"))

    return StreamRoute(
        target=target_value,
        base_url=stream.get("base_url", "https://moltchess.com"),
        replay=stream.get("replay", False),
        timestep_seconds=stream.get("timestep_seconds"),
        rotate_seconds=stream.get("rotate_seconds"),
    )


def _browser_from_mapping(browser: Mapping[str, Any]) -> BrowserLaunchOptions:
    return BrowserLaunchOptions(
        headless=browser.get("headless", True),
        channel=browser.get("channel"),
        width=browser.get("width", 1920),
        height=browser.get("height", 1080),
        wait_until=browser.get("wait_until", "networkidle"),
        ready_selector=browser.get("ready_selector"),
        ready_timeout_ms=browser.get("ready_timeout_ms", 30000),
    )


def _obs_from_mapping(obs: Mapping[str, Any]) -> ObsConnectionOptions:
    return ObsConnectionOptions(
        address=obs.get("address", "127.0.0.1"),
        port=obs.get("port", 4455),
        password=obs.get("password"),
        scene_name=obs.get("scene_name"),
        source_name=obs.get("source_name"),
        browser_width=obs.get("browser_width", 1920),
        browser_height=obs.get("browser_height", 1080),
        auto_start_record=obs.get("auto_start_record", False),
        auto_start_stream=obs.get("auto_start_stream", False),
        auto_stop_record=obs.get("auto_stop_record", False),
        auto_stop_stream=obs.get("auto_stop_stream", False),
    )


def _obs_process_from_mapping(obs_process: Mapping[str, Any]) -> ObsProcessOptions:
    return ObsProcessOptions(
        use_xvfb=obs_process.get("use_xvfb", True),
        xvfb_command=obs_process.get("xvfb_command", "xvfb-run"),
        xvfb_screen=obs_process.get("xvfb_screen", "-screen 0 1920x1080x24"),
        obs_command=obs_process.get("obs_command", "obs"),
        obs_args=tuple(obs_process.get("obs_args", ("--minimize-to-tray", "--disable-shutdown-check"))),
        startup_delay_ms=obs_process.get("startup_delay_ms", 4000),
    )


@dataclass(slots=True)
class StreamSession:
    route: StreamRoute
    url: str
    browser_session: BrowserSession | None = None
    obs_controller: ObsController | None = None
    obs_process: ObsProcessHandle | None = None
    obs_options: ObsConnectionOptions | None = None

    def stop(self) -> None:
        if self.obs_controller and self.obs_options:
            if self.obs_options.auto_stop_record:
                self.obs_controller.stop_record()
            if self.obs_options.auto_stop_stream:
                self.obs_controller.stop_stream()
        if self.browser_session:
            self.browser_session.stop()
        if self.obs_process:
            self.obs_process.stop()

    def update_url(self, **overrides: Any) -> str:
        for key, value in overrides.items():
            setattr(self.route, key, value)
        next_url = build_stream_url(self.route)
        self.url = next_url
        if self.browser_session:
            self.browser_session.goto(next_url)
        if self.obs_controller and self.obs_options and self.obs_options.source_name:
            self.obs_controller.set_browser_source_url(
                self.obs_options.source_name,
                next_url,
                self.obs_options.browser_width,
                self.obs_options.browser_height,
            )
        return next_url


def start_stream_session(
    *,
    stream: Mapping[str, Any],
    browser: Mapping[str, Any] | bool | None = None,
    obs: Mapping[str, Any] | bool | None = None,
    obs_process: Mapping[str, Any] | bool | None = None,
) -> StreamSession:
    route = _route_from_mapping(stream)
    url = build_stream_url(route)

    obs_process_handle = None
    if obs_process and obs_process is not False:
        obs_process_handle = launch_obs_process(_obs_process_from_mapping(obs_process))

    obs_options = _obs_from_mapping(obs) if obs and obs is not False else None
    obs_controller = connect_obs(obs_options) if obs_options else None
    browser_session = None if browser is False else start_browser_session(url, _browser_from_mapping(browser or {}))

    if obs_controller and obs_options:
        if obs_options.scene_name:
            obs_controller.set_scene(obs_options.scene_name)
        if obs_options.source_name:
            obs_controller.set_browser_source_url(
                obs_options.source_name,
                url,
                obs_options.browser_width,
                obs_options.browser_height,
            )
        if obs_options.auto_start_record:
            obs_controller.start_record()
        if obs_options.auto_start_stream:
            obs_controller.start_stream()

    return StreamSession(
        route=route,
        url=url,
        browser_session=browser_session,
        obs_controller=obs_controller,
        obs_process=obs_process_handle,
        obs_options=obs_options,
    )


def start_game_replay_session(*, game_id: str, **kwargs: Any) -> StreamSession:
    stream = dict(kwargs.pop("stream", {}))
    stream["target"] = {"type": "game", "value": game_id}
    stream["replay"] = True
    return start_stream_session(stream=stream, **kwargs)


def start_tournament_replay_session(*, tournament_id: str, **kwargs: Any) -> StreamSession:
    stream = dict(kwargs.pop("stream", {}))
    stream["target"] = {"type": "tournament", "value": tournament_id}
    stream["replay"] = True
    return start_stream_session(stream=stream, **kwargs)


def start_agent_stream_session(*, handle: str, **kwargs: Any) -> StreamSession:
    stream = dict(kwargs.pop("stream", {}))
    stream["target"] = {"type": "agent", "value": handle}
    return start_stream_session(stream=stream, **kwargs)


def start_human_stream_session(*, username: str, **kwargs: Any) -> StreamSession:
    stream = dict(kwargs.pop("stream", {}))
    stream["target"] = {"type": "human", "value": username}
    return start_stream_session(stream=stream, **kwargs)
