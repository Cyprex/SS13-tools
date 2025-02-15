# SS13 tools

[![PyLint](https://github.com/RigglePrime/SS13-tools/actions/workflows/pylint.yml/badge.svg)](https://github.com/RigglePrime/SS13-tools/actions/workflows/pylint.yml)
[![Flake8](https://github.com/RigglePrime/SS13-tools/actions/workflows/flake8-lint.yml/badge.svg)](https://github.com/RigglePrime/SS13-tools/actions/workflows/flake8-lint.yml)
[![Build](https://github.com/RigglePrime/SS13-tools/actions/workflows/publish.yml/badge.svg)](https://github.com/RigglePrime/SS13-tools/actions/workflows/publish.yml)

A set of tools to help with automating tasks for the /tg/ branch of SS13.

If you're looking for LogBuddy help, click [here](./ss13_tools/log_buddy/README.md)

Made for Python 3.9+

## How to run

`pip install ss13-tools; ss13tools` (pip3 on Linux) or dowload the executable [here](https://github.com/RigglePrime/SS13-tools/releases/latest) (Windows only).
If the latter is giving you trouble, try the former. Python can be installed [here](https://www.python.org/downloads/)

Remember, if you ever screw an input up try pressing the up arrow.

## Contents

- Root script that displays all options: `ss13tools`
- auth: authenticate and download from raw logs
- byond: tools for working with BYOND, such as checking if a ckey exists
- [centcom](https://centcom.melonmesa.com/), comes as a script `centcom`
- log_downloader: downloads logs from tg's [parsed logs](https://tgstation13.org/parsed-logs)
- [LogBuddy](./ss13_tools/log_buddy/README.md), comes as a script `logbuddy`
- scrubby: scrubby tools
- slur_detector: what it says on the tin

For examples on how to use please see [this file](ss13_tools/menu.py)

## Downloading

For compiled versions, see [this link](https://github.com/RigglePrime/admin-tools/releases).

If the above link is giving you trouble, try installing it with `pip`.

1. Download python from [here](https://www.python.org/downloads/)
2. Install, make sure to check "add to environment variables" or "add to PATH", and use `py` launcher
3. Run `pip install ss13-tools`. If this is giving you trouble, try logging out and back in.
4. Run `ss13tools` or `logbuddy` directly

Now also available on [PyPi](https://pypi.org/project/ss13-tools/)!

If you know your way around python, you may try using [PyPy](https://www.pypy.org/) for faster performance.
