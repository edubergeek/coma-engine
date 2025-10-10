FROM ubuntu:24.04

RUN apt-get update && apt-get install -y --no-install-recommends wget build-essential curl
RUN apt-get install -y libfftw3-dev gfortran libgfortran5 pgplot5

RUN ln -s /usr/lib/x86_64-linux-gnu/libfftw3.so.3.5.8 /usr/local/lib/libfftw3.so
RUN ln -s /usr/lib/x86_64-linux-gnu/libfftw3f.so.3.5.8 /usr/local/lib/libfftw3f.so
RUN ln -s /coma/code/Lisp/lisp-lib/dynamic-libraries/linux-x86-64/libslalib.so /usr/local/lib/libslalib.so


# Install dependencies for adding external repositories
RUN apt-get update && \
  apt-get install -y apt-transport-https gnupg curl lsb-release && \
  echo "deb https://repo.astromatic.net/ubuntu/bleeding $(lsb_release -cs) main" > /etc/apt/sources.list.d/astromatic-bleeding.list && \
  curl -fsSL https://repo.astromatic.net/astromatic.net.key | tee /etc/apt/trusted.gpg.d/astromatic.asc && \
  apt-get update

# Install astronomy tools
RUN apt-get install -y source-extractor swarp scamp libatlas-base-dev libblas-dev liblapack-dev

# Install SBCL
RUN apt-get install -y sbcl
# RUN mkdir -p /usr/local/src/Lisp
# WORKDIR /usr/local/src/Lisp
# COPY sbcl-2.3.8-source.tar.bz2 .
# RUN tar xjf sbcl-2.3.8-source.tar.bz2
# WORKDIR /usr/local/src/Lisp/sbcl-2.3.8
# RUN bash make.sh
# RUN bash install.sh
# # Install over distro provided sbcl
# RUN bash install.sh --prefix=/usr

WORKDIR /usr/local/src
COPY cdsclient.tar.gz .
RUN tar xzf cdsclient.tar.gz
WORKDIR /usr/local/src/cdsclient-3.84
RUN ./configure && make && make install

WORKDIR /root
COPY coma-json-server .

