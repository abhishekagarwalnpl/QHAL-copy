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

    def test_binary_to_angle_conversion(self):
        """Test the conversion of 16-bit binary to angles.
           Note that the conversion is only accurate up to 4 d.p."""

        # We also test some values outside of the usual 16-bit 
        # uint that the HAL would expect, as the conversion
        # is still accurate and these are sometimes useful.

        test_cases = {
            0: binary_angle_conversion(0),
            np.pi/4: binary_angle_conversion(8192),
            np.pi/3: binary_angle_conversion(10923),
            np.pi/2: binary_angle_conversion(16384),
            2 * np.pi/3: binary_angle_conversion(21845),
            3 * np.pi/4: binary_angle_conversion(24576),
            np.pi      : binary_angle_conversion(32768),
            5 * np.pi/4: binary_angle_conversion(40960),
            4 * np.pi/3: binary_angle_conversion(43691),
            3 * np.pi/2: binary_angle_conversion(49152),
            5 * np.pi/3: binary_angle_conversion(54613),
            7 * np.pi/4: binary_angle_conversion(57344),
            2 * np.pi: binary_angle_conversion(65536),
            2 * np.pi + np.pi/4: binary_angle_conversion(73728),
            2 * np.pi + np.pi: binary_angle_conversion(98304),
            2 * np.pi + 7 * np.pi/4: binary_angle_conversion(122880),
            -2 * np.pi: binary_angle_conversion(-65536),
            -7 * np.pi/4: binary_angle_conversion(-57344),
            -np.pi: binary_angle_conversion(-32768),
            -np.pi/4: binary_angle_conversion(-8192),
        }

        for expected, calculated in test_cases.items():
            self.assertAlmostEqual(expected, calculated, places=4)



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
