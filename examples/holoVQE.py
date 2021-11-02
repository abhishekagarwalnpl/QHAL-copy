from qhal import HardwareAbstractionLayer, ProjectqQuantumSimulator
from qhal.hal import command_creator, measurement_unpacker
from qhal.hal._utils import angle_binary_representation
from numpy import pi as PI

INT_PI_BY_2 = angle_binary_representation(PI/2)
INT_MINUS_PI_BY_2 = angle_binary_representation(-PI/2)
#
# holoVQE circuit for XXZ spin chain energy calculation
# 1 physical qubit, 1 bond qubit 4 ‘burn in’ lattice sites
#
lattice_sites = 4 # number of ‘burn in’ state preparation lattice sites
c = [0,0,0,0] # declare classical bit register with 4 bits (4 measurement results stored)
theta = 1.234 # parameterised angle
int_theta = angle_binary_representation(theta)
int_minus_theta = angle_binary_representation(-theta)
# initialize qubit register
# set up HAL using projectq backend for 2 qubits (1 bond, 1 physical)
hal = HardwareAbstractionLayer(
    ProjectqQuantumSimulator(2)
)

hal.accept_command(command_creator("START_SESSION",0,0))
hal.accept_command(command_creator("STATE_PREPARATION_ALL",0,0))
# State preparation
for i in range(lattice_sites):
    # Apply G_theta
    hal.accept_command(command_creator("RX", INT_PI_BY_2,0))
    hal.accept_command(command_creator("RY", INT_PI_BY_2,1))
    hal.accept_command(command_creator("H", 0, 1))
    hal.accept_command(command_creator("CNOT", 0, 1))
    hal.accept_command(command_creator("H", 0, 1))
    hal.accept_command(command_creator("RX", int_minus_theta,0))
    hal.accept_command(command_creator("RY", int_theta,1))
    hal.accept_command(command_creator("H", 0, 1))
    hal.accept_command(command_creator("CNOT", 0, 1))
    hal.accept_command(command_creator("H", 0, 1))
    hal.accept_command(command_creator("RX", INT_MINUS_PI_BY_2,0))
    hal.accept_command(command_creator("RY", INT_MINUS_PI_BY_2,1))
    # Reset physical qubit
    q_index,index_offset,status,readout = measurement_unpacker(hal.accept_command(command_creator("QUBIT_MEASURE", 0, 1))) 
    hal.accept_command(command_creator("STATE_PREPARATION", 0, 1))
    # Apply G_theta_tilda
    hal.accept_command(command_creator("RX", INT_PI_BY_2,0))
    hal.accept_command(command_creator("RY", INT_PI_BY_2,1))
    hal.accept_command(command_creator("H", 0, 1))
    hal.accept_command(command_creator("CNOT", 0, 1))
    hal.accept_command(command_creator("H", 0, 1))
    hal.accept_command(command_creator("RX", int_minus_theta,0))
    hal.accept_command(command_creator("RY", int_theta,1))
    hal.accept_command(command_creator("H", 0, 1))
    hal.accept_command(command_creator("CNOT", 0, 1))
    hal.accept_command(command_creator("H", 0, 1))
    hal.accept_command(command_creator("RX", INT_MINUS_PI_BY_2,0))

    hal.accept_command(command_creator("RY", INT_MINUS_PI_BY_2,1))
    hal.accept_command(command_creator("X", 0,1))

    # Reset physical qubit
    q_index,index_offset,status,readout = measurement_unpacker(hal.accept_command(command_creator("QUBIT_MEASURE", 0, 1))) 
    hal.accept_command(command_creator("STATE_PREPARATION", 0, 1))

#Expectation value measurement
#Apply G_theta, measure in X basis, then reset physical qubit
hal.accept_command(command_creator("RX", INT_PI_BY_2,0))
hal.accept_command(command_creator("RY", INT_PI_BY_2,1))
hal.accept_command(command_creator("H", 0, 1))
hal.accept_command(command_creator("CNOT", 0, 1))
hal.accept_command(command_creator("H", 0, 1))
hal.accept_command(command_creator("RX", int_minus_theta,0))
hal.accept_command(command_creator("RY", int_theta,1))
hal.accept_command(command_creator("H", 0, 1))
hal.accept_command(command_creator("CNOT", 0, 1))
hal.accept_command(command_creator("H", 0, 1))
hal.accept_command(command_creator("RX", INT_MINUS_PI_BY_2,0))
hal.accept_command(command_creator("RY", INT_MINUS_PI_BY_2,1))
hal.accept_command(command_creator("H", 0,1))

q_index,index_offset,status,readout = measurement_unpacker(hal.accept_command(command_creator("QUBIT_MEASURE", 0, 1))) 
c[0] = readout
hal.accept_command(command_creator("STATE_PREPARATION", 0, 1))

#Apply G_theta_tilda, measure in X basis, then reset physical qubit
hal.accept_command(command_creator("RX", INT_PI_BY_2,0))
hal.accept_command(command_creator("RY", INT_PI_BY_2,1))
hal.accept_command(command_creator("H", 0, 1))
hal.accept_command(command_creator("CNOT", 0, 1))
hal.accept_command(command_creator("H", 0, 1))
hal.accept_command(command_creator("RX", int_minus_theta,0))
hal.accept_command(command_creator("RY", int_theta,1))
hal.accept_command(command_creator("H", 0, 1))
hal.accept_command(command_creator("CNOT", 0, 1))
hal.accept_command(command_creator("H", 0, 1))
hal.accept_command(command_creator("RX", INT_MINUS_PI_BY_2,0))
hal.accept_command(command_creator("RY", INT_MINUS_PI_BY_2,1))
hal.accept_command(command_creator("X", 0,1))
hal.accept_command(command_creator("H", 0,1))
q_index,index_offset,status,readout = measurement_unpacker(hal.accept_command(command_creator("QUBIT_MEASURE", 0, 1))) 
c[1] = readout
hal.accept_command(command_creator("STATE_PREPARATION", 0, 1))

#Apply G_theta, measure in Z basis, then reset physical qubit
hal.accept_command(command_creator("RX", INT_PI_BY_2,0))
hal.accept_command(command_creator("RY", INT_PI_BY_2,1))
hal.accept_command(command_creator("H", 0, 1))
hal.accept_command(command_creator("CNOT", 0, 1))
hal.accept_command(command_creator("H", 0, 1))
hal.accept_command(command_creator("RX", int_minus_theta,0))
hal.accept_command(command_creator("RY", int_theta,1))
hal.accept_command(command_creator("H", 0, 1))
hal.accept_command(command_creator("CNOT", 0, 1))
hal.accept_command(command_creator("H", 0, 1))
hal.accept_command(command_creator("RX", INT_MINUS_PI_BY_2,0))
hal.accept_command(command_creator("RY", INT_MINUS_PI_BY_2,1))

q_index,index_offset,status,readout = measurement_unpacker(hal.accept_command(command_creator("QUBIT_MEASURE", 0, 1))) 
c[2] = readout
hal.accept_command(command_creator("STATE_PREPARATION", 0, 1))

#Apply G_theta_tilda, measure in Z basis, then reset physical qubit
hal.accept_command(command_creator("RX", INT_PI_BY_2,0))
hal.accept_command(command_creator("RY", INT_PI_BY_2,1))
hal.accept_command(command_creator("H", 0, 1))
hal.accept_command(command_creator("CNOT", 0, 1))
hal.accept_command(command_creator("H", 0, 1))
hal.accept_command(command_creator("RX", int_minus_theta,0))
hal.accept_command(command_creator("RY", int_theta,1))
hal.accept_command(command_creator("H", 0, 1))
hal.accept_command(command_creator("CNOT", 0, 1))
hal.accept_command(command_creator("H", 0, 1))
hal.accept_command(command_creator("RX", INT_MINUS_PI_BY_2,0))
hal.accept_command(command_creator("RY", INT_MINUS_PI_BY_2,1))
hal.accept_command(command_creator("X", 0,1))

q_index,index_offset,status,readout = measurement_unpacker(hal.accept_command(command_creator("QUBIT_MEASURE", 0, 1))) 
c[3] = readout
hal.accept_command(command_creator("STATE_PREPARATION", 0, 1))


hal.accept_command(command_creator("END_SESSION",0,0))
#------------------------------------------------
#------------------- DONE -----------------------
#------------------------------------------------