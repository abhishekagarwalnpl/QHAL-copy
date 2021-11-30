import unittest
import itertools

from qhal.hal._commands import (command_creator,
                                command_unpacker,
                                measurement_creator,
                                measurement_unpacker,
                                _OPCODES)


class HALTest(unittest.TestCase):
    """Basic tests for HAL command creation and result validation.
    """
    def test_roundtrip_hal_commands(self):
        """Test roundtripping of the command packer/unpackers."""

        single_params = list(itertools.product(range(32), range(32), range(8)))
        dual_params = list(itertools.product(range(32), range(32), range(8), range(8)))

        for opcode in _OPCODES:
            if opcode.cmd_type == "SINGLE":
                for param_set in single_params:
                    self.assertEqual(command_unpacker(
                                        command_creator(
                                            opcode.name,
                                            [param_set[0], param_set[1]],
                                            [param_set[2]])),
                                        (opcode.name,
                                         opcode.cmd_type,
                                         [param_set[0], param_set[1]],
                                         [param_set[2]]))
            else:
                for param_set in dual_params:
                    self.assertEqual(command_unpacker(
                                        command_creator(
                                            opcode.name,
                                            [param_set[0], param_set[1]],
                                            [param_set[2], param_set[3]])),
                                        (opcode.name,
                                         opcode.cmd_type,
                                         [param_set[0], param_set[1]],
                                         [param_set[2], param_set[3]]))

    def test_measurement_creator_unpacker(self):
        """Tests measurement encoding is consistent between measurement creator
        and unpacker functions.
        """

        for idx in range(8):
            for offset in range(8):
                for status in range(8):
                    for res in range(2):
                        args = (idx, offset, status, res)
                        self.assertEqual(
                            args, 
                            measurement_unpacker(measurement_creator(*args))
                        )


if __name__ == "__main__":
    unittest.main()
