from logging import basicConfig, debug, info, error
from time import sleep
from typing import Callable
from lib.serial_module_driver import NodeModuleDriver
from conf.serial_configuration import SERIAL_CONFIGURATION
from conf.lora_configuration import LORA_CONFIGURATION


LOG_LEVEL: str = 'INFO'
RECV_INTERVAL: float = 0.025
VERBOSE_MODE: bool = False


def configure_lora_device(lora_device: NodeModuleDriver) -> None:
    """
    Configures the provided LoRa device with predefined settings necessary for
    its operation.

    :param lora_device: An instance of NodeModuleDriver.
    :type lora_device: NodeModuleDriver
    :return: None
    """
    debug('Configuring LoRa device...')
    lora_device.reset_device()
    sleep(2)

    lora_device.enable_receive_mode()

    lora_device.set_region(LORA_CONFIGURATION['region'])
    lora_device.set_lora_mode(LORA_CONFIGURATION['mode'])
    lora_device.set_frequency(LORA_CONFIGURATION['frequency'])
    lora_device.set_transmit_power(LORA_CONFIGURATION['transmit_power'])
    lora_device.set_bandwidth(LORA_CONFIGURATION['bandwidth'])
    lora_device.set_spreading_factor(LORA_CONFIGURATION['spreading_factor'])

    if VERBOSE_MODE:
        print("\n=== LoRa Device P2P Configuration ===")
        print(f"{'Device ID:':18} {SERIAL_CONFIGURATION['serial_receive_id']}")
        print(f"{'Region:':18} {lora_device.get_region()}")
        print(f"{'LoRa mode:':18} {lora_device.get_lora_mode()}")
        print(f"{'Frequency:':18} {lora_device.get_frequency()}")
        print(f"{'Transmit Power:':18} {lora_device.get_transmit_power()}")
        print(f"{'Bandwidth:':18} {lora_device.get_bandwidth()}")
        print(f"{'Spreading factor:':18} {lora_device.get_spreading_factor()}")
        print("=" * 35 + "\n")


def receive_loop(lora_device: NodeModuleDriver, callback: Callable[[str], None]) -> None:
    while True:
        try:
            response = lora_device.receive_data()
            callback(response)
        except Exception as ex:
            error(f"Receive error: {ex}")

        sleep(RECV_INTERVAL)


def on_data_received(data: str) -> None:
    if data:
        try:
            to_id = ord(data[0])
            from_id = ord(data[1])
            payload = data[2:]

            clean_payload = ''.join(c for c in payload if c.isprintable())
            clean_payload = clean_payload.lstrip("=> \t\r\n")

            print(f"From: {from_id} → To: {to_id} | Payload: {clean_payload}")

        except Exception as e:
            error(f"Failed to parse received data: {e}")
            error(f"Raw data: {repr(data)}")


if __name__ == "__main__":
    basicConfig(
        level=LOG_LEVEL,
        format='[%(levelname)s] %(message)s'
    )

    try:
        with NodeModuleDriver(device_id=SERIAL_CONFIGURATION['serial_receive_id'],
                              port=SERIAL_CONFIGURATION['serial_receive_port'],
                              baudrate=SERIAL_CONFIGURATION['baudrate']) as lora:

            configure_lora_device(lora)
            lora.start_device()
            receive_loop(lora, on_data_received)
    except KeyboardInterrupt:
        info("Exiting...")
    finally:
        info("Closing application...")
