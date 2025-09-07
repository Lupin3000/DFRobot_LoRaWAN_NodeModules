from machine import UART, Pin
from time import sleep_ms, ticks_ms, ticks_diff


class NodeModuleDriver:

    _VALID_LORA_MODES: tuple = ('LORA', 'LORAWAN')
    _VALID_REGIONS: tuple = ('EU868', 'US915', 'CN470')
    _VALID_FREQUENCY_RANGES: dict = {
        'EU868': (863000000, 870000000),
        'US915': (902000000, 928000000),
        'CN470': (470000000, 510000000),
    }
    _VALID_TRANSMIT_POWERS: tuple = range(0, 30, 2)
    _VALID_BANDWIDTHS: tuple = (125000, 250000, 500000)
    _VALID_SPREADING_FACTORS: tuple = range(7, 13)

    def __init__(self, device_id: int, uart_instance: int, tx: int, rx: int, baudrate: int = 9600):
        if not (1 <= device_id <= 255):
            raise ValueError("[ERROR] Device ID must be between 1 and 255")

        self._device_id = device_id
        self._region = None
        self._mode = None
        self._join_type = None

        try:
            self._uart = UART(uart_instance, baudrate=baudrate, tx=Pin(tx), rx=Pin(rx))
        except Exception as err:
            raise RuntimeError(f"[ERROR] Failed to init UART{uart_instance} on TX={tx}, RX={rx}: {err}")

    def _required_region(self):
        if self._region is None:
            raise ValueError("LoRa region must be set before this operation")

    def _send_command(self, command: str, timeout: float = 0.5):
        if not command.startswith('+') and command != '':
            command = '+' + command

        full_command = f'AT{command}\r\n'.encode()
        self._uart.write(full_command)

        response = ""
        start = ticks_ms()

        while ticks_diff(ticks_ms(), start) < int(timeout * 1000):
            if self._uart.any():
                chunk = self._uart.read().decode("utf-8", "ignore")
                response += chunk

                if any(end in response for end in [
                    "+SEND=OK",
                    "+SEND=QUEUE",
                    "+SEND=FAIL",
                    "OK",
                    "ERROR"
                ]) and response.endswith("\r\n"):
                    break
            sleep_ms(50)

        response = response.strip()

        return response or None

    def set_lora_mode(self, mode: str):
        if mode not in self._VALID_LORA_MODES:
            raise ValueError(f"Invalid LoRa mode. Allowed modes: {self._VALID_LORA_MODES}")

        self._mode = mode.upper()
        self._send_command(f'LORAMODE={mode.upper()}')

    def set_region(self, value: str = 'EU868'):
        if value not in self._VALID_REGIONS:
            raise ValueError(f"Invalid region. Allowed regions: {self._VALID_REGIONS}")

        self._region = str(value)
        self._send_command(f'REGION={self._region}')

    def set_frequency(self, value: int):
        self._required_region()

        min_freq, max_freq = self._VALID_FREQUENCY_RANGES[self._region]

        if not (min_freq <= value <= max_freq):
            raise ValueError(f"Frequency {value} out of range for region {self._region}. "
                             f"Valid range: {min_freq} - {max_freq} Hz")

        self._send_command(f'FREQS={value}')

    def set_transmit_power(self, value: int):
        if value not in self._VALID_TRANSMIT_POWERS:
            raise ValueError(f"Invalid transmit power. Allowed values: {self._VALID_TRANSMIT_POWERS}")

        self._send_command(f'EIRP={value}')

    def set_bandwidth(self, value: int) -> None:
        if value not in self._VALID_BANDWIDTHS:
            raise ValueError(f"Invalid bandwidth. Allowed: {self._VALID_BANDWIDTHS}")

        self._send_command(f'BW={value}')

    def set_spreading_factor(self, value: int) -> None:
        if value not in self._VALID_SPREADING_FACTORS:
            raise ValueError(f"Invalid SF. Allowed: {list(self._VALID_SPREADING_FACTORS)}")

        self._send_command(f'SF={value}')

    def enable_receive_mode(self):
        self._send_command('RECV=1')

    def test_device(self):
        print(self._send_command(''))

    def reset_device(self):
        self._send_command('REBOOT')

    def start_device(self) -> None:
        self._send_command('JOIN=1')

    def send_data(self, target_id: int, data: str):
        if not (1 <= target_id <= 255):
            raise ValueError("Target ID must be between 1 and 255")

        if target_id == self._device_id:
            raise ValueError("Target ID cannot be the same as the Device ID")

        if self._mode is None:
            raise ValueError("LoRa mode must be set before sending data")

        if self._mode == 'LORAWAN':
            if self._join_type is None:
                raise ValueError("Join type must be set before sending data in LoRaWAN mode")

        to_hex = f'{target_id:02X}'
        from_hex = f'{self._device_id:02X}'
        data_hex = data.encode().hex().upper()
        payload = to_hex + from_hex + data_hex

        self._send_command(f'SEND={payload}')

    def receive_data(self):
        raw = self._send_command('RECV')

        if not raw:
            return None

        return raw
