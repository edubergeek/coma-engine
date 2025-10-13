FROM ubuntu:24.04

RUN apt-get update && apt-get install -y --no-install-recommends wget build-essential curl git ca-certificates
RUN apt-get install -y gfortran libgfortran5 pgplot5 libfftw3-double3 libfftw3-single3
# Additional libraries needed for compilation of cftisio quirks
RUN apt-get install -y zlib1g-dev libcurl4-openssl-dev

# ------------------------------------------------------------------
# Build and install CFITSIO with reentrant (thread-safe) support
# ------------------------------------------------------------------
WORKDIR /usr/local/src

RUN wget https://heasarc.gsfc.nasa.gov/FTP/software/fitsio/c/cfitsio_latest.tar.gz --no-check-certificate && \
  tar xzf cfitsio_latest.tar.gz && \
  cd cfitsio-* && \
  ./configure --prefix=/usr/local --enable-reentrant --enable-shared  && \
  make -j"$(nproc)" && \
  make install && \
  ldconfig && \
  cd /usr/local/src && rm -rf cfitsio cfitsio_latest.tar.gz

# Install TERAPIX reqs and other astro sw via astromatic  
RUN apt-get install -y source-extractor swarp scamp libatlas-base-dev libblas-dev liblapack-dev

# Compile and install SLALIB from C++ port (slalib-cpp)
# WORKDIR /usr/local/src
# RUN apt-get install -y git cmake && \
#   git clone --depth 1 https://github.com/cyberhull/slalib-cpp.git && \
#   cd slalib-cpp && \
#   mkdir build && cd build && \
#   cmake -DBUILD_SHARED_LIBS=ON .. && \
#   make && \
#   cp lib/libslalib.so /usr/local/lib/libslalib.so && \
#   ldconfig && \
#   cd /usr/local/src && rm -rf slalib-cpp

# Compile and install SLALIB from Fortran modded Jan Kleyna source
WORKDIR /usr/local/src
RUN git clone --depth 1 https://github.com/wakatara/slalib.starlink.modded.git && \
  cd slalib.starlink.modded && \
  make && \
  cp libslalib.so /usr/local/lib/libslalib.so && \
  cp slalib.h /usr/local/include/slalib.h && \
  ldconfig && \
  cd /usr/local/src && rm -rf slalib.starlink.modded

# Install SBCL
RUN apt-get install -y sbcl

# Compile and install cdsclient from CDS official source
WORKDIR /usr/local/src
RUN wget http://cdsarc.cds.unistra.fr/ftp/pub/sw/cdsclient.tar.gz && \
  tar xzf cdsclient.tar.gz && \
  cd cdsclient-* && \
  ./configure --prefix=/usr/local && \
  make && \
  make install && \
  cd /usr/local/src && rm -rf cdsclient-* cdsclient.tar.gz

WORKDIR /root
COPY ./coma-json-server .

