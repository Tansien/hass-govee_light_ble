DOMAIN = "govee_light_ble"
DISCOVERY_NAMES = ('Govee_', 'ihoment_', 'GBK_')
CONF_SEGMENTED = "segmented"
NON_SEGMENTED_NAMES = ("ihoment_H6102", "Govee_H6102", "H6102")
READ_CHARACTERISTIC_UUID = '00010203-0405-0607-0809-0a0b0c0d2b10'
WRITE_CHARACTERISTIC_UUID = '00010203-0405-0607-0809-0a0b0c0d2b11'


def default_segmented(name: str | None) -> bool:
    """Return the safest segmented protocol default for a BLE name."""
    return not (name or "").startswith(NON_SEGMENTED_NAMES)
