<div align="center">
<img src="media/yacc.png" width=500/>

# Yet Another CANopen Configurator
</div>

YACC is a simple read&write CANopen parameter set written on top of the [canopen](https://github.com/christiansandberg/canopen) library.

## Prerequisites
The [PEAK](https://www.peak-system.com/), [kvaser](https://kvaser.com/) and [ixxat](https://www.hms-networks.com/ixxat) devices are the possible selections: make sure to have the proper driver installed.

## Installation
Clone the repository, create a virtual environment, activate it and install the requirements
```bash
git clone https://github.com/setteZ/yacc.git
cd yacc
python3 -m venv .venv
source .venv/bin/activate
pip install .
```
or you can install [uv](https://github.com/astral-sh/uv) and after cloning the repo you can use yacc with:
```bash
uv run yacc/yacc.py
```


## Usage
There are two way to use YACC:
- a clean `yacc.py` will launch the GUI
- a geek `yacc.py -h` will show you the CLI capability

## Features
There is the possibility to:
1. upload form the device the configuration (starting from a .eds file)
2. download into the device a specific configuration (the .dcf file)
3. tell to the device to `save` the configuration

Bonus: the GUI gives the possibility to read/write a single entry.
That's all.