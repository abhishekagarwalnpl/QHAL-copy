import unittest

import numpy as np
from projectq import MainEngine
from projectq.ops import (All, C, CNOT, DaggeredGate, H, Measure, R,
                          Rx, Ry, Rz, S, SqrtX, Swap, T, X, Y, Z,
                          Rxx, Rzz)
from projectq.backends import Simulator

from qhal.quantum_simulators import ProjectqQuantumSimulator
from qhal.hal import (command_creator, measurement_unpacker,
                      angle_binary_representation, binary_angle_conversion)


class MockProjectqQuantumSimulator(ProjectqQuantumSimulator):

    def get_offset(self, qubit_index: int):
        return self._offset_registers[qubit_index] * 10


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

        hal_circuit = [
            ["START_SESSION", 0, 0],
            ["STATE_PREPARATION_ALL", 0, 0],
            ['X', 0, 0],
            ['H', 0, 1],
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
            ["PIXY", 458, 2],
        ]

        for commands in hal_circuit:
            hal_cmd = command_creator(*commands)
            projQ_backend.accept_command(hal_cmd)

        # extract wavefunction at the end of the circuit (before measuring)
        psi_projq_hal = np.array(projQ_backend._engine.backend.cheat()[1])
        projQ_backend.accept_command(command_creator(*['END_SESSION', 0, 0]))

        projQ_eng = MainEngine()
        projQ_register = projQ_eng.allocate_qureg(n_qubits)
        qubit0 = projQ_register[0]
        qubit1 = projQ_register[1]
        qubit2 = projQ_register[2]

        pq_circuit = [
            (X, qubit0),
            (H, qubit1),
            (T, qubit0),
            (X, qubit1),
            (S, qubit1),
            (T, qubit2),
            (S, qubit2),
            (Swap, (qubit1, qubit2)),
            (T, qubit2),
            (DaggeredGate(S), qubit2),
            (Rz(binary_angle_conversion(672)), qubit1),
            (SqrtX, qubit0),
            ### PSWAP:
            (CNOT, (qubit1, qubit0)),
            (R(binary_angle_conversion(200)), qubit0),
            (CNOT, (qubit0, qubit1)),
            (CNOT, (qubit1, qubit0)),
            ###
            (CNOT, (qubit2, qubit0)),
            (H, qubit2),
            (Rz(binary_angle_conversion(-2*458)), qubit2),
            (Rx(binary_angle_conversion(32768)), qubit2)
        ]

        for command in pq_circuit:
            command[0] | command[1]
            projQ_eng.flush()

        psi_projq_sim = np.array(projQ_eng.backend.cheat()[1])
        All(Measure) | projQ_register
        projQ_eng.flush()

        for n, i in enumerate(list(psi_projq_sim)):
            self.assertAlmostEqual(i, list(psi_projq_hal)[n], places=10)

    def test_individual_qubit_measurements(self):

        projQ_backend = ProjectqQuantumSimulator(
            register_size=2,
            seed=234,
            backend=Simulator
        )

        circuit = [
            ["START_SESSION", 0, 0],
            ["STATE_PREPARATION_ALL", 0, 0],
            ['X', 0, 0]
        ]

        for commands in circuit:

            hal_cmd = command_creator(*commands)
            projQ_backend.accept_command(hal_cmd)

        hal_res_0 = projQ_backend.accept_command(
            command_creator("QUBIT_MEASURE", 0, 0, 0)
        )
        hal_res_1 = projQ_backend.accept_command(
            command_creator("QUBIT_MEASURE", 0, 1, 0)
        )

        decoded_hal_result_0 = measurement_unpacker(hal_res_0)
        decoded_hal_result_1 = measurement_unpacker(hal_res_1)

        self.assertEqual(decoded_hal_result_0[0], 0)
        self.assertEqual(decoded_hal_result_0[3], 1)
        self.assertEqual(decoded_hal_result_1[0], 1)
        self.assertEqual(decoded_hal_result_1[3], 0)

    def test_variable_basis_measurement(self):
        """Tests that measuring in a rotated basis is equivalent
        to a rotation then measurement in the computational basis.
        """

        n = 4

        projQ_backend = ProjectqQuantumSimulator(
            register_size=n,
            seed=234,
            backend=Simulator
        )

        projQ_backend.accept_command(command_creator("START_SESSION", 0, 0))
        projQ_backend.accept_command(command_creator("STATE_PREPARATION_ALL", 0, 0))

        list_arg0 = [0, 458, 0, 672]
        list_arg1 = [0, 0, 234, 458]

        for i in range(n):
            projQ_backend.accept_command(command_creator("RY", list_arg0[i], i))
            projQ_backend.accept_command(command_creator("RZ", list_arg1[i], i))
            hal_res = projQ_backend.accept_command(command_creator("QUBIT_MEASURE", list_arg0[i], i, list_arg1[i]))
            decoded_hal_result = measurement_unpacker(hal_res)
            self.assertEqual(decoded_hal_result[3], 0)


    def test_measurement_failures(self):
        """Tests that you can't measure the same qubit twice, or can't
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
            ["START_SESSION", 0, 0],
            ["STATE_PREPARATION_ALL", 0, 0],
            ['X', 0, 0],
            ['QUBIT_MEASURE', 0, 0]
        ]

        for commands in circuit:

            hal_cmd = command_creator(*commands)
            projQ_backend.accept_command(hal_cmd)

        with self.assertRaises(ValueError):
            projQ_backend.accept_command(
                command_creator(*['QUBIT_MEASURE', 0, 0, 0])
            )
        projQ_backend.accept_command(command_creator(*['END_SESSION', 0, 0]))

        # multi qubit
        projQ_backend = ProjectqQuantumSimulator(
            register_size=2,
            seed=234,
            backend=Simulator
        )

        circuit = [
            ["START_SESSION", 0, 0],
            ["STATE_PREPARATION_ALL", 0, 0],
            ['X', 0, 0],
            ['QUBIT_MEASURE', 0, 0, 0]
        ]

        for commands in circuit:

            hal_cmd = command_creator(*commands)
            projQ_backend.accept_command(hal_cmd)

        # try double measurement
        with self.assertRaises(ValueError):
            projQ_backend.accept_command(
                command_creator(*['QUBIT_MEASURE', 0, 0, 0])
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
            command_creator(*['QUBIT_MEASURE', 0, 0, 0])
        )

        self.assertEqual(res, 1)

        projQ_backend.accept_command(command_creator(*['END_SESSION', 0, 0]))

    def test_qubit_index_offset(self):
        """Tests that we can address qubit indices that exist
        """

        projQ_backend = MockProjectqQuantumSimulator(
            register_size=11,
            seed=234,
            backend=Simulator)

        circuit = [
            ["START_SESSION", 0, 0],
            ["STATE_PREPARATION_ALL", 0, 0],
            ["PAGE_SET_QUBIT_0", 0, 1],  # set offset
            ['X', 0, 0]  # qubit index = 0 now refers to index = 10
        ]

        for commands in circuit:

            hal_cmd = command_creator(*commands)
            projQ_backend.accept_command(hal_cmd)

        res = measurement_unpacker(
            projQ_backend.accept_command(
                command_creator(*['QUBIT_MEASURE', 0, 0, 0])
            )
        )

        self.assertEqual(res[0], 0)
        self.assertEqual(res[1], 1)  # offset is still set
        self.assertEqual(res[3], 1)

        projQ_backend.accept_command(command_creator(*['END_SESSION', 0, 0]))

    def test_unrecognised_opcode(self):
        """Tests that an unrecognised opcode causes a fail.
        """

        projQ_backend = ProjectqQuantumSimulator(
            register_size=1,
            seed=234,
            backend=Simulator
        )

        circuit = [
            ["START_SESSION", 0, 0],
            ["STATE_PREPARATION_ALL", 0, 0],
            ['FAKE', 0, 0]
        ]

        with self.assertRaises(ValueError):
            for commands in circuit:
                hal_cmd = command_creator(*commands)
                projQ_backend.accept_command(hal_cmd)
        
        projQ_backend.accept_command(command_creator(*['END_SESSION', 0, 0]))

    def test_error_op_after_end_session(self):
        projQ_backend = ProjectqQuantumSimulator(
            register_size=2,
            seed=234,
            backend=Simulator
        )

        projQ_backend.accept_command(command_creator("START_SESSION", 0, 0))
        projQ_backend.accept_command(command_creator("END_SESSION", 0, 0))

        with self.assertRaises(AttributeError):
            projQ_backend.accept_command(command_creator("STATE_PREPARATION_ALL", 0, 0))

    def test_start_session_after_end_session(self):
        projQ_backend = ProjectqQuantumSimulator(
            register_size=2,
            seed=234,
            backend=Simulator
        )

        projQ_backend.accept_command(command_creator("START_SESSION", 0, 0))
        with self.assertRaises(ValueError):
            projQ_backend.accept_command(command_creator("START_SESSION", 0, 0))
        projQ_backend.accept_command(command_creator("END_SESSION", 0, 0))

        circuit = [
            ["START_SESSION", 0, 0],
            ["STATE_PREPARATION_ALL", 0, 0],
            ['H', 0, 0],
            ['X', 0, 1],
            ['CNOT', 0, 0, 0, 1],
        ]
        
        for commands in circuit:
            hal_cmd = command_creator(*commands)
            projQ_backend.accept_command(hal_cmd)

        hal_res_0 = projQ_backend.accept_command(
            command_creator("QUBIT_MEASURE", 0, 0, 0)
        )
        hal_res_1 = projQ_backend.accept_command(
            command_creator("QUBIT_MEASURE", 0, 1, 0)
        )

        decoded_hal_result_0 = measurement_unpacker(hal_res_0)
        decoded_hal_result_1 = measurement_unpacker(hal_res_1)

        self.assertEqual(decoded_hal_result_0[0], 0)
        self.assertEqual(decoded_hal_result_1[0], 1)
        self.assertEqual((decoded_hal_result_0[3] + decoded_hal_result_1[3]), 1)

        projQ_backend.accept_command(command_creator("END_SESSION", 0, 0))

if __name__ == "__main__":
    unittest.main()
