#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""KittyProtocol marketplace entry point."""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
from pathlib import Path


def _extension_base() -> Path:
    base = globals().get("__extension_base__")
    if base:
        return Path(base)
    return Path(__file__).resolve().parent.parent


def setup_paths() -> None:
    from core.utils.marketplace_apps import framework_root

    ext_base = _extension_base()
    root = framework_root()
    for path in (root, ext_base, ext_base / "src"):
        path_str = str(path)
        if path.exists() and path_str not in sys.path:
            sys.path.insert(0, path_str)


def _is_admin() -> bool:
    if os.name == "nt":
        try:
            import ctypes

            return bool(ctypes.windll.shell32.IsUserAnAdmin())
        except Exception:
            return False
    try:
        return os.geteuid() == 0
    except Exception:
        return False


def _relaunch_as_admin() -> None:
    marker = "KITTYPROTOCOL_ELEVATION_ATTEMPTED"
    if os.environ.get(marker) == "1":
        return

    if os.name == "nt":
        try:
            import ctypes

            params = " ".join(f'"{arg}"' for arg in sys.argv)
            rc = ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, params, None, 1)
            if int(rc) <= 32:
                print("[!] Unable to elevate to Administrator mode.")
                return
            raise SystemExit(0)
        except Exception:
            print("[!] Unable to elevate to Administrator mode.")
            return

    sudo_bin = shutil.which("sudo")
    if not sudo_bin:
        print("[!] KittyProtocol requires root. Install sudo or use: sudo python launch_kittyprotocol.py")
        return

    env = dict(os.environ)
    env[marker] = "1"
    print("[*] KittyProtocol requires root privileges. Sudo password required.")
    rc = subprocess.call([sudo_bin, sys.executable] + sys.argv, env=env)
    raise SystemExit(rc)


def main() -> None:
    setup_paths()
    if not _is_admin():
        _relaunch_as_admin()
    from kittyprotocol import main as run_protocol

    run_protocol()


if __name__ == "__main__":
    main()
