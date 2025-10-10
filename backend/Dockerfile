FROM ubuntu:24.04

RUN apt-get update && apt-get install -y --no-install-recommends wget build-essential curl
RUN apt-get install -y gfortran libgfortran5 pgplot5 libfftw3-double3 libfftw3-single3 

# Install cfitsio and friends 
RUN apt-get -y install  libcfitsio-bin libcfitsio-dev libcfitsio10t64

# Install TERAPIX reqs and other astro sw via astromatic  
# Install dependencies for adding external repositories
RUN apt-get update && \
  apt-get install -y apt-transport-https gnupg curl lsb-release && \
  echo "deb https://repo.astromatic.net/ubuntu/stable $(lsb_release -cs) main" > /etc/apt/sources.list.d/astromatic-stable.list && \
  curl -fsSL https://repo.astromatic.net/astromatic.net.key | tee /etc/apt/trusted.gpg.d/astromatic.asc && \
  apt-get update

# Install astronomy tools
RUN apt-get install -y source-extractor swarp scamp libatlas-base-dev libblas-dev liblapack-dev 
# RUN apt-get install -y slalib

# Compile and install SLALIB
WORKDIR /usr/local/src
RUN wget -q https://www.starlink.ac.uk/ftp/software/slalib/slalib-3.0.0.tar.gz -O slalib.tar.gz && \
  tar xzf slalib.tar.gz && \
  cd slalib-3.0.0 && \
  ./configure --prefix=/usr/local && \
  make && make install && \
  cd .. && rm -rf slalib-3.0.0 slalib.tar.gz

# Install SBCL
RUN apt-get install -y sbcl

WORKDIR /usr/local/src
COPY cdsclient.tar.gz .
RUN tar xzf cdsclient.tar.gz
WORKDIR /usr/local/src/cdsclient-3.84
RUN ./configure && make && make install

WORKDIR /root
COPY ./coma-json-server .

