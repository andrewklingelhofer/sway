# sway

## Rounded-corner fork

This fork is based on **Sway 1.12** with a pinned private build of **wlroots
0.20.2**. `floating_corner_radius 20` rounds individual floating windows;
`tiled_corner_radius 20` rounds tiled windows without changing the layout.
Set either radius to 0 to disable it. Pixel borders follow the curve.
Fullscreen windows, floating groups, client-side decorations, and
popups retain their normal behavior. The first Sway 1.9 prototype is preserved
on the `prototype-1.9` branch.

The port uses a small wlroots scene-node clipping patch in
`patches/wlroots-scene-clip.patch`. The same clip governs rendering, occlusion,
and hit-testing; clipped nodes cannot bypass it through direct scanout.
This is pixel-aligned rounding, not antialiasing, blur, or Liquid Glass.

### Build on Ubuntu 24.04

```sh
sudo apt install build-essential meson ninja-build pkg-config libwlroots-dev \
  libpcre2-dev libjson-c-dev libpango1.0-dev libcairo2-dev libgdk-pixbuf-2.0-dev \
  libevdev-dev libinput-dev libxcb-ewmh-dev scdoc bison libffi-dev libexpat1-dev \
  libxml2-dev libwacom-dev foot grim python3-pil
contrib/build-preview
python3 tests/preview-smoke.py
```

The script checks pinned dependency revisions and applies the wlroots patch.
Libraries missing from Ubuntu's versions are built privately in `subprojects/`
and `build-deps/`. It does not install Sway or replace system libraries.
The system `libwlroots-dev` package above supplies base build dependencies;
the actual compositor links to the private, patched 0.20.2 build.

### Run the isolated preview

```sh
WLR_BACKENDS=wayland WLR_WL_OUTPUTS=1 build/sway/sway -c "$PWD/contrib/rounded-preview.conf"
```

The standalone config does not run your desktop startup commands. F2 opens
Ghostty, F3 toggles fullscreen, F4 toggles floating, F5/F6 disable/enable rounding,
and F12 exits the nested compositor. Ghostty is only needed for this visual
preview; the automated smoke test uses Foot in a headless software-rendered
session and never connects to your desktop's IPC socket.

This preview disables Xwayland: Ubuntu 24.04's Xwayland 23.2.6 is older than
the 24.1 compatibility threshold noted in Sway 1.10. The separate desktop
session below uses a private Xwayland build instead. Physical monitor/KVM
behavior and HDR still require a real login test.

The earlier Ghostty 1.3.1 content-resize issue remains reproducible after
changing the preview output's scale and rotation repeatedly. Reopen Ghostty
after such experiments. The automated Foot-based scaling and rotation tests
also check that the client continues filling its window.

### Separate login session

Build the compositor above, then build Xwayland 24.1.13 and install a separate
session without replacing the system Sway or Xwayland:

```sh
sudo apt install libepoxy-dev libxfont-dev libxkbfile-dev libxshmfence-dev \
  libxcvt-dev libtirpc-dev libunwind-dev libmd-dev mesa-common-dev xtrans-dev python3-gi
contrib/build-xwayland
contrib/install-session
```

The installer runs as your normal user and uses sudo only to register
`/usr/local/share/wayland-sessions/sway-rounded.desktop`. With `--user-only`,
it prepares everything and prints that final administrator command instead.

* `~/.local/share/sway-rounded/releases/` contains independent runtime snapshots,
  so rebuilding or switching Git branches cannot break the login entry.
* `~/.local/bin/sway-rounded` starts the selected snapshot. Private libraries
  use relative RUNPATHs, not a session-wide `LD_LIBRARY_PATH` override.
* `~/.config/sway-rounded/config` includes your existing Sway config and adds
  rounding and Xwayland support. Existing config files are not overwritten.
* Session logs go to `~/.local/state/sway-rounded/`.

The separate session's `appearance.conf` provides live corner-radius presets:
**Alt+Ctrl+0** disables rounding, **Alt+Ctrl+1** sets 10 pixels,
**Alt+Ctrl+2** sets 20 pixels, and **Alt+Ctrl+3** sets 30 pixels.
These affect both tiled and floating windows without reloading the config or
rerunning startup commands. Preset selections last until logout or a full
config reload; the radius settings in `config` remain the startup defaults.
Existing installations can include `~/.config/sway-rounded/appearance.conf`
from their separate session config. The installer preserves custom presets.

Save your work, log out, and choose **Sway Rounded (1.12)** in the login screen's
session selector. Choose **Sway** to return to the stock compositor. The
installer does not log you out, restart GDM, change auto-login, or select a
default session for you. The launcher refuses to run inside an existing
desktop because your normal startup commands may affect that session.

This is the same Linux account, not a VM or a separate profile. Files, folders,
installed apps, and their settings are shared and remain in place. Changes to
those shared settings affect both sessions. Rounded corners apply to both tiled and floating windows; your existing
tiling behavior is preserved.

**[English][en]** - [عربي][ar] - [Azərbaycanca][az] - [Česky][cs] - [Deutsch][de] - [Dansk][dk] - [Español][es] - [Français][fr] - [ქართული][ge] - [Ελληνικά][gr] - [हिन्दी][hi] - [Magyar][hu] - [فارسی][ir] - [Italiano][it] - [日本語][ja] - [한국어][ko] - [Nederlands][nl] - [Norsk][no] - [Polski][pl] - [Português][pt] - [Română][ro] - [Русский][ru] - [Српски][sr] - [Svenska][sv] - [Türkçe][tr] - [Українська][uk] - [中文-简体][zh-CN] - [中文-繁體][zh-TW]

sway is an [i3]-compatible [Wayland] compositor. Read the [FAQ]. Join the
[IRC channel] \(#sway on irc.libera.chat).

## Release Signatures

Releases are signed with [E88F5E48] and published [on GitHub][GitHub releases].

## Installation

### From Packages

Sway is available in many distributions. Try installing the "sway" package for
yours.

### Compiling from Source

Check out [this wiki page][Development setup] if you want to build the HEAD of
sway and wlroots for testing or development.

Install dependencies:

* meson \*
* [wlroots]
* wayland
* wayland-protocols \*
* pcre2
* json-c
* pango
* cairo
* gdk-pixbuf2 (optional: additional image formats for system tray)
* [swaybg] (optional: wallpaper)
* [scdoc] (optional: man pages) \*
* git (optional: version info) \*

_\* Compile-time dep_

Run these commands:

    meson setup build/
    ninja -C build/
    sudo ninja -C build/ install

## Configuration

If you already use i3, then copy your i3 config to `~/.config/sway/config` and
it'll work out of the box. Otherwise, copy the sample configuration file to
`~/.config/sway/config`. It is usually located at `/etc/sway/config`.
Run `man 5 sway` for information on the configuration.

## Running

Run `sway` from a TTY or from a display manager.

[en]: https://github.com/swaywm/sway#readme
[ar]: README.ar.md
[az]: README.az.md
[cs]: README.cs.md
[de]: README.de.md
[dk]: README.dk.md
[es]: README.es.md
[fr]: README.fr.md
[ge]: README.ge.md
[gr]: README.gr.md
[hi]: README.hi.md
[hu]: README.hu.md
[ir]: README.ir.md
[it]: README.it.md
[ja]: README.ja.md
[ko]: README.ko.md
[nl]: README.nl.md
[no]: README.no.md
[pl]: README.pl.md
[pt]: README.pt.md
[ro]: README.ro.md
[ru]: README.ru.md
[sr]: README.sr.md
[sv]: README.sv.md
[tr]: README.tr.md
[uk]: README.uk.md
[zh-CN]: README.zh-CN.md
[zh-TW]: README.zh-TW.md
[i3]: https://i3wm.org/
[Wayland]: http://wayland.freedesktop.org/
[FAQ]: https://github.com/swaywm/sway/wiki
[IRC channel]: https://web.libera.chat/gamja/?channels=#sway
[E88F5E48]: https://keys.openpgp.org/search?q=34FF9526CFEF0E97A340E2E40FDE7BE0E88F5E48
[GitHub releases]: https://github.com/swaywm/sway/releases
[Development setup]: https://github.com/swaywm/sway/wiki/Development-Setup
[wlroots]: https://gitlab.freedesktop.org/wlroots/wlroots
[swaybg]: https://github.com/swaywm/swaybg/
[scdoc]: https://git.sr.ht/~sircmpwn/scdoc
