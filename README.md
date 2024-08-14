# Yet Another CANopen Configurator
YACC is a simple read&write parameter set written on top of the [canopen](https://github.com/christiansandberg/canopen) library.

## Prerequisites
The [PEAK](https://www.peak-system.com/), [kvaser](https://kvaser.com/) and [ixxat](https://www.hms-networks.com/ixxat) devices are the possible selections: make sure to have the proper driver installed.

## Installation
Clone the repository and install the requirements.

## Usage
There are two way to use YACC:
- a clean `yacc.py` will launch the GUI
- a geek `yacc.py -h` will show you the CLI usage

## Features
There is the possibility to:
1. upload form the device the configuration (starting from a .eds file)
2. download into the device a specific configuration (the .dcf file)
3. tell to the device to `save` the configuration

bonus: the GUI gives the possibility to read/write a single entry.
That's all