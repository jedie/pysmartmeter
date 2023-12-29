# pysmartmeter

[![tests](https://github.com/jedie/pysmartmeter/actions/workflows/tests.yml/badge.svg?branch=main)](https://github.com/jedie/pysmartmeter/actions/workflows/tests.yml)
[![codecov](https://codecov.io/github/jedie/pysmartmeter/branch/main/graph/badge.svg)](https://app.codecov.io/github/jedie/pysmartmeter)
[![pysmartmeter @ PyPi](https://img.shields.io/pypi/v/pysmartmeter?label=pysmartmeter%20%40%20PyPi)](https://pypi.org/project/pysmartmeter/)
[![Python Versions](https://img.shields.io/pypi/pyversions/pysmartmeter)](https://github.com/jedie/pysmartmeter/blob/main/pyproject.toml)
[![License GPL-3.0-or-later](https://img.shields.io/pypi/l/pysmartmeter)](https://github.com/jedie/pysmartmeter/blob/main/LICENSE)


Collect data from Hichi Smartmeter aka `volkszaehler.org` (USB Version) and expose it via MQTT.

Discussion: https://www.photovoltaikforum.com/thread/188160-pysmartmeter (de)

In the end it can looks like the following [Home Assistant](https://www.home-assistant.io/) dashboard screenshot, using [MQTT integration](https://www.home-assistant.io/integrations/mqtt):

![2023-02-26_17-39.png](https://raw.githubusercontent.com/jedie/jedie.github.io/master/screenshots/pysmartmeter/2023-02-26_17-39.png "2023-02-26_17-39.png")

With my "eBZ DD3" energy meter by eBZ GmbH the values update live every second ;)


Currently only energy meters that send [OBIS text protocol](https://wiki.volkszaehler.org/software/obis) are supported! (Test this with `./cli.py dump`)

TODO: [#37 - Add support for SML (Smart Message Language) binary protocol](https://github.com/jedie/pysmartmeter/issues/37)


## quickstart

Install minimum requirements, e.g.:
```bash
~$ sudo apt install python3-venv
```

Clone sources and install project:
```bash
~$ git clone https://github.com/jedie/pysmartmeter.git
~$ cd pysmartmeter
~/pysmartmeter$ ./cli.py --help
```

The output of `./cli.py --help` looks like:

[comment]: <> (✂✂✂ auto generated main help start ✂✂✂)
```
Usage: ./cli.py [OPTIONS] COMMAND [ARGS]...

╭─ Options ────────────────────────────────────────────────────────────────────────────────────────╮
│ --help      Show this message and exit.                                                          │
╰──────────────────────────────────────────────────────────────────────────────────────────────────╯
╭─ Commands ───────────────────────────────────────────────────────────────────────────────────────╮
│ debug-settings               Display (anonymized) MQTT server username and password              │
│ debug-systemd-service        Just print the systemd service file content                         │
│ detect-serial                Just print the detected serial port instance                        │
│ dump                         Just dump serial output                                             │
│ publish-loop                 Publish current data via MQTT (endless loop)                        │
│ setup-systemd-service        Setup PySmartMeter systemd services and starts it.                  │
│ store-settings               Store MQTT server settings.                                         │
│ systemd-restart              Restart PySmartMeter systemd services                               │
│ systemd-status               Call systemd status of PySmartMeter services                        │
│ systemd-stop                 Stop PySmartMeter systemd services                                  │
│ test-mqtt-connection         Test connection to MQTT Server                                      │
│ version                      Print version and exit                                              │
╰──────────────────────────────────────────────────────────────────────────────────────────────────╯
```
[comment]: <> (✂✂✂ auto generated main help end ✂✂✂)

Test if you Hichi Smartmeter with CP2102 USB to UART Bridge Controller will be found, e.g.:
```bash
~/pysmartmeter$ ./cli.py detect-serial
```

Maybe you didn't have permissions to access the port, e.g.:
```bash
~/pysmartmeter$ ./cli.py dump
...
try: /dev/ttyUSB0 CP2102 USB to UART Bridge Controller - CP2102 USB to UART Bridge Controller USB VID:PID=10C4:EA60
/dev/ttyUSB0 file mode: 0o20660
/dev/ttyUSB0 user ID: 0
/dev/ttyUSB0 user group ID: 20
/dev/ttyUSB0 user group: 'dialout'
ERROR: [Errno 13] could not open port /dev/ttyUSB0: [Errno 13] Permission denied: '/dev/ttyUSB0'
...
```

Fix fiy by add the user to the group, e.g.:
```bash
sudo usermod -a -G dialout $USER
```

## publish smartmeter data via MQTT

You have to store your MQTT settings (host, port, username, password) one time, e.g.:
```bash
~/pysmartmeter$ ./cli.py store-settings
```
This will create a JSON file here: `~/.pysmartmeter`

You can test reading this settings file with:
```bash
~/pysmartmeter$ ./cli.py debug-settings
```

Test your MQTT settings with:
```bash
~/pysmartmeter$ ./cli.py test-mqtt-connection
```

Setup systemd service:
```bash
~/pysmartmeter$ sudo ./cli.py setup-systemd-service
```
This will create a systemd service that automaticly starts on every boot.

Note: Before you start the systemd service, check if everything works correctly with `./cli.py dump` and `./cli.py publish-loop` 
Otherwise you may start a services that will just deal wie gabage (e.g.: your energy meters speaks no OBIS text protocol) and restarts on and on again ;)


Check if service is running:
```bash
~/pysmartmeter$ sudo ./cli.py systemd-status
```

If everything is fine: Go to your [Home Assistant and check the MQTT integration](https://www.home-assistant.io/integrations/mqtt/)
The device discovery will be made automaticly.


# Start hacking

```bash
~$ git clone https://github.com/jedie/pysmartmeter.git
~$ cd pysmartmeter
~/pysmartmeter$ ./dev-cli.py --help
```


[comment]: <> (✂✂✂ auto generated dev help start ✂✂✂)
```
Usage: ./dev-cli.py [OPTIONS] COMMAND [ARGS]...

╭─ Options ────────────────────────────────────────────────────────────────────────────────────────╮
│ --help      Show this message and exit.                                                          │
╰──────────────────────────────────────────────────────────────────────────────────────────────────╯
╭─ Commands ───────────────────────────────────────────────────────────────────────────────────────╮
│ check-code-style            Check code style by calling darker + flake8                          │
│ coverage                    Run tests and show coverage report.                                  │
│ fix-code-style              Fix code style of all pysmartmeter source code files via darker      │
│ install                     Run pip-sync and install 'pysmartmeter' via pip as editable.         │
│ mypy                        Run Mypy (configured in pyproject.toml)                              │
│ publish                     Build and upload this project to PyPi                                │
│ safety                      Run safety check against current requirements files                  │
│ test                        Run unittests                                                        │
│ tox                         Run tox                                                              │
│ update                      Update "requirements*.txt" dependencies files                        │
│ update-test-snapshot-files  Update all test snapshot files (by remove and recreate all snapshot  │
│                             files)                                                               │
│ version                     Print version and exit                                               │
╰──────────────────────────────────────────────────────────────────────────────────────────────────╯
```
[comment]: <> (✂✂✂ auto generated dev help end ✂✂✂)


# Backwards-incompatible changes

## v0.4.x -> v0.5.x

We split the CLI files into:

* `./cli.py` - Commands for end users
* `./dev-cli.py` - Commands for developers

## v0.2.x -> v0.3.x

Packages changes:

* We switched from `poetry` to `pip-tools`
* `Makefile` was removed
* "Renamed" `cli.sh` to `cli.py`

The `Makefile` is no longer needed, because "Bootstrapping" will be made, just by call `cli.py`

To migrate, just remove the existing `.venv` and create a fresh one, e.g.:
```bash
~$ cd pysmartmeter
~/pysmartmeter$ git pull origin main
~/pysmartmeter$ rm -Rf .venv
~/pysmartmeter$ ./cli.py --help
```


# various links

* Discussion: https://www.photovoltaikforum.com/thread/188160-pysmartmeter (de)
* https://github.com/pyserial/pyserial
* https://github.com/eclipse/paho.mqtt.python
* https://github.com/eclipse/mosquitto
* https://dewiki.de/Lexikon/OBIS-Kennzahlen (de) | https://www.promotic.eu/en/pmdoc/Subsystems/Comm/PmDrivers/IEC62056_OBIS.htm (en)
* https://www.photovoltaikforum.com/thread/145886-habe-lesk%C3%B6pfe-mit-usb-%C3%BCber/ (de)
* https://www.heise.de/tests/Ausprobiert-Guenstiger-IR-Lesekopf-fuer-Smart-Meter-mit-Tastmota-Firmware-7065559.html (de)
* https://www.home-assistant.io
