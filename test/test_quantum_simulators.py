import unittest

import numpy as np
from projectq.backends import Simulator

from test.quantum_simulators import ProjectqQuantumSimulator
from test.hal import command_creator, measurement_unpacker


class TestQuantumSimulators(unittest.TestCase):
    """
    Test that checks the projQ output by running a simple test circuit and
    checking that the final wavefunction is as expected.
    """

    def test_circuit_equivalence(self):

        # set the size of the register
        n_qubits = 3

        projQ_backend = ProjectqQuantumSimulator(
            register_size=n_qubits,
            seed=234,
            backend=Simulator
        )

        circuit = [
            ["STATE_PREPARATION_ALL", 0, 0],
            ['X', 0, 0],
            ['H', 0, 2],
            ["T", 0, 0],
            ["SX", 0, 1],
            ["T", 0, 2],
            ["S", 0, 2],
            ["SWAP", 0, 1, 0, 2],
            ["T", 0, 2],
            ["INVS", 0, 2],
            ['RZ', 672, 1],
            ['SQRT_X', 0, 0],
            ['PSWAP', 200, 0, 0, 1],
            ["CNOT", 0, 0, 0, 2],
            ["H", 0, 2],
            ["PIXY", 458, 1],
        ]

        for commands in circuit:

            hal_cmd = command_creator(*commands)
            projQ_backend.accept_command(hal_cmd)

        # extract wavefunction at the end of the circuit (before measuring)
        psi_projq = np.array(projQ_backend._engine.backend.cheat()[1])

        # send measure command to projQ backend (will complain if not flushed)
        projQ_backend.accept_command(command_creator(*['QUBIT_MEASURE', 0, 0]))

        self.assertEqual(
            list(psi_projq), [
                (-0.25903240188259363+0.24062879041156826j),
                (-0.20711081870608414+0.28653989037286853j),
                (0.349063763927275+0.05616483519893535j),
                (0.35331381736695744-0.013013318469484697j),
                (0.25903240188259363-0.24062879041156826j),
                (0.20711081870608414-0.28653989037286853j),
                (-0.349063763927275-0.05616483519893535j),
                (-0.35331381736695744+0.013013318469484697j)
            ]
        )

    def test_individual_qubit_measurements(self):

        projQ_backend = ProjectqQuantumSimulator(
            register_size=2,
            seed=234,
            backend=Simulator
        )

        circuit = [
            ["STATE_PREPARATION_ALL", 0, 0],
            ['X', 0, 0]
        ]

        for commands in circuit:

            hal_cmd = command_creator(*commands)
            projQ_backend.accept_command(hal_cmd)

        hal_res_0 = projQ_backend.accept_command(
            command_creator("QUBIT_MEASURE", 0, 0)
        )
        hal_res_1 = projQ_backend.accept_command(
            command_creator("QUBIT_MEASURE", 0, 1)
        )

        decoded_hal_result_0 = measurement_unpacker(hal_res_0)
        decoded_hal_result_1 = measurement_unpacker(hal_res_1)

        self.assertEqual(decoded_hal_result_0[0], 0)
        self.assertEqual(decoded_hal_result_0[2], 1)
        self.assertEqual(decoded_hal_result_1[0], 1)
        self.assertEqual(decoded_hal_result_1[2], 0)

    def test_measurement_failures(self):
        """Tests thats you can't measure the same qubit twice, or can't
        manipulate the qubit after measurement, but you can if you re-prepare
        the qubit state.
        """

        # single qubit
        projQ_backend = ProjectqQuantumSimulator(
            register_size=1,
            seed=234,
            backend=Simulator
        )

        circuit = [
            ["STATE_PREPARATION_ALL", 0, 0],
            ['X', 0, 0],
            ['QUBIT_MEASURE', 0, 0]
        ]

        for commands in circuit:

            hal_cmd = command_creator(*commands)
            projQ_backend.accept_command(hal_cmd)

        with self.assertRaises(ValueError):
            projQ_backend.accept_command(
                command_creator(*['QUBIT_MEASURE', 0, 0])
            )

        # multi qubit
        projQ_backend = ProjectqQuantumSimulator(
            register_size=2,
            seed=234,
            backend=Simulator
        )

        circuit = [
            ["STATE_PREPARATION_ALL", 0, 0],
            ['X', 0, 0],
            ['QUBIT_MEASURE', 0, 0]
        ]

        for commands in circuit:

            hal_cmd = command_creator(*commands)
            projQ_backend.accept_command(hal_cmd)

        # try double measurement
        with self.assertRaises(ValueError):
            projQ_backend.accept_command(
                command_creator(*['QUBIT_MEASURE', 0, 0])
            )

        # try manipulation after measurement
        with self.assertRaises(ValueError):
            projQ_backend.accept_command(
                command_creator(*['X', 0, 0])
            )

        # re-prepare state of qubit, then try bit-flip and measure
        projQ_backend.accept_command(
            command_creator(*['STATE_PREPARATION', 0, 0])
        )
        projQ_backend.accept_command(
            command_creator(*['X', 0, 0])
        )
        res = projQ_backend.accept_command(
            command_creator(*['QUBIT_MEASURE', 0, 0])
        )

        self.assertEqual(res, 1)

    def test_qubit_index_offset(self):
        """Tests that we can address qubit indices that exist
        """

        projQ_backend = ProjectqQuantumSimulator(
            register_size=10,
            seed=234,
            backend=Simulator,
            offset_register_weight=8  # offset qubit index = 0 as multiples of 8
        )

        circuit = [
            ["STATE_PREPARATION_ALL", 0, 0],
            ["PAGE_SET_QUBIT_0", 0, 1],  # set offset
            ['X', 0, 0]  # qubit index = 0 now refers to index = 8
        ]

        for commands in circuit:

            hal_cmd = command_creator(*commands)
            projQ_backend.accept_command(hal_cmd)

        res = measurement_unpacker(
            projQ_backend.accept_command(
                command_creator(*['QUBIT_MEASURE', 0, 0])
            )
        )

        self.assertEqual(res[0], 8)  # offset is still set
        self.assertEqual(res[2], 1)

    def test_unrecognised_opcode(self):
        """Tests that an unrecognised opcode causes a fail.
        """

        projQ_backend = ProjectqQuantumSimulator(
            register_size=1,
            seed=234,
            backend=Simulator
        )

        circuit = [
            ["STATE_PREPARATION_ALL", 0, 0],
            ['FAKE', 0, 0]
        ]

        with self.assertRaises(ValueError):
            for commands in circuit:

                hal_cmd = command_creator(*commands)
                projQ_backend.accept_command(hal_cmd)


if __name__ == "__main__":
    unittest.main()
