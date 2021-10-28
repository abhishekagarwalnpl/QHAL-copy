import unittest

import numpy as np

from qhal.hal import command_creator, HALMetadata, HardwareAbstractionLayer
from qhal.quantum_simulators import IQuantumSimulator


class MockQuantumSimulator(IQuantumSimulator):

    def __init__(self) -> None:
        super().__init__()

    def accept_command(cls, command: np.uint64) -> np.uint64:
        return super().accept_command(command)


class HALMetadataTest(unittest.TestCase):
    """Tests for HAL metadata encoding/decoding.
    """

    def test_metadata_encoding_decoding(self):
        """Tests metadata encoding is consistent between HAL object creation
        and metadata request commands.



        """
        test_input_output_data = [
            (  # NUM_QUBITS - metadata index 1 (001)
                5,  # input data
                [3458764513820540933]  # expected output for metadata req 001
            ),
            (  # MAX_DEPTH - metadata index 2 (010)
                1000,  # input data
                [5764607523034235880]  # expected output for metadata req 010
            ),
            (  # NATIVE_GATES (gate time, error rates) - metadata index 3/5 (011/101)
                # input data
                {
                    "RX": (100, np.array([0.014, 0.015, 0.013, 0.014, 0.012])),
                    "RY": (200, np.array([0.019, 0.017, 0.016, 0.018])),
                    "RZ": (200, np.array([0.015, 0.016, 0.016, 0.017])),
                    "CNOT": (1000, np.array(
                        [
                            [0, 0.02, 0, 0],
                            [0.03, 0, 0.03, 0],
                            [0, 0.05, 0, 0.04],
                            [0, 0, 0.02, 0]
                        ]
                    ))
                },
                # expected output for metadata req 011
                [
                    6953909668380934244,
                    7098060040828879048,
                    7242210413276823752,
                    8576964752838755304
                ],
                # expected output for metadata req 101
                [
                    [11530204671229837537, 12683126227644727521],
                    [12683478028148293921],
                    [12683196548876615953],
                    [12682281699364585505]
                ]
            ),
            (  # CONNECTIVITY - metadata index 4 (100)
                # input data
                np.array(
                    [
                        [1, 1, 0, 0, 0],
                        [1, 1, 1, 0, 0],
                        [0, 1, 1, 1, 0],
                        [0, 0, 1, 1, 1],
                        [0, 0, 0, 1, 1]
                    ]
                ),
                # expected output for metadata req 100
                [9223373137442244611, 10379675639228661760]
            ),
            (  # ERROR_RATES - metadata index 5 (101)
                # input data already given in NATIVE_GATES
                [0, 0, 1, 2, 3],
                [
                    11530204671229837537,  # gate 0
                    12683126227644727521,  # gate 0
                    12683478028148293921,  # gate 1
                    12683196548876615953,  # gate 2
                    12682281699364585505  # gate 3
                ]
            )
        ]

        hal = HardwareAbstractionLayer(
            MockQuantumSimulator(),
            HALMetadata(*[i[0] for i in test_input_output_data[:4]])
        )

        for metadata_index in range(1, 6):  # metadata indexes = 1 -> 5

            output_count = 0  # keep track of the output stream for given index

            # poll HAL with metadata reqs for index until receives final flags
            while True:

                res = hal.accept_command(
                    command_creator(
                        "REQUEST_METADATA",
                        arg0=metadata_index,
                        arg1=(
                            test_input_output_data[4][0][output_count] << 13
                            if metadata_index == 5 else 0
                        )
                    )
                )

                self.assertEqual(
                    res,
                    test_input_output_data[metadata_index - 1][1][output_count]
                )

                output_count += 1

                if (res >> 61) == metadata_index and (res >> 60) & 1:
                    break

    def test_default_values(self):
        """Tests that when no values are specified for the HALMetadata then
        the result returned is just a header with empty payload
        (index << 61) + (1 << 60).
        """

        hal = HardwareAbstractionLayer(
            MockQuantumSimulator(),
            HALMetadata()
        )

        for metadata_index in range(1, 6):

            res = hal.accept_command(
                command_creator("REQUEST_METADATA", arg0=metadata_index)
            )

            self.assertEqual(
                res,
                (metadata_index << 61) + (1 << 60)
            )


if __name__ == "__main__":
    unittest.main()
