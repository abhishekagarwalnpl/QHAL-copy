from typing import Dict, Tuple

import numpy as np

from . import command_unpacker, string_to_opcode
from ..quantum_simulators import IQuantumSimulator


class HALMetadata:
    """Class for storing HAL metadata items in pre-defined form.
    """
    def __init__(
        self,
        num_qubits: int = 0,
        max_depth: int = 0,
        native_gates: Dict[int, Tuple[int, np.array]] = {},
        connectivity: np.array = np.array([])
    ):

        def _error_raiser(metadata_item: str) -> None:
            raise ValueError(
                f"Metadata item {metadata_item} inconsistent with other items!"
            )

        self.num_qubits = num_qubits
        if max_depth > 0 and num_qubits == 0:
            _error_raiser("max_depth")
        else:
            self.max_depth = max_depth
        self.native_gates = native_gates if \
            all([
                mat.shape[0] <= num_qubits for mat in
                [t[1] for t in native_gates.values()]
            ]) \
            else _error_raiser("native_gates")
        self.connectivity = connectivity if \
            connectivity.shape[0] == num_qubits \
            else _error_raiser("connectivity")


class HardwareAbstractionLayer:
    """Encapsulates a process which receives HAL commands and uses them to
    perform operations on a quantum device.

    Parameters
    ----------
    quantum_simulator : IQuantumSimulator
        Object with the IQuantumSimulator interface that accepts commands
        and returns measurement results.
    hal_metadata : HALMetadata
        Object that holds a series of metadata items using a pre-defined
        structure.
    """

    def __init__(
        self,
        quantum_simulator: IQuantumSimulator,
        hal_metadata: HALMetadata
    ):
        self._quantum_simulator = quantum_simulator

        # set up some of the metadata in correct format
        self._hal_metadata = hal_metadata
        self._encoded_metadata = {}
        self._final_mask = (1 << 60)

        self._encoded_metadata["NUM_QUBITS"] = \
            (1 << 61) + self._hal_metadata.num_qubits
        self._encoded_metadata["MAX_DEPTH"] = \
            (2 << 61) + self._hal_metadata.max_depth

        native_gates = {}
        for i, (gate, gate_data) in enumerate(hal_metadata.native_gates.items()):
            native_gates[i] = []

            native_gates[i].append(
                (3 << 61) +
                (i << 57) +
                (string_to_opcode(gate).code << 45) +
                gate_data[0]
            )

        self._encoded_metadata["NATIVE_GATES"] = native_gates

        # useful state flags
        self._metadata_index = 0
        self._previous_metadata_request = 0

    def accept_command(self, hal_command: np.uint64) -> np.uint64:
        """Interface for ``quantum_simulator.accept_command``.

        Parameters
        ----------
        command : uint64
            The HAL command to deconstruct and use to perform actions.

        Returns
        -------
        uint64
            Result of a measurement command or metadata request.
        """

        # check if we've receieved a metadata request
        opcode, _, param, idx = command_unpacker(hal_command)
        if opcode == "REQUEST_METADATA":

            if param[0] != self._previous_metadata_request:
                self._metadata_index == 0

            if param[0] == 1:
                return self._encoded_metadata["NUM_QUBITS"] + self._final_mask

            elif param[0] == 2:
                return self._encoded_metadata["MAX_DEPTH"] + self._final_mask

            elif param[0] == 3:
                self._previous_metadata_request = param[0]

                if len(self._encoded_metadata["NATIVE_GATES"]) == 0:
                    return (3 << 61) + self._final_mask

                gate_list = [
                    i[0] for i in list(
                        self._encoded_metadata["NATIVE_GATES"].values()
                    )
                ]

                data = gate_list[self._metadata_index]
                self._metadata_index += 1
                if self._metadata_index == len(gate_list):
                    data = data + self._final_mask   # add final flag
                    self._metadata_index = 0
                return data

            elif param[0] == 4:

                if len(self._hal_metadata.connectivity) == 0:
                    return (4 << 61) + self._final_mask

                if "CONNECTIVITY" not in self._encoded_metadata:

                    self._encoded_metadata["CONNECTIVITY"] = []

                    # get all non-zero off-diagonal indexes
                    row_col_indexes = np.transpose(
                        np.nonzero(np.triu(self._hal_metadata.connectivity, 1))
                    )

                    # build up 64-bit encoded response
                    encoded_indexes = 0
                    count = 2
                    for i, row_col in enumerate(row_col_indexes):

                        encoded_indexes += \
                            ((row_col[0] << 10) + row_col[1]) << (count * 20)
                        count -= 1

                        if count == -1 or i == len(row_col_indexes) - 1:
                            self._encoded_metadata["CONNECTIVITY"].append(
                                int(encoded_indexes) | (4 << 61)
                            )
                            encoded_indexes = 0
                            count = 2

                self._previous_metadata_request = param[0]

                data = self._encoded_metadata["CONNECTIVITY"][self._metadata_index]
                self._metadata_index += 1
                if self._metadata_index == \
                        len(self._encoded_metadata["CONNECTIVITY"]):
                    data = data + self._final_mask  # add final flag
                    self._metadata_index = 0
                return int(data)

            elif param[0] == 5:

                if len(self._encoded_metadata["NATIVE_GATES"]) == 0:
                    return (5 << 61) + self._final_mask

                gate_index = param[1] >> 13

                gate_data_list = self._encoded_metadata["NATIVE_GATES"][
                    gate_index
                ]

                if len(gate_data_list) == 1:

                    def error_rate_encoder(num: float) -> int:
                        exp = -1

                        while num - int(num) != 0:
                            if num < 1:
                                exp += 1
                            num = float(f'{num:.3g}') * 10

                        return (int(num) << 4) + exp

                    error_rate_matrix = self._hal_metadata.native_gates[
                        list(self._hal_metadata.native_gates.keys())[gate_index]
                    ][1]

                    # build up 64-bit encoded response
                    encoded_error_rates = 0
                    count = 3
                    for i, error_rate in enumerate(error_rate_matrix):

                        if type(error_rate) == np.ndarray:
                            for element in error_rate:
                                if element != 0:
                                    encoded_error_rate = error_rate_encoder(
                                        element
                                    )

                        else:
                            encoded_error_rate = error_rate_encoder(error_rate)

                        encoded_error_rates += \
                            int(encoded_error_rate) << (count * 14)
                        count -= 1

                        if count == -1 or i == len(error_rate_matrix) - 1:
                            gate_data_list.append(
                                (5 << 61) | int(encoded_error_rates)
                            )
                            encoded_indexes = 0
                            count = 2

                self._previous_metadata_request = param[0]

                data = gate_data_list[self._metadata_index + 1]
                if self._metadata_index == len(gate_data_list) - 2:
                    data = data + self._final_mask  # add final flag
                    self._metadata_index = 0
                else:
                    self._metadata_index += 1
                return int(data)

        else:
            return self._quantum_simulator.accept_command(hal_command)
