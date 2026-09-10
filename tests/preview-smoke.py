#!/usr/bin/env python3
"""Exercise the built compositor in an isolated, software-rendered session."""
import json
import os
from pathlib import Path
import subprocess
import tempfile
import time

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]


def wait_for(predicate):
    deadline = time.monotonic() + 10
    while time.monotonic() < deadline:
        result = predicate()
        if result:
            return result
        time.sleep(0.05)
    raise AssertionError("Timed out waiting for the preview")


def nodes(tree):
    yield tree
    for child in tree.get("nodes", []) + tree.get("floating_nodes", []):
        yield from nodes(child)


with tempfile.TemporaryDirectory(prefix="sway-rounded-test-") as directory:
    runtime = Path(directory)
    env = {k: v for k, v in os.environ.items()
           if k not in ("DISPLAY", "WAYLAND_DISPLAY", "SWAYSOCK", "WAYLAND_SOCKET")}
    env.update(XDG_RUNTIME_DIR=directory, WLR_BACKENDS="headless",
               WLR_HEADLESS_OUTPUTS="1", WLR_RENDERER="pixman")
    config = runtime / "config"
    config.write_text("""
output * mode 800x600
output * bg #123456 solid_color
xwayland disable
floating_corner_radius 20
client.focused #789bb5 #151820 #e6edf3 #789bb5 #789bb5
for_window [app_id="rounded-test"] floating enable, border pixel 2, resize set width 500 px height 350 px, move position center
""")
    log = open(runtime / "sway.log", "w+")
    compositor = subprocess.Popen([ROOT / "build/sway/sway", "-c", config],
                                  env=env, stdout=log, stderr=log)
    client = None
    second_client = None
    try:
        sock = wait_for(lambda: next(runtime.glob("sway-ipc.*.sock"), None))
        display = wait_for(lambda: next((p for p in runtime.glob("wayland-*")
                                        if not p.name.endswith(".lock")), None))
        env.update(SWAYSOCK=str(sock), WAYLAND_DISPLAY=display.name)

        def ipc(*args):
            result = subprocess.run([ROOT / "build/swaymsg/swaymsg", "-s", sock,
                                     "-r", *args], env=env, text=True,
                                    capture_output=True)
            return json.loads(result.stdout)

        def command(text, success=True):
            result = ipc(text)
            assert result and all(item["success"] == success for item in result), (text, result)
            time.sleep(0.2)

        def window():
            return next((n for n in nodes(ipc("-t", "get_tree"))
                         if n.get("app_id") == "rounded-test"), None)

        def snapshot():
            target = runtime / "screenshot.png"
            subprocess.run(["grim", "-s", "1", target], env=env, check=True)
            return Image.open(target).convert("RGB")

        client = subprocess.Popen(["foot", "--app-id=rounded-test", "--",
                                   "sh", "-c", "printf 'Rounded corner regression test'; sleep 300"],
                                  env=env, stdout=log, stderr=log)
        wait_for(window)
        time.sleep(0.5)
        con = window()["id"]
        selector = f"[con_id={con}]"

        def check_shape():
            node = window()
            rect = node["rect"]
            x, y, w, h = (rect[k] for k in ("x", "y", "width", "height"))
            # The IPC rect excludes the normal titlebar.
            deco = node["deco_rect"]
            if deco["height"]:
                bottom = y + h
                y = min(y, deco["y"])
                h = bottom - y
            command(f"{selector} opacity 0")
            background = snapshot()
            command(f"{selector} opacity 1")
            rounded = snapshot()
            rounded.save(ROOT / "build/meson-logs/preview-rounded.png")
            background.save(ROOT / "build/meson-logs/preview-background.png")
            for point in ((x, y), (x+w-1, y), (x, y+h-1), (x+w-1, y+h-1)):
                assert rounded.getpixel(point) == background.getpixel(point), (point, window())
            assert rounded.getpixel((x+w//2, y)) != background.getpixel((x+w//2, y))
            assert rounded.getpixel((x+30, y+h-30)) != background.getpixel((x+30, y+h-30))
            return background, rounded

        background, rounded = check_shape()
        rect = window()["rect"]
        x, y = rect["x"], rect["y"]
        command("floating_corner_radius 0")
        square = snapshot()
        assert square.getpixel((x, y)) != background.getpixel((x, y))
        assert square.getpixel((x+50, y+100)) == rounded.getpixel((x+50, y+100))
        command("floating_corner_radius 20")
        for value in ("-1", "1001", "abc", "1.5", '""', "999999999999999999999999"):
            command("floating_corner_radius " + value, success=False)

        command(f"seat seat0 cursor set {x} {y}; seat seat0 cursor press button1; seat seat0 cursor release button1")
        assert not window()["focused"]
        command(f"{selector} focus")

        for style in ("none", "normal 2", "pixel 2"):
            print("Checking border style:", style, flush=True)
            command(f"{selector} border {style}")
            check_shape()

        for state in ("fullscreen enable", "fullscreen disable, floating disable"):
            command(f"{selector} {state}")
            before = snapshot()
            command("floating_corner_radius 0")
            after = snapshot()
            assert before.getpixel((1, 1)) == after.getpixel((1, 1))
            command("floating_corner_radius 20")

        command("tiled_corner_radius 20")
        for value in ("-1", "1001", "abc", "1.5"):
            command("tiled_corner_radius " + value, success=False)
        for style in ("none", "normal 2", "pixel 2"):
            command(f"{selector} border {style}")
            check_shape()
        command("gaps inner 10")
        command(f"{selector} focus, split h")
        second_client = subprocess.Popen(["foot", "--app-id=tiled-neighbor",
                                          "-o", "colors.background=445566", "--",
                                          "sh", "-c", "sleep 300"],
                                         env=env, stdout=log, stderr=log)
        wait_for(lambda: any(n.get("app_id") == "tiled-neighbor"
                             for n in nodes(ipc("-t", "get_tree"))))
        command(f"{selector} focus")
        assert window()["type"] == "con" and window()["rect"]["width"] < 500
        check_shape()
        command(f"{selector} resize grow width 40 px")
        check_shape()
        command(f"{selector} fullscreen enable")
        before = snapshot()
        command("tiled_corner_radius 0")
        assert list(before.getdata()) == list(snapshot().getdata())
        command("tiled_corner_radius 20")
        command(f"{selector} fullscreen disable")
        check_shape()

        command(f"{selector} floating enable, resize set width 500 px height 350 px, move position center")
        check_shape()
        command("output HEADLESS-1 scale 1.5")
        command(f"{selector} resize set width 320 px height 250 px, move position center")
        check_shape()
        command("output HEADLESS-1 transform 90")
        command(f"{selector} resize set width 250 px height 320 px, move position center")
        check_shape()
        command("output HEADLESS-1 transform normal")
        command("output HEADLESS-1 scale 1")
        command(f"{selector} resize set width 500 px height 350 px, move position center")
        background, _ = check_shape()
        command(f"{selector} move position 20 px 30 px")
        moved = snapshot()
        assert moved.getpixel((649, 250)) == background.getpixel((649, 250))
        check_shape()
        print("PASS: rounded pixels, border styles, toggling, invalid input, click-through, tiled/fullscreen transitions, fractional scale, rotation, move damage")
    except BaseException:
        log.flush()
        log.seek(0)
        print(log.read())
        raise
    finally:
        if second_client is not None:
            second_client.terminate()
            second_client.wait(timeout=10)
        if client is not None:
            client.terminate()
            client.wait(timeout=10)
        compositor.terminate()
        compositor.wait(timeout=10)
        log.close()
