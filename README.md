# xkcd1172

Rapidly increases CPU temperature when holding down the spacebar.

***https://xkcd.com/1172***

![xkcd 1172: Workflow](https://imgs.xkcd.com/comics/workflow.png)

## Installation

```sh
$ pip3 install xkcd1172
```

### Requirements

- Xorg (Wayland works if you are focused on an Xwayland window)
- Spacebar
- CPU

## Building

```sh
$ git clone https://git.dawidpotocki.com/dawid/xkcd1172
$ cd xkcd1172

$ python3 -m build
$ pip3 install dist/xkcd1172-<version>-py3-none-any.whl
```

## Running standalone

```sh
$ xkcd1172
```

### Autostart

```sh
$ xkcd1172 -a  # Add to XDG autostart
$ xkcd1172 -r  # Remove from XDG autostart
```

## Running as a library

```py
import xkcd1172

xkcd1172.start_daemon_thread()
```
