from qhal import HardwareAbstractionLayer, ProjectqQuantumSimulator
from qhal.hal import command_creator, measurement_unpacker, HALMetadata

# set up HAL using projectq backend for 3 qubits
hal = HardwareAbstractionLayer(
    ProjectqQuantumSimulator(3),
    HALMetadata()
)

# prepare commands
circuit = [
    ["START_SESSION", 0, 0],
    ["STATE_PREPARATION", 0, 0],
    ['X', 0, 0],
    ['H', 0, 2],
    ["T", 0, 0],
    ["SX", 0, 1],
    ["T", 0, 2],
    ["S", 0, 2],
    ["SWAP", 1, 2],
    ["T", 0, 2],
    ["INVS", 0, 2],
    ['RZ', 672, 1],
    ['SQRT_X', 0, 0],
    ['PSWAP', 200, 0, 0, 1],
    ["CNOT", 0, 2],
    ["H", 0, 2],
    ["PIXY", 458, 1],
]

# send commands to HAL
for commands in circuit:

    hal_cmd = command_creator(*commands)
    hal.accept_command(hal_cmd)

# send measure command to HAL and get encoded HAL result
hal_result = hal.accept_command(command_creator(*['QUBIT_MEASURE', 0, 2]))
hal.accept_command(command_creator(*['END_SESSION', 0, 0]))

# decode hal result and print qubit index, status, readout
print(measurement_unpacker(hal_result))