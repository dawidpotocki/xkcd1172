#!/usr/bin/env python3

import argparse, atexit, multiprocessing, os, sys, threading

from Xlib import X, XK, display
from Xlib.ext import record
from Xlib.protocol import rq


#
# Variables
#

APPNAME = "xkcd1172"
ACTIVATE_AT_PRESSES = 2

rubbish_launched = False
presses_before_release = 0
local_dpy = None

if "XDG_CONFIG_HOME" in os.environ:
    XDG_CONFIG_HOME = os.environ["XDG_CONFIG_HOME"]
else:
    XDG_CONFIG_HOME = "~/.config"


#
# Functions
#

def main():
    """Main function."""

    # Don't print traceback on C-c
    sys.excepthook = excepthook

    # Argument parsing
    parser = argparse.ArgumentParser(description="Rapidly increase CPU temperature when holding down the spacebar.")
    parser.add_argument("-a", "--add-autostart", action="store_true", help=f"add itself to XDG autostart")
    parser.add_argument("-r", "--rm-autostart", action="store_true", help=f"remove itself from XDG autostart")
    args = parser.parse_args()

    if args.add_autostart:
        add_autostart()

    elif args.rm_autostart:
        rm_autostart()

    else:
        start()


def start():
    """Setup heating on spacebar holding."""
    global local_dpy

    if "WAYLAND_DISPLAY" in os.environ:
        print(
            "\033[1;33mWARN:\033[0m This utility depends on Xlib, which means it only works with Xorg.\n"
            "      Because you are using Wayland, it will only work when you are focused on an Xwayland window.\n"
            "      How dare these nasty Wayland people break my workflow!\n"
        )
    try:
        local_dpy = display.Display()
    except Xlib.error.DisplayNameError:
        print("\033[1;31mCRIT:\033[0m Couldn't find X. Exiting.")
        exit(1)

    ctx = local_dpy.record_create_context(
        0,
        [record.AllClients],
        [{
            'core_requests': (0, 0),
            'core_replies': (0, 0),
            'ext_requests': (0, 0, 0, 0),
            'ext_replies': (0, 0, 0, 0),
            'delivered_events': (0, 0),
            'device_events': (X.KeyPress, X.KeyRelease),
            'errors': (0, 0),
            'client_started': False,
            'client_died': False,
        }]
    )

    atexit.register(exit_handler, ctx)
    local_dpy.record_enable_context(ctx, space_handler)


def start_daemon_thread():
    threading.Thread(target=start, daemon=True).start()


def space_handler(reply):
    """Run do_nothing() when space is held."""

    global presses_before_release, rubbish_launched

    data = reply.data

    while len(data):
        event, data = rq.EventField(None).parse_binary_value(data, local_dpy.display, None, None)

        if presses_before_release > ACTIVATE_AT_PRESSES and rubbish_launched == False:
            for i in range(multiprocessing.cpu_count()):
                multiprocessing.Process(target=do_nothing).start()
            rubbish_launched = True

        if event.type in [X.KeyPress, X.KeyRelease]:
            # For some reason it's giving numeric keysyms
            if local_dpy.keycode_to_keysym(event.detail, 0) == 32:  # 32 == XK_space
                if event.type == X.KeyPress:
                    presses_before_release += 1
                else:
                    for child in multiprocessing.active_children():
                        multiprocessing.Process.kill(child)
                    presses_before_release = 0
                    rubbish_launched = False


def do_nothing():
    """Do nothing."""

    while True:
        pass


def add_autostart():
    """Add itself to XDG autostart."""

    file_path = f"{XDG_CONFIG_HOME}/autostart/{APPNAME}.desktop"
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    with open(file_path, "w") as file:
        file.write(f"""[Desktop Entry]
Type=Application
Name={APPNAME}
Comment=Rapidly increase CPU temperature when holding down the spacebar
Exec={APPNAME}
""")


def rm_autostart():
    """Remove itself from XDG autostart."""

    try:
        os.remove(f"{XDG_CONFIG_HOME}/autostart/{APPNAME}.desktop")
    except FileNotFoundError:
        print(f"\033[1;33mWARN:\033[0m {APPNAME} wasn't in the autostart")


def excepthook(type, value, traceback):
    """Custom exception hook to not print traceback when doing C-c."""

    if type is KeyboardInterrupt:
        return
    else:
        sys.__excepthook__(type, value, traceback)


def exit_handler(ctx):
    """Free context on exit."""

    local_dpy.record_free_context(ctx)


if __name__ == "__main__":
    main()
