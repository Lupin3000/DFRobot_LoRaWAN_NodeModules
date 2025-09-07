from logging import basicConfig, debug, info
from time import sleep
from lib.serial_module_driver import NodeModuleDriver
from conf.serial_configuration import SERIAL_CONFIGURATION
from conf.lora_configuration import LORA_CONFIGURATION


LOG_LEVEL: str = 'INFO'
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

    lora_device.set_region(LORA_CONFIGURATION['region'])
    lora_device.set_lora_mode(LORA_CONFIGURATION['mode'])
    lora_device.set_frequency(LORA_CONFIGURATION['frequency'])
    lora_device.set_transmit_power(LORA_CONFIGURATION['transmit_power'])
    lora_device.set_bandwidth(LORA_CONFIGURATION['bandwidth'])
    lora_device.set_spreading_factor(LORA_CONFIGURATION['spreading_factor'])

    if VERBOSE_MODE:
        print("\n=== LoRa Device P2P Configuration ===")
        print(f"{'Device ID:':18} {SERIAL_CONFIGURATION['serial_send_id']}")
        print(f"{'Region:':18} {lora_device.get_region()}")
        print(f"{'LoRa mode:':18} {lora_device.get_lora_mode()}")
        print(f"{'Frequency:':18} {lora_device.get_frequency()}")
        print(f"{'Transmit Power:':18} {lora_device.get_transmit_power()}")
        print(f"{'Bandwidth:':18} {lora_device.get_bandwidth()}")
        print(f"{'Spreading factor:':18} {lora_device.get_spreading_factor()}")
        print("=" * 35 + "\n")


if __name__ == "__main__":
    basicConfig(
        level=LOG_LEVEL,
        format='[%(levelname)s] %(message)s'
    )

    try:
        with NodeModuleDriver(device_id=SERIAL_CONFIGURATION['serial_send_id'],
                              port=SERIAL_CONFIGURATION['serial_send_port'],
                              baudrate=SERIAL_CONFIGURATION['baudrate']) as lora:

            configure_lora_device(lora_device=lora)
            lora.start_device()

            for i in range(5):
                sleep(5)
                msg = f'Hello ({i})'

                print(f'Sending message: {msg}')
                lora.send_data(target_id=SERIAL_CONFIGURATION['serial_receive_id'], data=msg)
    except KeyboardInterrupt:
        info("Exiting...")
    finally:
        info("Closing application...")
