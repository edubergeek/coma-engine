FROM ubuntu:24.04

RUN apt-get update && apt-get install -y --no-install-recommends wget build-essential curl
RUN apt-get install -y gfortran libgfortran5 pgplot5 libfftw3-double3 libfftw3-single3 

# Install cfitsio and friends 
RUN apt-get install -y libcfitsio-bin libcfitsio-dev libcfitsio10t64

# Install TERAPIX reqs and other astro sw via astromatic  
RUN apt-get install -y source-extractor swarp scamp libatlas-base-dev libblas-dev liblapack-dev

# Compile and install SLALIB from C++ port (slalib-cpp)
WORKDIR /usr/local/src
RUN apt-get install -y git cmake && \
  git clone --depth 1 https://github.com/cyberhull/slalib-cpp.git && \
  cd slalib-cpp && \
  mkdir build && cd build && \
  cmake -DBUILD_SHARED_LIBS=ON .. && \
  make && \
  cp lib/libslalib.so /usr/local/lib/libslalib.so && \
  ldconfig && \
  cd /usr/local/src && rm -rf slalib-cpp

# Install SBCL
RUN apt-get install -y sbcl

WORKDIR /usr/local/src
COPY cdsclient.tar.gz .
RUN tar xzf cdsclient.tar.gz
WORKDIR /usr/local/src/cdsclient-3.84
RUN ./configure && make && make install

WORKDIR /root
COPY ./coma-json-server .

