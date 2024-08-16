# pyAbletonPush
Maps the Ableton Push ta an object. Also exposes the interface over MQTT.

# Setup lib
## Requirements
* import mido https://github.com/mido/mido
* python-rtmidi `pip3 install python-rtmidi` or `pip3 install python-rtmidi --install-option="--no-jack"`
* paho-mqtt `pip3 install paho-mqtt`
* Pysh for using interactive mode https://github.com/TimGremalm/pysh
* python-osc `pip3 install python-osc`

## Install
```bash
pip install .
```

## Uninstall
```bash
pip uninstall pyAbletonPush
```

## Add module to python path
An alternative to install is to add the environment variable PYTHONPATH.

Nix:
```
~\projects\pyAbletonPush\src:~\projects\pyFaderport\src
```

Windows:
```
C:\Users\Username\projects\pyAbletonPush\src;C:\Users\Username\projects\pyFaderport\src;
```

# MQTT
Install a MQTT broker like [Mosquitto ](https://mosquitto.org/download/).

## Listen to messages
```bash
mosquitto_sub -v -t "#"
```
