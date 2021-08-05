import atexit
import logging
from typing import Tuple

import numpy as np
from numpy import uint64
from numpy.random import RandomState

from projectq import MainEngine
from projectq.backends import Simulator
from projectq.ops import (All, C, CNOT, DaggeredGate, H, Measure, R,
                          Rx, Ry, Rz, S, SqrtX, Swap, T, X, Y, Z)
from projectq.ops._basics import BasicGate, BasicRotationGate

from . import IQuantumSimulator
from ..hal import command_unpacker, string_to_command


class SxGate(BasicGate):
    """Gate that consists of consecutive S and X gate
    (pi-rotation with axis in x-y-plane).
    """

    @property
    def matrix(self):
        return np.array([[0, 1], [1j, 0]])

    def __str__(self):
        return "SX"


#: Shortcut (instance of) :class:`projectq.ops.SxGate`
Sx = SxGate()


class SyGate(BasicGate):
    """Gate that consists of consecutive S and Y gate
    (pi-rotation with axis in x-y-plane).
    """

    @property
    def matrix(self):
        return np.array([[0, 1j], [1, 0]])

    def __str__(self):
        return "SY"


#: Shortcut (instance of) :class:`projectq.ops.SyGate`
Sy = SyGate()


class PiXY(BasicRotationGate):
    """Pi-rotation with axis in x-y-plane gate class."""

    @property
    def matrix(self):
        return np.array([[0, -np.sin(self.angle) - 1j * np.cos(self.angle)],
                         [np.sin(self.angle) - 1j * np.cos(self.angle), 0]])


class PiYZ(BasicRotationGate):
    """Pi-rotation with axis in y-z-plane gate class."""

    @property
    def matrix(self):
        return np.array([[np.cos(self.angle), -1j * np.sin(self.angle)],
                         [1j * np.sin(self.angle), -1 * np.cos(self.angle)]])


class PiZX(BasicRotationGate):
    """Pi-rotation with axis in z-x-plane gate class."""

    @property
    def matrix(self):
        return np.array([[np.cos(self.angle), np.sin(self.angle)],
                         [np.sin(self.angle), -1 * np.cos(self.angle)]])


class Pswap(BasicRotationGate):
    """Parameterised swap gate class."""

    @property
    def matrix(self):
        return np.array([[1, 0, 0, 0],
                        [0, 0, np.exp(1j * self.angle), 0],
                        [0, np.exp(1j * self.angle), 0, 0],
                        [0, 0, 0, 1]])


class ProjectqQuantumSimulator(IQuantumSimulator):
    """Concrete ProjectQ implementation of the IQuantumSimulator interface.

    Parameters
    ----------
    register_size: int
        Size of the qubit register.
    seed : int
        Random number generator seed for both the ProjectQ Simulator and
        circuit errors.
    backend
        ProjectQ backend, could use CircuitDrawer for debugging purposes.


    .. TODO::
        Add and example how to use it in a graph (without any simulator).
    """

    def __init__(self,
                 register_size: int = 16,
                 seed: int = None,
                 backend=Simulator):
        if backend == Simulator and seed is not None:
            self._engine = MainEngine(backend=Simulator(rnd_seed=seed))

        else:
            self._engine = MainEngine(backend=backend())
        self.backend = backend
        self.seed = seed

        # if random numbers are needed to simulate quantum noise use this
        # state in the following way self._random_state.rand()
        self._random_state = RandomState(seed)

        self._qubit_register = None
        self._measured_qubits = []

        # defaulted to 16 because the bitcode status return
        # has 16 bits assigned for measurement results.
        self._qubit_register_size = register_size

        # assign projectq gate to each opcode
        self._parameterised_gate_dict = {
            'CONTROL': C,
            'R': R,
            'RX': Rx,
            'RY': Ry,
            'RZ': Rz,
            'PIXY': PiXY,
            'PIYZ': PiYZ,
            'PIZX': PiZX,
            'PSWAP': Pswap
        }

        self._constant_gate_dict = {
            # SINGLE
            'H': H,
            'S': S,
            'SQRT_X': SqrtX,
            'T': T,
            'X': X,
            'Y': Y,
            'Z': Z,
            'INVT': DaggeredGate(T),
            'INVS': DaggeredGate(S),
            'SX': Sx,  # consecutive S and X gate, needed for RC
            'SY': Sy,  # consecutive S and Y gate, needed for RC
            # DUAL
            'CNOT': CNOT,
            'SWAP': Swap
        }
        atexit.register(self.cleanup)

    def __getstate__(self):
        # Copy the object's state from self.__dict__ which contains
        # all our instance attributes. Always use the dict.copy()
        # method to avoid modifying the original state.
        state = self.__dict__.copy()
        # Remove the engine has it generally unpickable.
        del state['_engine']
        return state

    def __setstate__(self, state):
        # Restore instance attributes (i.e., filename and lineno).
        self.__dict__.update(state)
        # Restore the engine
        if self.backend == Simulator and self.seed is not None:
            self._engine = MainEngine(backend=Simulator(rnd_seed=self.seed))
        else:
            self._engine = MainEngine(backend=self.backend())

    def cleanup(self):
        """Release all the qubits that haven't been handled yet."""
        if self._qubit_register is not None:
            All(Measure) | self._qubit_register
        self._engine.flush()

    def apply_gate(self,
                   gate: BasicGate,
                   qubit_index_0: int,
                   qubit_index_1: int = None,
                   parameter_0: float = None,
                   parameter_1: float = None):
        """Receives command information and implements the gate on the
        corresponding qubit.

        Parameters
        ----------
        gate : BasicGate
            ProjectQ gate to be applied.
        qubit_index : int
            Index of qubit for gate to be applied to.
        parameter : float
            Angle of gate if parametrised.
        """
        if self._qubit_register is not None:

            if qubit_index_1 is None:  # single qubit gate
                if parameter_0 is not None:
                    gate(parameter_0) | self._qubit_register[qubit_index_0]
                else:
                    gate | self._qubit_register[qubit_index_0]

            else:  # multi qubit gate
                if parameter_0 is not None:
                    gate(parameter_0) | (
                        self._qubit_register[qubit_index_1],
                        self._qubit_register[qubit_index_0]
                    )
                else:
                    gate | (
                        self._qubit_register[qubit_index_1],
                        self._qubit_register[qubit_index_0]
                    )

            self._engine.flush()

    def accept_command(
        self,
        command: Tuple[uint64, uint64]
    ) -> uint64:

        op, args, qubit_indexes = command_unpacker(command)
        op_obj = string_to_command(op)

        for index in qubit_indexes:
            assert index <= self._qubit_register_size, \
                f"Qubit index {index} greater than register size " + \
                f"({self._qubit_register_size})!"

        if op == "STATE_PREPARATION_ALL":
            if self._qubit_register is None:
                self._qubit_register = self._engine.allocate_qureg(
                    self._qubit_register_size
                )
                self._measured_qubits = []
            else:
                raise ValueError("Qubit register has already been initialised!")

        elif op == "STATE_PREPARATION":
            if self._qubit_register is None:
                self._qubit_register = self._engine.allocate_qureg(
                    self._qubit_register_size
                )
                self._measured_qubits = []
            elif qubit_indexes[0] in self._measured_qubits:
                if int(self._qubit_register[qubit_indexes[0]]):
                    X | self._qubit_register[qubit_indexes[0]]
                self._measured_qubits.remove(qubit_indexes[0])
            else:
                raise ValueError("QUbit already prepared!")

        elif op == "QUBIT_MEASURE":

            if qubit_indexes[0] in self._measured_qubits:
                raise ValueError("Qubit already measured!")

            # This measures a single qubit at the time.
            Measure | self._qubit_register[qubit_indexes[0]]
            self._engine.flush()

            measurement = int(self._qubit_register[qubit_indexes[0]])
            self._measured_qubits.append(qubit_indexes[0])

            if len(self._qubit_register) == len(self._measured_qubits):
                self._qubit_register = None

            # QUBIT INDEX [63-32] | STATUS [31-27] | PADDING [26-1] | VALUE [0]
            # TODO: add STATUS
            return (qubit_indexes[0] << 32) + measurement

        elif op == "ID":
            pass

        elif op_obj.param == "PARAM":
            if qubit_indexes[0] in self._measured_qubits:
                raise ValueError("Qubit requires re-preparation!")

            # convert from 16-bit representation of angle
            angle = args[-1] * (2 * np.pi) / 65536

            gate = self._parameterised_gate_dict[op]
            if op_obj.type == "SINGLE":
                self.apply_gate(gate, qubit_indexes[0], parameter_0=angle)
            else:
                self.apply_gate(
                    gate,
                    qubit_index_0=qubit_indexes[0],
                    qubit_index_1=qubit_indexes[1],
                    parameter_0=angle
                )

        elif op_obj.param == "CONST":
            if qubit_indexes[0] in self._measured_qubits:
                raise ValueError("Qubit requires re-preparation!")

            gate = self._constant_gate_dict[op]
            if op_obj.type == "SINGLE":
                self.apply_gate(gate, qubit_indexes[0])
            else:
                self.apply_gate(
                    gate,
                    qubit_index_0=qubit_indexes[0],
                    qubit_index_1=qubit_indexes[1]
                )
        else:
            raise TypeError(f"{op} is not a recognised opcode!")
