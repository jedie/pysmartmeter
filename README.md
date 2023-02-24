# pysmartmeter

Collect data from Hichi Smartmeter aka `volkszaehler.org` (USB Version) and expose it via MQTT.
[![tests](https://github.com/jedie/pysmartmeter/actions/workflows/tests.yml/badge.svg?branch=main)](https://github.com/jedie/pysmartmeter/actions/workflows/tests.yml)
[![codecov](https://codecov.io/github/jedie/pysmartmeter/branch/main/graph/badge.svg)](https://codecov.io/github/jedie/pysmartmeter)
[![pysmartmeter @ PyPi](https://img.shields.io/pypi/v/pysmartmeter?label=pysmartmeter%20%40%20PyPi)](https://pypi.org/project/pysmartmeter/)
[![Python Versions](https://img.shields.io/pypi/pyversions/pysmartmeter)](https://github.com/jedie/pysmartmeter/blob/main/pyproject.toml)
[![License GPL-3.0-or-later](https://img.shields.io/pypi/l/pysmartmeter)](https://github.com/jedie/pysmartmeter/blob/main/LICENSE)

In the end it can looks like the following [Home Assistant](https://www.home-assistant.io/) dashboard screenshot, using [MQTT integration](https://www.home-assistant.io/integrations/mqtt):

![2022-11-21_13-47.png](https://raw.githubusercontent.com/jedie/jedie.github.io/master/screenshots/pysmartmeter/2022-11-21_13-47.png "2022-11-21_13-47.png")

With my "eBZ DD3" energy meterby eBZ GmbH the values update live every second ;)


## quickstart

Install minimum requirements, e.g.:
```bash
~$ sudo apt install make python3-venv
```

Clone sources and install project:
```bash
~$ git clone https://github.com/jedie/pysmartmeter.git
~$ cd pysmartmeter
~/pysmartmeter$ make install-poetry
~/pysmartmeter$ make install
~/pysmartmeter$ ./cli.sh --help
+ exec .venv/bin/python -m pysmartmeter --help
PySmartMeter v0.1.0

 Usage: python -m pysmartmeter [OPTIONS] COMMAND [ARGS]...

╭─ Options ─────────────────────────────────────────────────────────────────────────────────────────╮
│ --install-completion        [bash|zsh|fish|powershell|pwsh]  Install completion for the specified │
│                                                              shell.                               │
│                                                              [default: None]                      │
│ --show-completion           [bash|zsh|fish|powershell|pwsh]  Show completion for the specified    │
│                                                              shell, to copy it or customize the   │
│                                                              installation.                        │
│                                                              [default: None]                      │
│ --help                                                       Show this message and exit.          │
╰───────────────────────────────────────────────────────────────────────────────────────────────────╯
╭─ Commands ────────────────────────────────────────────────────────────────────────────────────────╮
│ check-code-style                                                                                  │
│ coverage                     Run and show coverage.                                               │
│ debug-settings               Display (anonymized) MQTT server username and password               │
│ debug-systemd-service        Just print the systemd service file content                          │
│ detect-serial                Just print the detected serial port instance                         │
│ dump                         Just dump serial output                                              │
│ fix-code-style               Fix code style via darker                                            │
│ mypy                         Run Mypy (configured in pyproject.toml)                              │
│ publish-loop                 Publish current data via MQTT (endless loop)                         │
│ setup-systemd-service        Setup PySmartMeter systemd services and starts it.                   │
│ store-settings               Store MQTT server settings.                                          │
│ systemd-status               Call systemd status of PySmartMeter services                         │
│ systemd-stop                 Stop PySmartMeter systemd services                                   │
│ test                         Run unittests                                                        │
╰───────────────────────────────────────────────────────────────────────────────────────────────────╯
```

Test if you Hichi Smartmeter with CP2102 USB to UART Bridge Controller will be found, e.g.:
```bash
~/pysmartmeter$ ./cli.sh detect-serial
```

Maybe you didn't have permissions to access the port, e.g.:
```bash
~/pysmartmeter$ ./cli.sh dump
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
~/pysmartmeter$ ./cli.sh store-settings
```
This will create a JSON file here: `~/.pysmartmeter`

You can test reading this settings file with:
```bash
~/pysmartmeter$ ./cli.sh debug-settings
```

Setup systemd service:
```bash
~/pysmartmeter$ sudo ./cli.sh setup-systemd-service
```
This will create a systemd service that automaticly starts on every boot.

Check if service is running:
```bash
~/pysmartmeter$ sudo ./cli.sh systemd-status
```

If everything is fine: Go to your [Home Assistant and check the MQTT integration](https://www.home-assistant.io/integrations/mqtt/)
The device discovery will be made automaticly.

# various links

* https://github.com/pyserial/pyserial
* https://github.com/eclipse/paho.mqtt.python
* https://github.com/eclipse/mosquitto
* https://dewiki.de/Lexikon/OBIS-Kennzahlen (de) | https://www.promotic.eu/en/pmdoc/Subsystems/Comm/PmDrivers/IEC62056_OBIS.htm (en)
* https://www.photovoltaikforum.com/thread/145886-habe-lesk%C3%B6pfe-mit-usb-%C3%BCber/ (de)
* https://www.heise.de/tests/Ausprobiert-Guenstiger-IR-Lesekopf-fuer-Smart-Meter-mit-Tastmota-Firmware-7065559.html (de)
* https://www.home-assistant.io
