#!/usr/bin/env python3
"""Test private session installation without registering a system login entry."""
import os
from pathlib import Path
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[1]

with tempfile.TemporaryDirectory(prefix="sway session test-") as directory:
    home = Path(directory)
    config_home = home / ".config"
    base = config_home / "sway/config"
    base.parent.mkdir(parents=True)
    base.write_text("output * bg #182238 solid_color\n")
    env = dict(os.environ, HOME=directory, XDG_CONFIG_HOME=str(config_home),
               XDG_STATE_HOME=str(home / "state"))
    command = [ROOT / "contrib/install-session", "--user-only"]
    subprocess.run(command, env=env, check=True)
    prefix = home / ".local/share/sway-rounded"
    launcher = home / ".local/bin/sway-rounded"
    config = config_home / "sway-rounded/config"
    original = base.read_bytes()
    config.write_text(config.read_text() + "# Preserve custom session settings.\n")
    custom = config.read_bytes()
    first = (prefix / "current").resolve()
    subprocess.run(command, env=env, check=True)
    second = (prefix / "current").resolve()
    assert second != first and first.is_dir()
    assert base.read_bytes() == original and config.read_bytes() == custom

    runtime_dir = home / "run"
    runtime_dir.mkdir(mode=0o700)
    validation_env = dict(env, XDG_RUNTIME_DIR=str(runtime_dir),
                          WLR_BACKENDS="headless", WLR_RENDERER="pixman")
    subprocess.run([second / "bin/sway", "--validate", "--config", config],
                   env=validation_env, check=True)

    for name in ("DISPLAY", "WAYLAND_DISPLAY", "WAYLAND_SOCKET"):
        guarded = dict(env)
        for key in ("DISPLAY", "WAYLAND_DISPLAY", "WAYLAND_SOCKET", "SWAYSOCK"):
            guarded.pop(key, None)
        guarded[name] = "active-session"
        result = subprocess.run([launcher], env=guarded, capture_output=True, text=True)
        assert result.returncode == 1 and "login screen" in result.stderr

    # Only the test snapshot is replaced: inspect the environment that the
    # launcher would give Sway without starting another compositor.
    fake = second / "build/sway/sway"
    fake.write_text('''#!/bin/sh
printf '%s\\n' "${SWAYSOCK-unset}" "${WLR_BACKENDS-unset}" "${LD_LIBRARY_PATH-unset}" "$WLR_XWAYLAND" "$@"
''')
    login_env = dict(env, SWAYSOCK="/tmp/stale-sway.sock", WLR_BACKENDS="headless")
    for key in ("DISPLAY", "WAYLAND_DISPLAY", "WAYLAND_SOCKET", "LD_LIBRARY_PATH"):
        login_env.pop(key, None)
    subprocess.run([launcher, "--validate"], env=login_env, check=True)
    log = next((home / "state/sway-rounded").glob("session-*.log")).read_text().splitlines()
    assert log[:3] == ["unset", "unset", "unset"]
    assert log[3] == str(second / "build-xwayland/hw/xwayland/Xwayland")
    assert log[4:] == ["--config", str(config), "--validate"]
    print("PASS: relocated runtime, preserved config and prior snapshot, desktop guard, stale GDM environment")
