from time import sleep
from lib.uart_module_driver import NodeModuleDriver
from conf.uart_configuration import UART_CONFIGURATION
from conf.lora_configuration import LORA_CONFIGURATION


if __name__ == '__main__':
    lora = NodeModuleDriver(device_id=UART_CONFIGURATION['uart_send_id'],
                            uart_instance=UART_CONFIGURATION['uart_instance'],
                            tx=UART_CONFIGURATION['uart_tx'],
                            rx=UART_CONFIGURATION['uart_rx'])

    # lora.test_device()
    lora.reset_device()
    sleep(2)

    lora.set_region(LORA_CONFIGURATION['region'])
    lora.set_lora_mode(LORA_CONFIGURATION['mode'])
    lora.set_frequency(LORA_CONFIGURATION['frequency'])
    lora.set_transmit_power(LORA_CONFIGURATION['transmit_power'])
    lora.set_bandwidth(LORA_CONFIGURATION['bandwidth'])
    lora.set_spreading_factor(LORA_CONFIGURATION['spreading_factor'])

    lora.start_device()

    for i in range(5):
        sleep(5)
        msg = f'Hello ({i})'

        print(f'Sending message: {msg}')
        lora.send_data(target_id=2, data=msg)
