from machine import UART, Pin
from time import sleep_ms, ticks_ms, ticks_diff


class NodeModuleDriver:

    _VALID_LORA_MODES: tuple = ('LORA', 'LORAWAN')
    _VALID_REGIONS: tuple = ('EU868', 'US915', 'CN470')
    _VALID_JOIN_TYPES: tuple = ('OTAA', 'ABP')
    _VALID_NET_TYPES: tuple = ('CLASS_A', 'CLASS_C')
    _VALID_PACKET_TYPES: tuple = ('CONFIRMED', 'UNCONFIRMED')
    _VALID_FREQUENCY_RANGES: dict = {
        'EU868': (863000000, 870000000),
        'US915': (902000000, 928000000),
        'CN470': (470000000, 510000000),
    }
    _VALID_DATA_RANGES: dict = {
        'EU868': range(0, 6),
        'US915': range(0, 4),
        'CN470': range(0, 6)
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

    def _required_lora_mode(self, expected: str):
        if self._mode is None:
            raise ValueError("LoRa mode must be set before this operation")

        if self._mode != expected:
            raise ValueError(f"This operation requires mode: {expected}")

    def _required_join_type(self, expected: str):
        if self._join_type is None:
            raise ValueError("LoRa join type must be set before this operation")

        if self._join_type != expected:
            raise RuntimeError(f"This operation requires join type: {expected}")

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

    def _receive_raw_data(self):
        raw_data = self._send_command('RECV')

        if not raw_data:
            return None
        else:
            return raw_data

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

    def set_data_rate(self, value: int):
        self._required_lora_mode('LORAWAN')
        self._required_region()

        if value not in self._VALID_DATA_RANGES[self._region]:
            raise ValueError(f"Invalid data rate for region {self._region}.")

        self._send_command(f'+DATARATE={value}')

    def set_dev_type(self, value: str):
        self._required_lora_mode('LORAWAN')

        class_type = value.upper()

        if class_type not in self._VALID_NET_TYPES:
            raise ValueError("Device class must be CLASS_A or CLASS_C")

        self._send_command(f'CLASS={class_type}')

    def set_sub_band(self, value: int):
        self._required_lora_mode('LORAWAN')

        if self._region not in {'US915', 'CN470'}:
            raise ValueError("Sub-band selection is only available for US915 and CN470 regions")

        if not (0 <= value <= 15):
            raise ValueError("Sub-band must be between 0 and 15")

        self._send_command(f'SUBBAND={value}')

    def set_packet_type(self, value: str):
        self._required_lora_mode('LORAWAN')

        mode = value.upper()

        if mode not in self._VALID_PACKET_TYPES:
            raise ValueError("Packet type must be either CONFIRMED or UNCONFIRMED")

        self._send_command(f'UPLINKTYPE={mode}')

    def set_join_type(self, value: str):
        self._required_lora_mode('LORAWAN')

        join_type = value.upper()

        if join_type not in self._VALID_JOIN_TYPES:
            raise ValueError("Join type must be either OTAA or ABP")

        self._join_type = join_type
        self._send_command(f'JOINTYPE={join_type}')

    def set_app_eui(self, value: str):
        self._required_lora_mode('LORAWAN')
        self._required_join_type('OTAA')

        app_eui = value.upper()

        if len(app_eui) != 16:
            raise ValueError("AppEUI must be 16 characters (8 bytes in hex)")

        self._send_command(f'JOINEUI={app_eui}')

    def set_app_key(self, value: str):
        self._required_lora_mode('LORAWAN')
        self._required_join_type('OTAA')

        app_key = value.upper()

        if len(app_key) != 32:
            raise ValueError("AppKey must be 32 characters (16 bytes in hex)")

        self._send_command(f'APPKEY={app_key}')

    def set_dev_addr(self, value: str):
        self._required_lora_mode('LORAWAN')
        self._required_join_type('ABP')

        dev_addr = value.upper()

        if len(dev_addr) != 8 or not all(c in '0123456789ABCDEF' for c in dev_addr):
            raise ValueError("DevAddr must be 8 hex characters (0–9, A–F)")

        self._send_command(f'DEVADDR={dev_addr}')

    def set_app_skey(self, value: str):
        self._required_lora_mode('LORAWAN')
        self._required_join_type('ABP')

        app_skey = value.upper()

        if len(app_skey) != 32:
            raise ValueError("AppSKey must be 32 characters (16 bytes in hex)")

        self._send_command(f'APPSKEY={app_skey}')

    def set_nwk_skey(self, value: str):
        self._required_lora_mode('LORAWAN')
        self._required_join_type('ABP')

        nwk_skey = value.upper()

        if len(nwk_skey) != 32:
            raise ValueError("NwkSKey must be 32 characters (16 bytes in hex)")

        self._send_command(f'NWKSKEY={nwk_skey}')

    def enable_adr(self, value: bool):
        self._required_lora_mode('LORAWAN')

        cmd = f'ADR={1 if value else 0}'
        self._send_command(cmd)

    def enable_receive_mode(self):
        self._send_command('RECV=1')

    def test_device(self):
        print(self._send_command(''))

    def reset_device(self):
        self._send_command('REBOOT')

    def start_device(self) -> None:
        self._send_command('JOIN=1')

    def get_lora_mode(self):
        response = self._send_command('LORAMODE?')
        return response.split('=')[-1] if response else None

    def get_region(self):
        response = self._send_command('REGION?')
        return response.split('=')[-1] if response else None

    def get_frequency(self):
        response = self._send_command('FREQS?')
        return response.split('=')[-1] if response else None

    def get_transmit_power(self):
        response = self._send_command('EIRP?')
        return response.split('=')[-1] if response else None

    def get_bandwidth(self):
        response = self._send_command('BW?')
        return response.split('=')[-1] if response else None

    def get_spreading_factor(self):
        response = self._send_command('SF?')
        return response.split('=')[-1] if response else None

    def get_data_rate(self):
        response = self._send_command('DATARATE?')
        return response.split('=')[-1] if response else None

    def get_dev_eui(self):
        response = self._send_command('DEVEUI?')
        return response.split('=')[-1] if response else None

    def get_net_id(self):
        response = self._send_command('NETID?')
        return response.split('=')[-1] if response else None

    def get_dev_addr(self):
        response = self._send_command('DEVADDR?')
        return response.split('=')[-1] if response else None

    def get_eirp(self):
        response = self._send_command('EIRP?')
        return response.split('=')[-1] if response else None

    def is_joined(self):
        self._required_lora_mode('LORAWAN')

        response = self._send_command('JOIN?')
        joined = response and response.strip() == '+JOIN=1'

        return joined

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
        value = None
        raw_response = self._send_command('RECV?')

        for line in raw_response.splitlines():
            if line.strip() in ("+RECV=OK", "The list is empty!"):
                continue

            if "The list is empty!" in line:
                line = line.split("The list is empty!")[0].rstrip()

            if line.startswith("+RECV="):
                parts = line.split("\t", 1)
                if len(parts) == 2:
                    value = parts[1]
                else:
                    value = line.split(" ", 1)[-1]

        if value:
            return value
        else:
            return None
