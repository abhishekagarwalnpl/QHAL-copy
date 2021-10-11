cd ../..
git clone https://gitlab.com/johnrscott/mbqc-fpga.git
cd mbqc-fpga/simulator/
mkdir build
cd build
CC=gcc-10 CXX=g++-10 cmake ..
cmake --build .
cd ../../..
mv ./mbqc-fpga/simulator/build/bin/mbqcsim ./qhal/quantum_simulators/mbqcsim  
