import sys

for entry in sys.path:
    print(entry)

from lib import HardwareAbstractionLayer, ProjectqQuantumSimulator
from lib.hal import command_creator, measurement_unpacker

from numpy import pi as PI
#
# Shor's algorithm circuit
# 1+4 qubits example with k=3, N = 15, a = 11
#
n = 5 # 1 + number of bits used to represent N
k = 3 # number of QFT bits
c = [0,0,0] # declare classical bit register with QFT bits ordered from most significant(c[0]) to least significant (c[k-1])

# set up HAL using projectq backend for n qubits
hal = HardwareAbstractionLayer(
    ProjectqQuantumSimulator(n)
)

#initialise qubit register
hal.accept_command(command_creator("STATE_PREPARATION", 0, 0)) # TODO change to state prepare all

# prepare qubits register |00001>
hal.accept_command(command_creator("X", 0, n-1))

# Shor's algorithm loop
#------------------------------------------------
#------------------- k = 0 ----------------------
#------------------------------------------------
# Set QFT qubit to |+> state
hal.accept_command(command_creator("H", 0, 0))

# apply controlled (11^4)%15 = controlled 1%15
# nothing to do
# phase shift to apply depends on previous measurements
if (c[0] == 1):
    hal.accept_command(command_creator("RZ", PI/2,0))

if (c[1] == 1):
    hal.accept_command(command_creator("RZ", PI/4,0))

if (c[2] == 1):
    hal.accept_command(command_creator("RZ", PI/8,0))

hal.accept_command(command_creator("H", 0, 0))
# newest measurement outcome is associated with a pi/2 phase shift
# in the next iteration, so shift all bits of c to the right
c >>= 1

q_index,status,readout = hal.accept_command(command_creator("MEASURE", 0, 0)) 
c[0] = readout
# Reset qubit to |0> after measurement
hal.accept_command(command_creator("STATE_PREPARE", 0, 0))

#------------------------------------------------
#------------------- k = 1 ----------------------
#------------------------------------------------
# Set QFT qubit to |+> state
hal.accept_command(command_creator("H", 0, 0))

# apply controlled (11^2)%15 = controlled 1%15
# nothing to do
# phase shift to apply depends on previous measurements
if (c[0] == 1):
    hal.accept_command(command_creator("RZ", PI/2,0))

if (c[1] == 1):
    hal.accept_command(command_creator("RZ", PI/4,0))

if (c[2] == 1):
    hal.accept_command(command_creator("RZ", PI/8,0))

hal.accept_command(command_creator("H", 0, 0))
# newest measurement outcome is associated with a pi/2 phase shift
# in the next iteration, so shift all bits of c to the right
c >>= 1

q_index,status,readout = hal.accept_command(command_creator("MEASURE", 0, 0)) 
c[0] = readout
# Reset qubit to |0> after measurement
hal.accept_command(command_creator("STATE_PREPARE", 0, 0))

#------------------------------------------------
#------------------- k = 2 ----------------------
#------------------------------------------------
# Set QFT qubit to |+> state
hal.accept_command(command_creator("H", 0, 0))

# apply controlled (11^1)%15 = controlled 1%15
# cswap 0,2,4 START
hal.accept_command(command_creator("CNOT", 4, 2))

hal.accept_command(command_creator("H", 0, 4))
hal.accept_command(command_creator("CNOT", 2, 4))
hal.accept_command(command_creator("INVT", 0, 4))
hal.accept_command(command_creator("CNOT", 0, 4))
hal.accept_command(command_creator("T", 0, 4))
hal.accept_command(command_creator("CNOT", 2, 4))
hal.accept_command(command_creator("INVT", 0, 4))
hal.accept_command(command_creator("CNOT", 0, 4))
hal.accept_command(command_creator("T", 0, 2))
hal.accept_command(command_creator("T", 0, 4))
hal.accept_command(command_creator("H", 0, 4))
hal.accept_command(command_creator("CNOT", 0, 2))
hal.accept_command(command_creator("T", 0, 0))
hal.accept_command(command_creator("INVT", 0, 2))
hal.accept_command(command_creator("CNOT", 0, 2))

hal.accept_command(command_creator("CNOT", 4, 2))
# cswap 0,2,4 END

# cswap 0,1,3 START
hal.accept_command(command_creator("CNOT", 3, 1))

hal.accept_command(command_creator("H", 0, 4))
hal.accept_command(command_creator("CNOT", 1, 3))
hal.accept_command(command_creator("INVT", 0, 3))
hal.accept_command(command_creator("CNOT", 0, 3))
hal.accept_command(command_creator("T", 0, 3))
hal.accept_command(command_creator("CNOT", 1, 3))
hal.accept_command(command_creator("INVT", 0, 3))
hal.accept_command(command_creator("CNOT", 0, 3))
hal.accept_command(command_creator("T", 0, 1))
hal.accept_command(command_creator("T", 0, 3))
hal.accept_command(command_creator("H", 0, 3))
hal.accept_command(command_creator("CNOT", 0, 1))
hal.accept_command(command_creator("T", 0, 0))
hal.accept_command(command_creator("INVT", 0, 1))
hal.accept_command(command_creator("CNOT", 0, 1))

hal.accept_command(command_creator("CNOT", 3, 1))
# cswap 0,1,3 END

hal.accept_command(command_creator("CNOT", 0, 1))
hal.accept_command(command_creator("CNOT", 0, 2))
hal.accept_command(command_creator("CNOT", 0, 3))
hal.accept_command(command_creator("CNOT", 0, 4))

# phase shift to apply depends on previous measurements
if (c[0] == 1):
    hal.accept_command(command_creator("RZ", PI/2,0))

if (c[1] == 1):
    hal.accept_command(command_creator("RZ", PI/4,0))

if (c[2] == 1):
    hal.accept_command(command_creator("RZ", PI/8,0))

hal.accept_command(command_creator("H", 0, 0))
# newest measurement outcome is associated with a pi/2 phase shift
# in the next iteration, so shift all bits of c to the right
c >>= 1

q_index,status,readout = hal.accept_command(command_creator("MEASURE", 0, 0)) 
c[0] = readout
# Reset qubit to |0> after measurement
hal.accept_command(command_creator("STATE_PREPARE", 0, 0))


#------------------------------------------------
#------------------- DONE -----------------------
#------------------------------------------------
