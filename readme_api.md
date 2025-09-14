# API

## NodeModuleDriver

### set_lora_mode

Sets the operating mode for LoRa communication. This method configures
the LoRa module to operate in the specified mode. If an invalid mode is provided,
a ValueError will be raised.

### set_region

Sets the operating region for the system configuration.

This method allows setting the operating region for the system. The region must be
one of the allowed values defined in the system. If an invalid region is provided,
an exception will be raised.

### set_frequency

Sets the frequency for the given region. The frequency must fall within the
valid range designated for the region. If the region is not set, an error
will be raised. If the frequency falls outside the predefined limits,
a value error will be raised.

### set_transmit_power

Sets transmit power (dBm) to a specified value if it is within the allowed range.
If the provided value is invalid, an error is raised to indicate the issue.

### set_bandwidth

Sets the bandwidth to the specified value. Validates the provided value
against a predefined set of allowed bandwidths. If the bandwidth is valid,
a corresponding command is sent to update the bandwidth. Invalid bandwidths
will result in an exception being raised.

### set_spreading_factor

Sets the spreading factor (SF) for the device. The value of SF must be one of
the allowed spreading factors. If an invalid value is provided, a ValueError is raised.

### set_data_rate

Sets the data rate for the device. This function configures the data rate, defined by
the `value` parameter, for the current mode and region settings. The function ensures
that the device is in a valid mode and within a valid region before setting the data rate.

### set_dev_type

Sets the device type to the specified LoRaWAN class.
The class type must be one of the supported LoRaWAN classes.

### set_sub_band

Sets the sub-band for the LoRaWAN operation. This functionality is region-dependent
and only applicable for the US915 and CN470 regions.

### set_packet_type

Sets the packet type for LoRaWAN communication. The packet type defines whether
the message is confirmed or unconfirmed. A confirmed message requires an
acknowledgment from the receiver, while an unconfirmed message does not.

### set_join_type

Sets the join type for the device, ensuring it meets the mode requirements
and is within the allowed join types. The join type determines how the device
will connect in LORAWAN mode (OTAA or ABP).

### set_app_eui

Sets the AppEUI (JoinEUI) for a device. The AppEUI is a unique 64-bit identifier
used to identify the application associated with the device.

### set_app_key

Sets the application key (AppKey) for LoRaWAN communication. The AppKey is a crucial
parameter in the OTAA (Over-The-Air Activation) join procedure for LoRaWAN devices.

### set_dev_addr

Sets the device address (DevAddr) for the device in LORAWAN mode with an ABP join
type. The address must be a string of exactly 8 hexadecimal characters
(containing only 0 – 9 and A – F).

### set_app_skey

Sets the Application Session Key (AppSKey) for the LoRa device. The AppSKey
must be exactly 32 characters (16 bytes in hexadecimal format).

### set_nwk_skey

Sets the Network Session Key (NwkSKey) for an ABP (Activation By Personalization)
Join type and LoRaWAN mode. The key must be provided as a 32-character hexadecimal.

### enable_adr

Enables or disables ADR (Adaptive Data Rate) for the device
to optimize the communication link in LoRaWAN by adjusting the data
rate and power level dynamically.

### enable_receive_mode

Enable the device to receive mode.

### test_device

Tests the serial connection to the device by sending an empty command.

### reset_device

Resets the device by sending a reboot command.

### start_device

Start the device in a specific mode.

### get_lora_mode

Gets the LoRa mode by sending a specific command to the device.

### get_region

Gets the region by sending a specific command to the device.

### get_frequency

Gets the frequency by sending a specific command to the device.

### get_transmit_power

Gets the transmit power by sending a specific command to the device.

### get_bandwidth

Gets the bandwidth by sending a specific command to the device.

### get_spreading_factor

Gets the spreading factor by sending a specific command to the device.

### get_data_rate

Gets the data range by sending an appropriate command to the device.

### get_dev_eui

Retrieve the Extended Unique Identifier (DEVEUI) from the device.

### get_net_id

Retrieves the network id from the response of a command sent to the device.
If a device is connected to LoRaWAN otherwise returns None.

### get_dev_addr

Retrieves the device address from the response of a command sent to the device.
If a device is connected to LoRaWAN otherwise returns None.

### get_eirp

Retrieves the Effective Isotropic Radiated Power (EIRP) from the device.
If a device is connected to LoRaWAN otherwise returns None.

### is_joined

Checks if the device is joined to the LoRaWAN network.

### send_data

Sends data to a specified target device. The function sends a formatted
command string to the target device, encoded as hexadecimal. It ensures
the target ID is valid and is different from the sender's device ID.
Raises exceptions for invalid input values.

### receive_specific_data

Processes and extracts a specific data message received.
The data is parsed to determine if it contains a valid message payload intended
for the current device. If no appropriate data is found, the method will return None.

### receive_data

Processes received data and do extract a relevant portion if available.
