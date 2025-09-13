# Gravity: LoRaWAN Node Module 

[![Static](https://img.shields.io/badge/python-==3.12.2-green)](https://python.org)
[![Static](https://img.shields.io/badge/MicroPython-==1.25.0-green)](https://micropython.org)

You can find the details about LoRaWAN Node Modules on the DFRobot [Wiki](https://wiki.dfrobot.com/SKU_DFR1115-868_Gravity_LoRaWAN_Node_Module_EU868) page. The original CPP drivers and Arduino examples are available on DFRobots [GitHub](https://github.com/cdjq/DFRobot_LWNode) repository.

## Preparation

```shell
# clone GitHub project
$ git clone https://github.com/Lupin3000/DFRobot_LoRaWAN_NodeModules.git

# change into cloned project directory
$ cd DFRobot_LoRaWAN_NodeModules/

# create Python virtualenv (optional)
$ python3 -m venv .venv

# activate Python virtualenv (macOS & Linux)
$ source .venv/bin/activate

# update pip (optional)
(.venv) $ pip3 install -U pip
```

## Python (_serial_)

The Python serial module supports LoRa and LoRaWAN modes for EU868/US915/CN470.

### Quick Installation

```shell
# install required Python dependencies
(.venv) $ pip3 install -r serial_requirements.txt

# show packages (optional)
(.venv) $ pip3 freeze
```

Serial P2P example files are located in the `example_serial_*.py` files.

```
Project
├── conf
│   ├── lora_configuration.py
│   └── serial_configuration.py
├── lib
│   └── serial_module_driver.py
├── example_serial_receive.py
└── example_serial_send.py
```

### Run LoRa (P2P) serial example

Set the dial switch to UART and connect the node modules.

![serial connection example](img/serial_connection.jpg)

_The picture shows the usage of two CH340 USB to TTL converters for each Node module._

Before running the examples to send and receive data. Ensure the configuration settings meet your requirements! Therefor, adapt files `conf/lora_configuration.py` and `conf/serial_configuration.py`.

```shell
# start serial receive
(.venv) $ python3 example_serial_receive.py

Received payload: Hello (0)
Received payload: Hello (1)
Received payload: Hello (2)
Received payload: Hello (3)
Received payload: Hello (4)
[INFO] Closing serial connection.
[INFO] Exiting...
[INFO] Closing application...

# start serial send
(.venv) $ python3 example_serial_send.py

Sending payload: Hello (0)
Sending payload: Hello (1)
Sending payload: Hello (2)
Sending payload: Hello (3)
Sending payload: Hello (4)
[INFO] Closing application...
```

## MicroPython (_UART_)

The MicroPython UART module supports LoRa and LoRaWAN modes for EU868/US915/CN470.

### Quick Installation

```shell
# install required MicroPython dependencies
(.venv) $ pip3 install -r uart_requirements.txt

# show packages (optional)
(.venv) $ pip3 freeze
```

If MicroPython is not flashed on the ESP device, download the latest firmware from [MicroPython](https://micropython.org/download/). The next step is to flash the MicroPython firmware on the ESP device via the esptool.

> **Note:** In case you are not familiar with command line tools like esptool, try [MicroPython-Firmware-Studio](https://github.com/Lupin3000/MicroPython-Firmware-Studio).

After that, use rshell to connect to the ESP device and upload the required directories and files. Rename the P2P example files like `example_uart_*.py` to `main.py`!

```
ESP
├── boot.py
├── conf
│   ├── lora_configuration.py
│   └── uart_configuration.py
├── lib
│   └── uart_module_driver.py
└── main.py
```

### Run LoRa (P2P) UART example

```
# receive LoRa payload (example_uart_receive.py)

Received payload: Hello (0)
Received payload: Hello (1)
Received payload: Hello (2)
Received payload: Hello (3)
Received payload: Hello (4)

# send LoRa payload (example_uart_send.py)

Sending payload: Hello (0)
Sending payload: Hello (1)
Sending payload: Hello (2)
Sending payload: Hello (3)
Sending payload: Hello (4)
```
