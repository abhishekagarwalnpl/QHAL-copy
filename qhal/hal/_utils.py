import numpy as np


def angle_binary_representation(angle: float) -> int:
    """Converts an angle in radians to a 16-bit representation.

    Parameters
    ----------
    angle : float
        The angle (in radians) to be converted.

    Returns
    -------
    int
        16-bit representation of angle.
    """
    return int(np.rint((angle % (2*np.pi)) / (2 * np.pi / 2**16)))


def binary_angle_conversion(binary: int) -> float:
    """Converts a binary representation to an angle.
    HAL commands typically contain 16-bit unsigned integers, although
    this function accepts integers outside that range.

    Parameters
    ----------
    binary : int
        The binary representation to be converted.

    Returns
    -------
    float
        The angle (in radians).
    """
    return float(binary * (2 * np.pi / 2**16))
