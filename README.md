<div align="center">
<img src="media/yacc.png" width=500/>

# Yet Another CANopen Configurator
</div>

YACC is a simple read&write CANopen parameter set written on top of the [canopen](https://github.com/christiansandberg/canopen) library.

## Prerequisites
The [PEAK](https://www.peak-system.com/), [kvaser](https://kvaser.com/) and [ixxat](https://www.hms-networks.com/ixxat) devices are the possible selections: make sure to have the proper driver installed.

## Installation
### From the source
Clone the repository
```console
$ git clone https://github.com/setteZ/yacc.git
```
or [download](https://github.com/setteZ/yacc/archive/refs/heads/master.zip) the source code.\
Create a virtual environment, activate it and install the dependencies
```console
$ cd yacc
$ python3 -m venv .venv
$ source .venv/bin/activate
$ pip install .
```
or you can stop just after cloning the repo if you use [uv](https://github.com/astral-sh/uv).

### As binary (for Windows users)
Download the proper binary from the [Releases](https://github.com/setteZ/yacc/releases) page.

## Usage
There are two way to use YACC:
- a clean `python3 yacc.py`* will launch the GUI
- a geek `python3 yacc -h`* will show you the CLI capability

(*) `uv run yacc.py` if you are using [uv](https://github.com/astral-sh/uv), just `yacc` if you are using the binary

## Features
There is the possibility to:
1. `upload` the actual values of the parameters to a .dcf file
2. `download` a .dcf file to the device
3. request the device to `save` the actual values of the parameters

Bonus: the GUI gives you the possibility to read and write a single entry.\
That's all.