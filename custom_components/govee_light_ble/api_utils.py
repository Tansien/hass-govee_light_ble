from enum import IntEnum
from dataclasses import dataclass

class LedPacketHead(IntEnum):
    COMMAND = 0x33
    REQUEST = 0xaa

class LedPacketCmd(IntEnum):
    POWER      = 0x01
    BRIGHTNESS = 0x04
    COLOR      = 0x05
    SEGMENT    = 0xa5

class LedColorType(IntEnum):
    SEGMENTS    = 0x15
    SINGLE      = 0x02
    LEGACY      = 0x0D

@dataclass
class LedPacket:
    #request data or perform a change
    head: LedPacketHead
    #data to request or command to perform
    cmd: LedPacketCmd
    #actual data to transmit
    payload: bytes | list = b''


def clamp_byte(value: int | float) -> int:
    """Clamp a value to the Home Assistant brightness range."""
    return max(0, min(255, round(value)))


def brightness_from_device(value: int, segmented: bool) -> int:
    """Convert device brightness to Home Assistant brightness."""
    return clamp_byte(value / 100 * 255 if segmented else value)


def brightness_to_device(value: int, segmented: bool) -> int:
    """Convert Home Assistant brightness to device brightness."""
    brightness = clamp_byte(value)
    if not segmented or brightness == 0:
        return brightness
    return max(1, min(100, round(brightness / 255 * 100)))


class GoveeUtils:
    @staticmethod
    async def generateChecksum(frame: bytes):
        """ returns checksum by XORing all data bytes """
        checksum = 0
        for b in frame:
            checksum ^= b
        #pad response to 8 bits
        return bytes([checksum & 0xFF])

    @staticmethod
    async def generateFrame(packet: LedPacket):
        """ returns transmittable frame bytes """
        #pad cmd to 8 bits
        cmd = packet.cmd & 0xFF
        #combine segments
        frame = bytes([packet.head, cmd]) + bytes(packet.payload)
        #pad frame data to 19 bytes (plus checksum)
        frame += bytes([0] * (19 - len(frame)))
        #add checksum to end
        frame += await GoveeUtils.generateChecksum(frame)
        return frame

    @staticmethod
    async def verifyChecksum(frame: bytes):
        checksum_received = frame[-1].to_bytes(1, 'big')
        checksum_calculated = await GoveeUtils.generateChecksum(frame[:-1])
        return checksum_received == checksum_calculated
