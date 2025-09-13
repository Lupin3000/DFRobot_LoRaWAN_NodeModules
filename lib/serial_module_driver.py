from logging import getLogger, debug, info, error
from serial import Serial, SerialException
from time import time, sleep
from typing import Optional, Type
from types import TracebackType


logger = getLogger(__name__)


class NodeModuleDriver:
    """
    Provides an interface for controlling the DFRobot LoRaWAN Node Module.

    :ivar _DELAY: Delay in seconds between sending commands.
    :type _DELAY: float
    :ivar _VALID_LORA_MODES: Specifies the allowed operating modes.
    :type _VALID_LORA_MODES: tuple
    :ivar _VALID_REGIONS: Specifies the allowed regions.
    :type _VALID_REGIONS: tuple
    :ivar _VALID_JOIN_TYPES: Specifies the allowed join types.
    :type _VALID_JOIN_TYPES: tuple
    :ivar _VALID_NET_TYPES: Specifies the allowed network types.
    :type _VALID_NET_TYPES: tuple
    :ivar _VALID_PACKET_TYPES: Specifies the allowed packet types.
    :type _VALID_PACKET_TYPES: tuple
    :ivar _VALID_FREQUENCY_RANGES: Specifies the valid frequency ranges for each region.
    :type _VALID_FREQUENCY_RANGES: dict
    :ivar _VALID_DATA_RANGES: Specifies the valid data rates for each region.
    :type _VALID_DATA_RANGES: dict
    :ivar _VALID_TRANSMIT_POWERS: Range of allowed transmit powers.
    :type _VALID_TRANSMIT_POWERS: tuple
    :ivar _VALID_BANDWIDTHS: Specifies the allowed bandwidths.
    :type _VALID_BANDWIDTHS: tuple
    :ivar _VALID_SPREADING_FACTORS: Range of supported spreading factors.
    :type _VALID_SPREADING_FACTORS: tuple
    """
    _DELAY: float = 0.5
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

    def __init__(self, device_id: int, port: str, baudrate: int = 9600):
        """
        Initializes a communication interface for a device by specifying its device ID,
        port, and baudrate. The device ID must be a value between 1 and 255.

        :param device_id: The ID of the device. Must be within the range 1-255.
        :type device_id: int
        :param port: The serial port to which the device is connected.
        :type port: str
        :param baudrate: The baud rate for the serial communication.
        :type baudrate: int
        :raises ValueError: If the device ID is not within the valid range.
        """
        if not (1 <= device_id <= 255):
            error('Device ID must be between 1 and 255')
            raise ValueError("[ERROR] Device ID must be between 1 and 255")

        self._device_id = device_id
        self._region = None
        self._mode = None
        self._join_type = None

        try:
            self._ser = Serial(port=port, baudrate=baudrate, timeout=1)
        except SerialException as err:
            error(f"Open serial port: {err}")
            raise RuntimeError(f"[ERROR] Open serial port: {err}")

    def __enter__(self) -> 'NodeModuleDriver':
        """
        Open the serial connection if it is not already open.

        :returns: The instance of the resource that is being managed.
        :rtype: NodeModuleDriver
        """
        if not self._ser.is_open:
            self._ser.open()

        return self

    def __exit__(self,
                 exc_type: Optional[Type[BaseException]],
                 exc_val: Optional[BaseException],
                 exc_tb: Optional[TracebackType]
                 ) -> None:
        """
        Handle the actions to be taken when exiting a context managed by the object.

        :param exc_type: The exception type that caused the exit from the context block.
        :type exc_type: Optional[Type[BaseException]]
        :param exc_val: The exception instance that caused the exit from the context block.
        :type exc_val: Optional[BaseException]
        :param exc_tb: The traceback that caused the exit from the context block.
        :type exc_tb: Optional[TracebackType]
        :return: None
        """
        if exc_type is KeyboardInterrupt:
            info("Closing serial connection.")

        if self._ser.is_open:
            self._ser.close()

    def _required_lora_mode(self, expected: str) -> None:
        """
        Ensures LoRa mode is set and that the current LoRa mode matches the expected mode.

        :param expected: The mode required for the operation.
        :type expected: str
        :raises ValueError: If the mode is not set.
        :raises ValueError: If the mode does not match the expected mode.
        :return: None
        """
        if self._mode is None:
            error("LoRa mode must be set before this operation")
            raise ValueError("LoRa mode must be set before this operation")

        if self._mode != expected:
            error(f"This operation requires mode: {expected}")
            raise ValueError(f"This operation requires mode: {expected}")

    def _required_join_type(self, expected: str) -> None:
        """
        Ensures the LoRaWAN join type is set and that the current join type
        matches the expected join type.

        :param expected: The expected join type to validate against.
        :type expected: str
        :raises ValueError: If the join type has not been set.
        :raises RuntimeError: If the current join type does not match the expected type.
        """
        if self._join_type is None:
            error("LoRa join type must be set before this operation")
            raise ValueError("LoRa join type must be set before this operation")

        if self._join_type != expected:
            error(f"This operation requires join type: {expected}")
            raise RuntimeError(f"This operation requires join type: {expected}")

    def _required_region(self) -> None:
        """
        Raises an exception if the LoRa region is not set.

        :raises ValueError: If the LoRa region attribute is not set.
        :return: None
        """
        if self._region is None:
            error("LoRa region must be set before this operation")
            raise ValueError("LoRa region must be set before this operation")

    def _send_command(self, command: str, timeout: float = 5.0) -> Optional[str]:
        """
        Sends an AT command to the device and waits for a response. This method ensures the
        command format is correct and reads the device's output within a specified timeout period.

        :param command: The AT command to send.
        :type command: str
        :param timeout: Maximum duration to wait for a response, in seconds.
        :type timeout: float
        :return: The response from the device as a string, or None.
        :rtype: Optional[str]
        """
        if not command.startswith('+') and command != '':
            command = '+' + command

        full_command = f'AT{command}\r\n'.encode()

        debug(f"[SEND] {full_command}")

        self._ser.reset_input_buffer()
        self._ser.write(full_command)

        response = ""
        start_time = time()

        while time() - start_time < timeout:
            if self._ser.in_waiting:
                chunk = self._ser.read(self._ser.in_waiting).decode(errors='ignore')
                response += chunk

                if any(end in response for end in
                       ['+SEND=OK',
                        '+SEND=QUEUE',
                        '+SEND=QU',
                        '+SEND=FAIL',
                        'OK',
                        'ERROR']) and response.endswith('\r\n'):
                    break

            sleep(0.05)

        response = response.strip()

        debug(f"[RECV] {response}")

        return response or None

    def _receive_raw_data(self) -> Optional[str]:
        """
        Processes and retrieves raw data received from the 'RECV' command.

        :return: The raw data received as a string, or None if no data is available.
        :rtype: Optional[str]
        """
        raw_data = self._send_command('RECV')

        if not raw_data:
            return None
        else:
            return raw_data

    def set_lora_mode(self, mode: str) -> None:
        """
        Sets the operating mode for LoRa communication. This method configures
        the LoRa module to operate in the specified mode. If an invalid mode is provided,
        a ValueError will be raised.

        :param mode: The desired LoRa mode as a string. Must be one of the allowed modes.
        :type mode: str
        :raises ValueError: If the LoRa mode is not in the list of allowed modes.
        :return: None
        """
        if mode not in self._VALID_LORA_MODES:
            error(f"Invalid LoRa mode: {mode}")
            raise ValueError(f"Invalid LoRa mode. Allowed modes: {self._VALID_LORA_MODES}")

        self._mode = mode.upper()
        self._send_command(f'LORAMODE={mode.upper()}')

    def set_region(self, value: str = 'EU868') -> None:
        """
        Sets the operating region for the system configuration.

        This method allows setting the operating region for the system. The region must be
        one of the allowed values defined in the system. If an invalid region is provided,
        an exception will be raised.

        :param value: The LoRa region to set. Defaults to 'EU868'.
        :type value: str
        :raises ValueError: If the provided region is not in the list of allowed regions.
        :return: None
        """
        if value not in self._VALID_REGIONS:
            error(f"Invalid region: {value}")
            raise ValueError(f"Invalid region. Allowed regions: {self._VALID_REGIONS}")

        self._region = str(value)
        self._send_command(f'REGION={self._region}')

    def set_frequency(self, value: int) -> None:
        """
        Sets the frequency for the given region. The frequency must fall within the
        valid range designated for the region. If the region is not set, an error
        will be raised. If the frequency falls outside the predefined limits,
        a value error will be raised.

        :param value: Frequency in Hz to set.
        :type value: int
        :raises ValueError: If the frequency is out of the valid range.
        :return: None
        """
        self._required_region()

        min_freq, max_freq = self._VALID_FREQUENCY_RANGES[self._region]

        if not (min_freq <= value <= max_freq):
            error(f"Frequency {value} out of range for region {self._region}.")
            raise ValueError(f"Frequency {value} out of range for region {self._region}. "
                             f"Valid range: {min_freq} - {max_freq} Hz")

        self._send_command(f'FREQS={value}')

    def set_transmit_power(self, value: int) -> None:
        """
        Sets transmit power (dBm) to a specified value if it is within the allowed range.
        If the provided value is invalid, an error is raised to indicate the issue.

        :param value: The desired transmit power value to set.
        :type value: int
        :raises ValueError: If the transmit power value is not one of the allowed values.
        :return: None
        """
        if value not in self._VALID_TRANSMIT_POWERS:
            error(f"Invalid transmit power: {value}")
            raise ValueError(f"Invalid transmit power. Allowed values: {self._VALID_TRANSMIT_POWERS}")

        self._send_command(f'EIRP={value}')

    def set_bandwidth(self, value: int) -> None:
        """
        Sets the bandwidth to the specified value. Validates the provided value
        against a predefined set of allowed bandwidths. If the bandwidth is valid,
        a corresponding command is sent to update the bandwidth. Invalid bandwidths
        will result in an exception being raised.

        :param value: Desired bandwidth setting.
        :type value: int
        :raises ValueError: If the provided bandwidth is not in the allowed set.
        :return: None
        """
        if value not in self._VALID_BANDWIDTHS:
            error(f"Invalid bandwidth: {value}")
            raise ValueError(f"Invalid bandwidth. Allowed: {self._VALID_BANDWIDTHS}")

        self._send_command(f'BW={value}')

    def set_spreading_factor(self, value: int) -> None:
        """
        Sets the spreading factor (SF) for the device. The value of SF must be one of
        the allowed spreading factors. If an invalid value is provided, a ValueError is raised.

        :param value: The spreading factor to be set.
        :type value: int
        :raises ValueError: If the provided value is not within the list of allowed values.
        :return: None
        """
        if value not in self._VALID_SPREADING_FACTORS:
            error(f"Invalid SF: {value}")
            raise ValueError(f"Invalid SF. Allowed: {list(self._VALID_SPREADING_FACTORS)}")

        self._send_command(f'SF={value}')

    def set_data_rate(self, value: int) -> None:
        """
        Sets the data rate for the device. This function configures the data rate, defined by
        the `value` parameter, for the current mode and region settings. The function ensures
        that the device is in a valid mode and within a valid region before setting the data rate.

        :param value: The desired data rate to configure.
        :type value: int
        :raises ValueError: If the provided data rate is not valid for the current region.
        :return: None
        """
        self._required_lora_mode('LORAWAN')
        self._required_region()

        if value not in self._VALID_DATA_RANGES[self._region]:
            error(f"Invalid data rate {value} for region {self._region}")
            raise ValueError(f"Invalid data rate for region {self._region}.")

        self._send_command(f'+DATARATE={value}')

    def set_dev_type(self, value: str) -> None:
        """
        Sets the device type to the specified LoRaWAN class.
        The class type must be one of the supported LoRaWAN classes.

        :param value: The LoRaWAN class type
        :type value: str
        :raises ValueError: If the provided class type is not CLASS_A or CLASS_C.
        :return: None
        """
        self._required_lora_mode('LORAWAN')

        class_type = value.upper()

        if class_type not in self._VALID_NET_TYPES:
            error("Device class must be CLASS_A or CLASS_C")
            raise ValueError("Device class must be CLASS_A or CLASS_C")

        self._send_command(f'CLASS={class_type}')

    def set_sub_band(self, value: int) -> None:
        """
        Sets the sub-band for the LoRaWAN operation. This functionality is region-dependent
        and only applicable for the US915 and CN470 regions.

        :param value: Integer value representing the sub-band to configure (0 to 15).
        :type value: int
        :raises ValueError: If the region does not support sub-band selection.
        :raises ValueError: If an invalid sub-band value (not between 0 and 15) is provided.
        :return: None
        """
        self._required_lora_mode('LORAWAN')

        if self._region not in {'US915', 'CN470'}:
            error("Sub-band selection is only available for US915 and CN470 regions")
            raise ValueError("Sub-band selection is only available for US915 and CN470 regions")

        if not (0 <= value <= 15):
            error("Sub-band must be between 0 and 15")
            raise ValueError("Sub-band must be between 0 and 15")

        self._send_command(f'SUBBAND={value}')

    def set_packet_type(self, value: str) -> None:
        """
        Sets the packet type for LoRaWAN communication. The packet type defines whether
        the message is confirmed or unconfirmed. A confirmed message requires an
        acknowledgment from the receiver, while an unconfirmed message does not.

        :param value: Specifies the LoRaWAN packet type.
        :type value: str
        :raises ValueError: If the provided packet type is not 'CONFIRMED' or 'UNCONFIRMED'.
        :return: None
        """
        self._required_lora_mode('LORAWAN')

        mode = value.upper()

        if mode not in self._VALID_PACKET_TYPES:
            error("Packet type must be either CONFIRMED or UNCONFIRMED")
            raise ValueError("Packet type must be either CONFIRMED or UNCONFIRMED")

        self._send_command(f'UPLINKTYPE={mode}')

    def set_join_type(self, value: str) -> None:
        """
        Sets the join type for the device, ensuring it meets the mode requirements
        and is within the allowed join types. The join type determines how the device
        will connect in LORAWAN mode (OTAA or ABP).

        :param value: The join type (OTAA or ABP) to set.
        :type value: str
        :raises ValueError: If the provided join type is invalid.
        :return: None
        """
        self._required_lora_mode('LORAWAN')

        join_type = value.upper()

        if join_type not in self._VALID_JOIN_TYPES:
            error(f"Invalid join type: {join_type}")
            raise ValueError("Join type must be either OTAA or ABP")

        self._join_type = join_type
        self._send_command(f'JOINTYPE={join_type}')

    def set_app_eui(self, value: str) -> None:
        """
        Sets the AppEUI (JoinEUI) for a device. The AppEUI is a unique 64-bit identifier
        used to identify the application associated with the device.

        :param value: The AppEUI represented as a 16-character hexadecimal string.
        :type value: str
        :raises ValueError: If the provided AppEUI is not 16 characters long.
        :return: None
        """
        self._required_lora_mode('LORAWAN')
        self._required_join_type('OTAA')

        app_eui = value.upper()

        if len(app_eui) != 16:
            error("AppEUI must be 16 characters (8 bytes in hex)")
            raise ValueError("AppEUI must be 16 characters (8 bytes in hex)")

        self._send_command(f'JOINEUI={app_eui}')

    def set_app_key(self, value: str) -> None:
        """
        Sets the application key (AppKey) for LoRaWAN communication. The AppKey is a crucial
        parameter in the OTAA (Over-The-Air Activation) join procedure for LoRaWAN devices.

        :param value: The AppKey to be set, which must be a 32-character hexadecimal string.
        :type value: str
        :raises ValueError: If the provided AppKey is not exactly 32 characters long.
        :return: None
        """
        self._required_lora_mode('LORAWAN')
        self._required_join_type('OTAA')

        app_key = value.upper()

        if len(app_key) != 32:
            error("AppKey must be 32 characters (16 bytes in hex)")
            raise ValueError("AppKey must be 32 characters (16 bytes in hex)")

        self._send_command(f'APPKEY={app_key}')

    def set_dev_addr(self, value: str) -> None:
        """
        Sets the device address (DevAddr) for the device in LORAWAN mode with an ABP join
        type. The address must be a string of exactly 8 hexadecimal characters
        (containing only 0 – 9 and A – F).

        :param value: The device address as an 8-character hexadecimal string.
        :type value: str
        :raises ValueError: If the provided address is not exactly 8 characters long.
        :return: None
        """
        self._required_lora_mode('LORAWAN')
        self._required_join_type('ABP')

        dev_addr = value.upper()

        if len(dev_addr) != 8 or not all(c in '0123456789ABCDEF' for c in dev_addr):
            error("DevAddr must be 8 hex characters (0–9, A–F)")
            raise ValueError("DevAddr must be 8 hex characters (0–9, A–F)")

        self._send_command(f'DEVADDR={dev_addr}')

    def set_app_skey(self, value: str) -> None:
        """
        Sets the Application Session Key (AppSKey) for the LoRa device. The AppSKey
        must be exactly 32 characters (16 bytes in hexadecimal format).

        :param value: Application Session Key (AppSKey) in hexadecimal format.
        :type value: str
        :raises ValueError: If the provided AppSKey is not exactly 32 characters long.
        :return: None
        """
        self._required_lora_mode('LORAWAN')
        self._required_join_type('ABP')

        app_skey = value.upper()

        if len(app_skey) != 32:
            error("AppSKey must be 32 characters (16 bytes in hex)")
            raise ValueError("AppSKey must be 32 characters (16 bytes in hex)")

        self._send_command(f'APPSKEY={app_skey}')

    def set_nwk_skey(self, value: str) -> None:
        """
        Sets the Network Session Key (NwkSKey) for an ABP (Activation By Personalization)
        Join type and LoRaWAN mode. The key must be provided as a 32-character hexadecimal.

        :param value: A 32-character hexadecimal string (16 bytes).
        :type value: str
        :raises ValueError: If the provided value is not a 32-character hexadecimal string.
        :return: None
        """
        self._required_lora_mode('LORAWAN')
        self._required_join_type('ABP')

        nwk_skey = value.upper()

        if len(nwk_skey) != 32:
            error("NwkSKey must be 32 characters (16 bytes in hex)")
            raise ValueError("NwkSKey must be 32 characters (16 bytes in hex)")

        self._send_command(f'NWKSKEY={nwk_skey}')

    def enable_adr(self, value: bool) -> None:
        """
        Enables or disables ADR (Adaptive Data Rate) for the device
        to optimize the communication link in LoRaWAN by adjusting the data
        rate and power level dynamically.

        :param value: A boolean indicating whether to enable ADR.
        :return: None
        """
        self._required_lora_mode('LORAWAN')

        cmd = f'ADR={1 if value else 0}'
        self._send_command(cmd)

    def enable_receive_mode(self) -> None:
        """
        Enable the device to receive mode.

        :return: None
        """
        self._send_command('RECV=1')

    def test_device(self) -> None:
        """
        Tests the serial connection to the device by sending an empty command.

        :return: None
        """
        info(self._send_command(''))

    def reset_device(self) -> None:
        """
        Resets the device by sending a reboot command.

        :return: None
        """
        self._send_command('REBOOT')

    def start_device(self) -> None:
        """
        Start the device in a specific mode.

        :return: None
        """
        self._send_command('JOIN=1')

    def get_lora_mode(self) -> Optional[str]:
        """
        Gets the LoRa mode by sending a specific command to the device.

        :return: The LoRa mode as a string, or None if not available.
        :rtype: Optional[str]
        """
        response = self._send_command('LORAMODE?')
        return response.split('=')[-1] if response else None

    def get_region(self) -> Optional[str]:
        """
        Gets the region by sending a specific command to the device.

        :return: The region as a string, or None if not available.
        :rtype: Optional[str]
        """
        response = self._send_command('REGION?')
        return response.split('=')[-1] if response else None

    def get_frequency(self) -> Optional[str]:
        """
        Gets the frequency by sending a specific command to the device.

        :return: The frequency as a string, or None if not available.
        :rtype: Optional[str]
        """

        response = self._send_command('FREQS?')
        return response.split('=')[-1] if response else None

    def get_transmit_power(self) -> Optional[str]:
        """
        Gets the transmit power by sending a specific command to the device.

        :return: The transmit power as a string, or None if not available.
        :rtype: Optional[str]
        """
        response = self._send_command('EIRP?')
        return response.split('=')[-1] if response else None

    def get_bandwidth(self) -> Optional[str]:
        """
        Gets the bandwidth by sending a specific command to the device.

        :return: The bandwidth as a string, or None if not available.
        :rtype: Optional[str]
        """
        response = self._send_command('BW?')
        return response.split('=')[-1] if response else None

    def get_spreading_factor(self) -> Optional[str]:
        """
        Gets the spreading factor by sending a specific command to the device.

        :return: The spreading factor as a string, or None if not available.
        :rtype: Optional[str]
        """
        response = self._send_command('SF?')
        return response.split('=')[-1] if response else None

    def get_data_rate(self) -> Optional[str]:
        """
        Gets the data range by sending an appropriate command to the device.

        :return: The data range value as a string if available, otherwise None.
        :rtype: Optional[str]
        """
        response = self._send_command('DATARATE?')
        return response.split('=')[-1] if response else None

    def get_dev_eui(self) -> Optional[str]:
        """
        Retrieve the Extended Unique Identifier (DEVEUI) from the device.

        :return: The DEVEUI as a string if available, otherwise None.
        :rtype: Optional[str]
        """
        response = self._send_command('DEVEUI?')
        return response.split('=')[-1] if response else None

    def get_net_id(self) -> Optional[str]:
        """
        Retrieves the network id from the response of a command sent to the device.
        If a device is connected to LoRaWAN otherwise returns None.

        :return: The network id as a string if found, otherwise None.
        :rtype: Optional[str]
        """
        response = self._send_command('NETID?')
        return response.split('=')[-1] if response else None

    def get_dev_addr(self) -> Optional[str]:
        """
        Retrieves the device address from the response of a command sent to the device.
        If a device is connected to LoRaWAN otherwise returns None.

        :return: The device address as a string if found, otherwise None.
        :rtype: Optional[str]
        """
        response = self._send_command('DEVADDR?')
        return response.split('=')[-1] if response else None

    def get_eirp(self) -> Optional[str]:
        """
        Retrieves the Effective Isotropic Radiated Power (EIRP) from the device.
        If a device is connected to LoRaWAN otherwise returns None.

        :return: The EIRP value as a string if available.
        :rtype: Optional[str]
        """
        response = self._send_command('EIRP?')
        return response.split('=')[-1] if response else None

    def is_joined(self) -> bool:
        """
        Checks if the device is joined to the LoRaWAN network.

        :return: True if the device is joined, False otherwise.
        :rtype: bool
        """
        self._required_lora_mode('LORAWAN')

        response = self._send_command('JOIN?')
        joined = response and response.strip() == '+JOIN=1'

        info(f"Device join status: {'joined' if joined else 'not joined'}")
        return joined

    def send_data(self, target_id: int, data: str) -> None:
        """
        Sends data to a specified target device. The function sends a formatted
        command string to the target device, encoded as hexadecimal. It ensures
        the target ID is valid and is different from the sender's device ID.
        Raises exceptions for invalid input values.

        :param target_id: The ID of the target device.
        :type target_id: int
        :param data: Data to be sent to the target device, represented as a string.
        :type data: str
        :raises ValueError: If the target ID is invalid.
        :raises ValueError: If the target ID is the same as the sender's device ID.
        :raises ValueError: If the LoRa mode is not set before sending data.
        :raises ValueError: If the LoRa mode is set to LoRaWAN, and the join type is not set.
        :return: None
        """
        if not (1 <= target_id <= 255):
            error(f"Invalid target ID: {target_id}")
            raise ValueError("Target ID must be between 1 and 255")

        if target_id == self._device_id:
            error("Target ID cannot be the same as the Device ID")
            raise ValueError("Target ID cannot be the same as the Device ID")

        if self._mode is None:
            error("LoRa mode must be set before sending data")
            raise ValueError("LoRa mode must be set before sending data")

        if self._mode == 'LORAWAN':
            if self._join_type is None:
                error("Join type must be set before sending data in LoRaWAN mode")
                raise ValueError("Join type must be set before sending data in LoRaWAN mode")

        to_hex = f'{target_id:02X}'
        from_hex = f'{self._device_id:02X}'
        data_hex = data.encode().hex().upper()
        payload = to_hex + from_hex + data_hex

        self._send_command(f'SEND={payload}')

    def receive_data(self) -> Optional[str]:
        """
        Processes received raw data, extracts meaningful payload, and ignores specific
        irrelevant lines. The function communicates using a command, parses the
        response, and disregards predefined ignored messages or empty strings. If a
        valid payload is found, it is returned; otherwise, the function returns None.

        :param self: Instance of the class (implicit parameter for instance methods).
        :return: Processed payload as a string if it exists, otherwise None.
        :rtype: Optional[str]
        """
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
