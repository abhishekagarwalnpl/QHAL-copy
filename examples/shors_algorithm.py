from lib import HardwareAbstractionLayer, ProjectqQuantumSimulator
from lib.hal import command_creator, measurement_unpacker

from numpy import pi as PI


def angle_to_integer(angle):
    rescaled_angle = angle % 2*PI
    return int(1024*rescaled_angle / (2*PI))
INT_PI_BY_2 = angle_to_integer(PI/2)
INT_PI_BY_4 = angle_to_integer(PI/4)
INT_PI_BY_8 = angle_to_integer(PI/8)

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
hal.accept_command(command_creator("STATE_PREPARATION_ALL", 0, 0))

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
    hal.accept_command(command_creator("RZ", INT_PI_BY_2,0))

if (c[1] == 1):
    hal.accept_command(command_creator("RZ", INT_PI_BY_4,0))

if (c[2] == 1):
    hal.accept_command(command_creator("RZ", INT_PI_BY_8,0))

hal.accept_command(command_creator("H", 0, 0))
# newest measurement outcome is associated with a pi/2 phase shift
# in the next iteration, so shift all bits of c to the right
c.insert(0,0) # Add bit to the left
c.pop() # Remove rightmost bit

q_index,status,readout = measurement_unpacker(hal.accept_command(command_creator("QUBIT_MEASURE", 0, 0))) 
c[0] = readout
# Reset qubit to |0> after measurement
hal.accept_command(command_creator("STATE_PREPARATION", 0, 0))

#------------------------------------------------
#------------------- k = 1 ----------------------
#------------------------------------------------
# Set QFT qubit to |+> state
hal.accept_command(command_creator("H", 0, 0))

# apply controlled (11^2)%15 = controlled 1%15
# nothing to do
# phase shift to apply depends on previous measurements
if (c[0] == 1):
    hal.accept_command(command_creator("RZ", INT_PI_BY_2,0))

if (c[1] == 1):
    hal.accept_command(command_creator("RZ", INT_PI_BY_4,0))

if (c[2] == 1):
    hal.accept_command(command_creator("RZ", INT_PI_BY_8,0))

hal.accept_command(command_creator("H", 0, 0))
# newest measurement outcome is associated with a pi/2 phase shift
# in the next iteration, so shift all bits of c to the right
c.insert(0,0) # Add bit to the left
c.pop() # Remove rightmost bit

q_index,status,readout = measurement_unpacker(hal.accept_command(command_creator("QUBIT_MEASURE", 0, 0))) 
c[0] = readout
# Reset qubit to |0> after measurement
hal.accept_command(command_creator("STATE_PREPARATION", 0, 0))

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
    hal.accept_command(command_creator("RZ", INT_PI_BY_2,0))

if (c[1] == 1):
    hal.accept_command(command_creator("RZ", INT_PI_BY_4,0))

if (c[2] == 1):
    hal.accept_command(command_creator("RZ", INT_PI_BY_8,0))

hal.accept_command(command_creator("H", 0, 0))
# newest measurement outcome is associated with a pi/2 phase shift
# in the next iteration, so shift all bits of c to the right
c.insert(0,0) # Add bit to the left
c.pop() # Remove rightmost bit

q_index,status,readout = measurement_unpacker(hal.accept_command(command_creator("QUBIT_MEASURE", 0, 0))) 
c[0] = readout
# Reset qubit to |0> after measurement
hal.accept_command(command_creator("STATE_PREPARATION", 0, 0))


#------------------------------------------------
#------------------- DONE -----------------------
#------------------------------------------------
print(f'Noiseless outcome expected to be 000 with probablity 50% and 100 with probability 50%. 100 corresponds to the correct period r of 2.')
print(f'Output = {c}')