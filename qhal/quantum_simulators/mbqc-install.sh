cd /workdir
git clone https://gitlab.com/johnrscott/mbqc-fpga.git
cd mbqc-fpga/simulator/
mkdir build
cd build
cmake ..
cmake --build .
cd /workdir
mv /workdir/mbqc-fpga/simulator/build/bin/mbqcsim /workdir/qhal/quantum_simulators/mbqcsim  