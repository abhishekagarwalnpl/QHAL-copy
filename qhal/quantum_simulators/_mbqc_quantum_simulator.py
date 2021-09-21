import atexit
import os

import numpy as np
from numpy import uint64
from numpy.random import RandomState

from _interface_quantum_simulator import IQuantumSimulator
from ..hal import command_unpacker, string_to_opcode

# This interface uses the simulator at https://gitlab.com/johnrscott/mbqc-fpga
#TODO: document properly
#TODO: work out interface with the C++
#TODO: full testing and debugging :)

class MBQCQuantumSimulator(IQuantumSimulator):
    """MBQC implementation of the IQuantumSimulator interface.

    Parameters
    ----------
    file_name : str
        Name of the circuit file.
    register_size : int
        Size of the qubit register.
    """

    def __init__(self,
            file_name : str = "circuit.txt",
            register_size : int = 4):

        self.file_name = file_name
        self._qubit_register_size = register_size
        self._qubit_register_initialised = False
        self._offset_registers = [0,0]

        self._const_gate_angles = {
            'H': [np.pi/2.0, np.pi/2.0, np.pi/2.0],
            'S': [0.0, 0.0, np.pi/2.0],
            'SQRT_X': [np.pi/2.0, 0.0, 0.0],
            'T': [0.0, 0.0, np.pi/4.0],
            'X': [np.pi, 0.0, 0.0],
            'Y': [-np.pi/2.0, np.pi, np.pi/2.0],
            'Z': [0.0, 0.0, np.pi],
            'INVT': [0.0, 0.0, -np.pi/4.0],
            'INVS': [0.0, 0.0, -np.pi/2.0],
            'SX': [np.pi, -np.pi/2.0, 0.0],
            'SY': [np.pi, np.pi/2.0, 0.0]
        }
    
        atexit.register(self.cleanup)
        # Is this the best way to do it? Or better to tie to a command?
        #TODO: adding functionality to delete/clean circuit file.

    #TODO: set_state/get_state

    def cleanup(self):
        """Run command to implement circuit."""
        os.system('mbqcsim -c {filename} -o results'.format(filename = self.file_name))
        #TODO: read results from log file 


    def get_offset(self, qubit_index: int):
        return self._offset_registers[qubit_index]

    def prepare_circuit(self):

        with open(self.file_name, 'w') as f:
            f.write('N={size}\n'.format(size = self._qubit_register_size))
        self._qubit_register_initialised = True


    def add_rotation(self, qubit_label : int, x1_angle : float, 
            z_angle : float, x2_angle : float):

        with open(self.file_name, 'w') as f:
            f.write('u {q0} {a1} {a2} {a3}\n'.format(q0 = qubit_label, 
                a1 = x1_angle, a2 = z_angle, a3 = x2_angle))


    def add_cnot(self, control_qubit : int, target_qubit: int):

        with open(self.file_name, 'w') as f:
            f.write('cnot {c} {t}\n'.format(c = control_qubit, t = target_qubit))
    
    #These replace the 'apply gate' function in the projectq sim

    def accept_command(
        self,
        command: uint64
    ) -> uint64:
        # Currently I don't think any of these actually give an output

        op, cmd_type, args, qubit_indexes = command_unpacker(command)
        op_obj = string_to_opcode(op)

        q_index_0 = qubit_indexes[0] + self.get_offset(0)
        q_index_1 = 0
        if len(qubit_indexes) > 1:
            q_index_1 = qubit_indexes[1] + self.get_offset(1)

        for index in qubit_indexes:
            assert index <= self._qubit_register_size, \
                f"Qubit index {index} greater than register size " + \
                f"({self._qubit_register_size})!"

        if op == "STATE_PREPARATION_ALL":
            if self_qubit_register_intialised == True:
                raise ValueError("Qubit register has already been initialised!")
            else:
                self.prepare_circuit()

        #TODO: Is qubit re-preparation something we can support with this simulator?
        elif op == "STATE_PREPARATION":
            raise ValueError("This command is not supported with this simulator. \n" + \
                    "Please use STATE_PREPARATION_ALL.")

        #TODO: QUBIT_MEASURE
        #--Understand how to process output of simulator.--

        # This bit is taken straight from the projectQ simulator so may need some adjustment.
        elif op.split("_")[0] == "PAGE":
            self._offset_registers[int(op.split("_")[3])] = qubit_indexes[0]

        elif op == "ID":
            pass

        elif op_obj.param == "PARAM":

            angle = args[-1]*(2*np.pi)/65536 #What is going on here?
        #These conversions might be better off going somewhere else
            if cmd_type == "SINGLE":

                if op == "RX":
                    self.add_rotation(q_index_0, angle, 0.0, 0.0)

                elif op == "RY":
                    self.add_rotation(q_index_0, -np.pi/2.0, angle, np.pi/2.0)

                elif op == "RZ":
                    self.add_rotation(q_index_0, 0.0, angle, 0.0)

                elif op == "PIXY":
                    self.add_rotation(q_index_0, np.pi, -2.0*angle, 0.0)

                elif op == "PIYZ":
                    self.add_rotation(q_index_0, 0.0, np.pi, 2.0*angle)

                elif op == "PIZX":
                    self.add_rotation(q_index_0, 0.0, np.pi, 2.0*angle)


            else:

                if op == "PSWAP":
                    self.add_cnot(q_index_0, q_index_1)
                    self.add_rotation(q_index_1, 0.0, angle, 0.0)
                    self.add_cnot(q_index_1, q_index_0)
                    self.add_cnot(q_index_0, q_index_1)

                elif op == "RXX":
                    self.add_cnot(q_index_0, q_index_1)
                    self.add_rotation(q_index_0, angle, 0.0, 0.0)
                    self.add_cnot(q_index_0, q_index_1)

                elif op == "RYY":
                    self.add_rotation(q_index_0, -np.pi/2, np.pi, 0.0)
                    self.add_rotation(q_index_1, -np.pi/2, np.pi, 0.0)
                    self.add_cnot(q_index_0, q_index_1)
                    self.add_rotation(q_index_1, 0.0, -angle, 0.0)
                    self.add_cnot(q_index_0, q_index_1)
                    self.add_rotation(q_index_0, 0.0, np.pi, np.pi/2.0)
                    self.add_rotation(q_index_1, 0.0, np.pi, np.pi/2.0)

                elif op == "RZZ":
                    self.add_cnot(q_index_0, q_index_1)
                    self.add_rotation(q_index_1, 0.0, angle, 0.0)
                    self.add_rotation(q_index_0, q_index_1)


        elif op_obj.param == "CONST":

            if cmd_type == "SINGLE":
                self.add_rotation(q_index_0, self._const_gate_angles[op][0], 
                    self._const_gate_angles[op][1], self._const_gate_angles[op][2])

            else:

                if op == "SWAP":
                    self.add_cnot(q_index_0, q_index_1)
                    self.add_cnot(q_index_1, q_index_0)
                    self.add_cnot(q_index_0, q_index_1)

        else:
            raise TypeError(f"{op} is not a recognised opcode!")



