FROM ubuntu:24.04

RUN apt-get update && apt-get install -y --no-install-recommends wget build-essential curl git ca-certificates
RUN apt-get install -y gfortran libgfortran5 pgplot5 libfftw3-double3 libfftw3-single3
# Additional libraries needed for compilation of cftisio quirks
RUN apt-get install -y zlib1g-dev libcurl4-openssl-dev
# Additional libraries from original dynamic-libraries (XPA, WCS)
RUN apt-get install -y libxpa-dev libxpa1 xpa-tools wcslib-dev libwcs8

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

# ------------------------------------------------------------------
# Install TERAPIX reqs and other astro sw via astromatic  
# ------------------------------------------------------------------
RUN apt-get install -y source-extractor swarp scamp libatlas-base-dev libblas-dev liblapack-dev


# ------------------------------------------------------------------
# Compile and install SLALIB from C++ port (slalib-cpp)
# ------------------------------------------------------------------
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

# ------------------------------------------------------------------
# Compile and install SLALIB from Fortran modded Jan Kleyna source
# ------------------------------------------------------------------
WORKDIR /usr/local/src
RUN git clone --depth 1 https://github.com/wakatara/slalib.starlink.modded.git && \
  cd slalib.starlink.modded && \
  make && \
  cp libslalib.so /usr/local/lib/libslalib.so && \
  cp slalib.h /usr/local/include/slalib.h && \
  ldconfig && \
  cd /usr/local/src && rm -rf slalib.starlink.modded

# ------------------------------------------------------------------
# Build and install kdtree library for spatial indexing
# ------------------------------------------------------------------
WORKDIR /usr/local/src
RUN git clone --depth 1 https://github.com/jtsiomb/kdtree.git && \
  cd kdtree && \
  ./configure --prefix=/usr/local && \
  make && \
  make install && \
  ldconfig && \
  cd /usr/local/src && rm -rf kdtree

# ------------------------------------------------------------------
# Build and install concaveman for concave hull computation
# ------------------------------------------------------------------
WORKDIR /usr/local/src
RUN git clone --depth 1 https://github.com/sadaszewski/concaveman-cpp.git && \
  cd concaveman-cpp/src/main/cpp && \
  g++ -std=c++11 -fPIC -shared concaveman.cpp -o libconcaveman.so && \
  cp libconcaveman.so /usr/local/lib/ && \
  cp concaveman.h /usr/local/include/ && \
  ldconfig && \
  cd /usr/local/src && rm -rf concaveman-cpp

# ------------------------------------------------------------------
# Build and install tsnnls (sparse non-negative least squares)
# ------------------------------------------------------------------
WORKDIR /usr/local/src
RUN apt-get install -y autoconf automake libtool && \
  wget https://jasoncantarella.com/downloads/libtsnnls-2.3.4.tar.gz && \
  tar xzf libtsnnls-2.3.4.tar.gz && \
  cd libtsnnls-2.3.4 && \
  autoreconf --install --force && \
  ./configure --prefix=/usr/local && \
  make && \
  make install && \
  ldconfig && \
  cd /usr/local/src && rm -rf libtsnnls-2.3.4 libtsnnls-2.3.4.tar.gz

# ------------------------------------------------------------------
# Build and install simple-kepler-solver (Kepler orbit solver)
# Archival copy of Mehmet Atakan Gürkan's sol_kep code
# Used by Jan Kleyna in COMA sci-backend for isochrone/isodyne calculations
# ------------------------------------------------------------------
WORKDIR /usr/local/src
RUN git clone --depth 1 https://github.com/wakatara/simple-kepler-solver.git && \
  cd simple-kepler-solver && \
  make && \
  make install && \
  ldconfig && \
  cd /usr/local/src && rm -rf simple-kepler-solver

# ------------------------------------------------------------------
# Install SBCL
# ------------------------------------------------------------------
RUN apt-get install -y sbcl

# ------------------------------------------------------------------
# Compile and install cdsclient from CDS official source
# ------------------------------------------------------------------
WORKDIR /usr/local/src
RUN wget http://cdsarc.cds.unistra.fr/ftp/pub/sw/cdsclient.tar.gz && \
  tar xzf cdsclient.tar.gz && \
  cd cdsclient-* && \
  ./configure --prefix=/usr/local && \
  make && \
  make install && \
  cd /usr/local/src && rm -rf cdsclient-* cdsclient.tar.gz



# ------------------------------------------------------------------
# Boot the sci-backend coma-json-server
# ------------------------------------------------------------------
WORKDIR /root
COPY ./coma-json-server .

