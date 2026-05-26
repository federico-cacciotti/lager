import math
import logging

import Drones.DJI_M600.parameters as params

log = logging.getLogger(__name__)

def crc16(data: bytes) -> int:
    """
    Compute CRC-16-CCITT (XModem) over the given data.
    
    Parameters:
    -----------
    data: bytes
        The input data for which the CRC16 checksum is to be computed.

    Returns:
    --------
    int
        The computed CRC16 checksum as an integer.
    """
    crc = params.CRC_INIT
    for b in data:
        crc = (crc >> 8) ^ params.CRC16_TAB[(crc ^ b) & 0xFF]
    return crc & 0xFFFF

def crc32(data: bytes) -> int:
    """
    Compute CRC-32 (IEEE 802.3) over the given data.

    Parameters:
    -----------
    data: bytes
        The input data for which the CRC32 checksum is to be computed.

    Returns:
    --------
    int
        The computed CRC32 checksum as an integer.
    """
    crc = params.CRC_INIT
    for b in data:
        crc = (crc >> 8) ^ params.CRC32_TAB[(crc ^ b) & 0xFF]
    return crc & 0xFFFFFFFF


def quat_to_euler(q0: float, q1: float, q2: float, q3: float) -> tuple:
    """
    Convert quaternion (q0=w, q1=x, q2=y, q3=z) to (roll, pitch, yaw) in degrees.
    Parameters:
    -----------
    q0, q1, q2, q3: float
        The components of the quaternion.
    Returns:
    --------
    tuple
        A tuple containing the Euler angles (roll, pitch, yaw) in degrees.
    """
    sinr_cosp = 2 * (q0 * q1 + q2 * q3)
    cosr_cosp = 1 - 2 * (q1 * q1 + q2 * q2)
    roll = math.atan2(sinr_cosp, cosr_cosp)

    sinp = 2 * (q0 * q2 - q3 * q1)
    pitch = math.copysign(math.pi / 2, sinp) if abs(sinp) >= 1 else math.asin(sinp)

    siny_cosp = 2 * (q0 * q3 + q1 * q2)
    cosy_cosp = 1 - 2 * (q2 * q2 + q3 * q3)
    yaw = math.atan2(siny_cosp, cosy_cosp)

    return math.degrees(roll), math.degrees(pitch), math.degrees(yaw)
