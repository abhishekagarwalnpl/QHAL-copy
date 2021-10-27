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
            (5, [3458764513820540933]),  # NUM_QUBITS
            (1000, [5764607523034235880]),  # MAX_DEPTH
            (  # NATIVE_GATES (gate time, error rates)
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
                [
                    6953909668380934244,
                    7098060040828879048,
                    7242210413276823752,
                    8576964752838755304
                ],
                [
                    [11530204671229837537, 12683126227644727521],
                    [12683478028148293921],
                    [12683196548876615953],
                    [12682281699364585505]
                ]
            ),
            (  # CONNECTIVITY
                np.array(
                    [
                        [1, 1, 0, 0, 0],
                        [1, 1, 1, 0, 0],
                        [0, 1, 1, 1, 0],
                        [0, 0, 1, 1, 1],
                        [0, 0, 0, 1, 1]
                    ]
                ),
                [9223373137442244611, 10379675639228661760]
            )
        ]

        hal = HardwareAbstractionLayer(
            MockQuantumSimulator(),
            HALMetadata(*[i[0] for i in test_input_output_data[:4]])
        )

        for metadata_index in range(1, len(test_input_output_data) + 2):

            output_count = 0
            i = 0

            while True:

                res = hal.accept_command(
                    command_creator(
                        "REQUEST_METADATA",
                        arg0=metadata_index,
                        arg1=(output_count << 13 if metadata_index == 5 else 0)
                    )
                )

                self.assertEqual(
                    res,
                    (
                        test_input_output_data[2][2][output_count][i] if metadata_index == 5
                        else test_input_output_data[metadata_index - 1][1][output_count]
                    )
                )

                if metadata_index == 5:
                    i += 1
                else:
                    output_count += 1

                if (res >> 61) == metadata_index and (res >> 60) & 1:
                    if metadata_index == 5 and \
                       output_count < len(test_input_output_data[2][2]) - 1:
                        output_count += 1
                        i = 0
                        continue
                    else:
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
