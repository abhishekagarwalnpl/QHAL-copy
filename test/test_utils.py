import numpy as np
import unittest

from qhal.hal._utils import (angle_binary_representation,
                             binary_angle_conversion)


class UtilsTest(unittest.TestCase):
    """Basic tests for HAL util functions.
    """

    def test_angle_binary_conversion(self):
        """Test the conversion of angles to 16-bit representation."""

        test_cases = {
            0: angle_binary_representation(0),
            8192: angle_binary_representation(np.pi/4),
            10923: angle_binary_representation(np.pi/3),
            16384: angle_binary_representation(np.pi/2),
            21845: angle_binary_representation(2 * np.pi/3),
            24576: angle_binary_representation(3 * np.pi/4),
            32768: angle_binary_representation(np.pi),
            40960: angle_binary_representation(5 * np.pi/4),
            43691: angle_binary_representation(4 * np.pi/3),
            49152: angle_binary_representation(3 * np.pi/2),
            54613: angle_binary_representation(5 * np.pi/3),
            57344: angle_binary_representation(7 * np.pi/4),
            0: angle_binary_representation(2 * np.pi),
            8192: angle_binary_representation(2 * np.pi + np.pi/4),
            32768: angle_binary_representation(2 * np.pi + np.pi),
            57344: angle_binary_representation(2 * np.pi + 7 * np.pi/4),
            0: angle_binary_representation(-2 * np.pi),
            8192: angle_binary_representation(-7 * np.pi/4),
            32768: angle_binary_representation(-np.pi),
            57344: angle_binary_representation(-np.pi/4),
        }

        for expected, calculated in test_cases.items():
            self.assertEqual(expected, calculated)


    def test_angle_binary_roundtrip(self):
        """Test that conversions between angle and binary and 
           back again give the same results.
        """

        binary_tests = [0, 8192, 10923, 16384, 21845, 24576, 
                        32768, 40960, 43691, 49152, 54613, 57344]
        angle_tests = [0, np.pi/4, np.pi/3, np.pi/2, 2*np.pi/3,
                       3*np.pi/4, np.pi, 5*np.pi/4, 4*np.pi/3,
                       3*np.pi/2, 5*np.pi/3, 7*np.pi/4]

        for bin_rep in binary_tests:
            self.assertEqual(angle_binary_representation(
                             binary_angle_conversion(bin_rep)),
                             bin_rep)

        for angle in angle_tests:
            self.assertAlmostEqual(binary_angle_conversion(
                             angle_binary_representation(angle)),
                             angle, places=4)
            #Binary to angle is not exact


if __name__ == "__main__":
    unittest.main()
