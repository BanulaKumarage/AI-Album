#!/usr/bin/bash
set -ex

sudo apt install -y libavdevice-dev libavfilter-dev libavformat-dev 
sudo apt install -y libavcodec-dev libswresample-dev libswscale-dev  
sudo apt install -y libavutil-dev  
sudo apt install -y libopenblas-dev liblapack-dev

cwd=$(pwd)
nvcc=$(which nvcc)
nvcc --help &> /dev/null
cd dlib
if [ -d build ]; then rm -Rf build; fi
mkdir build
cd build
cmake .. -DDLIB_USE_CUDA=1 -DUSE_AVX_INSTRUCTIONS=1 -DCUDAToolkit_ROOT=$(dirname $(which nvcc))
cmake --build .
cd ..
python setup.py build --set DLIB_USE_CUDA=1