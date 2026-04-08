from __future__ import annotations

import subprocess
import time
from dataclasses import dataclass

from obsws_python import ReqClient

from .types import ObsConnectionOptions, ObsProcessOptions


@dataclass(slots=True)
class ObsProcessHandle:
    process: subprocess.Popen[bytes]

    def stop(self) -> None:
        if self.process.poll() is not None:
            return
        self.process.terminate()
        try:
            self.process.wait(timeout=1)
        except subprocess.TimeoutExpired:
            self.process.kill()
            self.process.wait(timeout=1)


@dataclass(slots=True)
class ObsController:
    client: ReqClient

    def set_scene(self, scene_name: str) -> None:
        self.client.set_current_program_scene(scene_name)

    def set_browser_source_url(self, input_name: str, url: str, width: int = 1920, height: int = 1080) -> None:
        self.client.set_input_settings(
            input_name,
            {
                "url": url,
                "width": width,
                "height": height,
            },
            True,
        )

    def start_record(self) -> None:
        self.client.start_record()

    def stop_record(self) -> None:
        try:
            self.client.stop_record()
        except Exception:
            pass

    def start_stream(self) -> None:
        self.client.start_stream()

    def stop_stream(self) -> None:
        try:
            self.client.stop_stream()
        except Exception:
            pass


def launch_obs_process(options: ObsProcessOptions | None = None) -> ObsProcessHandle:
    config = options or ObsProcessOptions()
    if config.use_xvfb:
        command = [
            config.xvfb_command,
            "-a",
            "-s",
            config.xvfb_screen,
            config.obs_command,
            *config.obs_args,
        ]
    else:
        command = [config.obs_command, *config.obs_args]

    process = subprocess.Popen(command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    time.sleep(config.startup_delay_ms / 1000)
    return ObsProcessHandle(process=process)


def connect_obs(options: ObsConnectionOptions | None = None) -> ObsController:
    config = options or ObsConnectionOptions()
    client = ReqClient(
        host=config.address,
        port=config.port,
        password=config.password or "",
    )
    return ObsController(client=client)
