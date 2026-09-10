# sway

## Rounded-corner prototype

This fork is based on Sway 1.9 and uses the system wlroots
0.17 library. It adds opt-in `floating_corner_radius 20` configuration for
individual floating windows. Pixel borders follow the curve; tiled and
fullscreen windows, popups, and client-side decorations keep upstream behavior.
This first implementation uses pixel-aligned clipping, without antialiasing,
blur, or changes to wlroots.

On Ubuntu 24.04, install the build dependencies and build locally:

```sh
sudo apt install build-essential meson ninja-build pkg-config wayland-protocols \
  libwlroots-dev libpcre2-dev libjson-c-dev libpango1.0-dev libcairo2-dev \
  libgdk-pixbuf-2.0-dev libevdev-dev libinput-dev libxcb-ewmh-dev scdoc
meson setup build --prefix="$PWD/build-install" --sysconfdir=/etc
meson compile -C build
meson test -C build --print-errorlogs
```

Test it as a window inside an existing Wayland session, without installing it
or loading your normal Sway startup commands:

```sh
WLR_BACKENDS=wayland WLR_WL_OUTPUTS=1 build/sway/sway -c "$PWD/contrib/rounded-preview.conf"
```

Click inside the nested desktop and press F2 to open Ghostty, F3 to toggle
fullscreen, F4 to toggle floating, F5/F6 to disable/enable corners, and F12 to
exit the nested compositor. Ghostty must be installed for the F2 shortcut.
Changes through its IPC socket must use the nested instance's `SWAYSOCK`, not
the parent desktop's socket. Do not run `sudo ninja install` for this preview;
the installed `/usr/bin/sway` and your normal configuration need not change.

In nested testing on Ubuntu 24.04 with Ghostty 1.3.1, changing output scale and
rotation repeatedly can leave terminal content smaller than its window. This
also reproduces with unmodified Sway 1.9. Reopen the terminal after these display
experiments; normal rounded-corner toggles do not require reopening it.

**[English][en]** - [عربي][ar] - [Česky][cs] - [Deutsch][de] - [Dansk][dk] - [Español][es] - [Français][fr] - [ქართული][ge] - [Ελληνικά][gr] - [हिन्दी][hi] - [Magyar][hu] - [فارسی][ir] - [Italiano][it] - [日本語][ja] - [한국어][ko] - [Nederlands][nl] - [Norsk][no] - [Polski][pl] - [Português][pt] - [Română][ro] - [Русский][ru] - [Svenska][sv] - [Türkçe][tr] - [Українська][uk] - [中文-简体][zh-CN] - [中文-繁體][zh-TW]

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

    meson build/
    ninja -C build/
    sudo ninja -C build/ install

## Configuration

If you already use i3, then copy your i3 config to `~/.config/sway/config` and
it'll work out of the box. Otherwise, copy the sample configuration file to
`~/.config/sway/config`. It is usually located at `/etc/sway/config`.
Run `man 5 sway` for information on the configuration.

## Running

Run `sway` from a TTY. Some display managers may work but are not supported by
sway (gdm is known to work fairly well).

[en]: https://github.com/swaywm/sway#readme
[ar]: README.ar.md
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
