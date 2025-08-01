# Gravity: LoRaWAN Node Module 

[![Static](https://img.shields.io/badge/python-==3.12.2-green)](https://python.org)

## Python (_serial_)

### Quick Installation

```shell
# clone project
$ git clone https://github.com/Lupin3000/DFRobot_LoRaWAN_NodeModules.git

# change into cloned project directory
$ cd DFRobot_LoRaWAN_NodeModules/

# create python virtualenv (optional)
$ python3 -m venv .venv

# activate Python virtualenv (macOS & Linux)
$ source venv/bin/activate

# update pip (optional)
(.venv) $ pip3 install -U pip

# install required dependencies
(.venv) $ pip3 install -r serial_requirements.txt

# show packages (optional)
(.venv) $ pip3 freeze
```

### Run LoRa (P2P) serial example

Set the dial switch to UART and connect the node modules.

![serial connection example](img/serial_connection.jpg)

Before running the examples to send and receive data. Ensure the configuration settings meet your requirements! Therefor, adapt files `conf/lora_configuration.py` and `conf/serial_configuration.py`.

```shell
# start serial receive
(.venv) $ python3 example_serial_receive.py

From: 1 → To: 2 | Payload: Hello (0)
From: 1 → To: 2 | Payload: Hello (1)
From: 1 → To: 2 | Payload: Hello (2)
From: 1 → To: 2 | Payload: Hello (3)
From: 1 → To: 2 | Payload: Hello (4)
[INFO] Closing serial connection.
[INFO] Exiting...
[INFO] Closing application...

# start serial send
(.venv) $ python3 example_serial_send.py

Sending data: Hello (0)
Sending data: Hello (1)
Sending data: Hello (2)
Sending data: Hello (3)
Sending data: Hello (4)
[INFO] Closing application...
```
