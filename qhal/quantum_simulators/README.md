# Instructions for installing MBQC simulator

The file `_mbqc_quantum_simulator.py` is designed to interface with [MBQC-sim](https://gitlab.com/johnrscott/mbqc-fpga/-/tree/master/) designed by John Scott. It produces a file `circuit.txt` which is read by the command line interface, and produces an output called `results.log`. It requires another quantum simulator, QSL.

Currently, in order to use our interface with the simulator, the following steps should be followed:

1. Install `g++-10` and `cmake`. You will also need to install [QSL](https://github.com/lanamineh/qsl) - instructions for how to install this on Linux are in the readme.
2. Run `sh mbqc-install.sh`. This will install MBQC-sim in the parent folder `QHAL_internal`.
3. You can then use the HAL as normal. Be aware that depending on how you are running it there may be errors caused by the paths specified - we use paths that start with `QHAL_internal/`.
4. For more information on the results contained in the log file please check the MBQC-sim documentation.
