FROM ubuntu:20.04

RUN apt-get update && apt-get install -y --no-install-recommends wget build-essential curl
RUN apt-get install -y fftw3 gfortran libgfortran4:amd64 pgplot5

RUN ln -s /usr/lib/x86_64-linux-gnu/libfftw3.so.3.5.8 /usr/local/lib/libfftw3.so
RUN ln -s /usr/lib/x86_64-linux-gnu/libfftw3f.so.3.5.8 /usr/local/lib/libfftw3f.so
RUN ln -s /coma/code/Lisp/lisp-lib/dynamic-libraries/linux-x86-64/libslalib.so /usr/local/lib/libslalib.so

#Install ATLAS
#WORKDIR /usr/local/src
#COPY atlas3.10.3.tar.bz2 .
#RUN tar xjvf atlas3.10.3.tar.bz2
#RUN mkdir ./ATLAS/LinuxBuild
#WORKDIR ./ATLAS/LinuxBuild
#../configure --shared -b 64 
#RUN make build && make check && make ptcheck && make time && make install

#Install FFTw
#WORKDIR /usr/local/src
#COPY fftw-3.3.10.tar.gz .
#RUN tar -xzvf fftw-3.3.10.tar.gz
#WORKDIR ./fftw-3.3.10
#RUN ./configure
#RUN make && make install

#Install TERAPIX
RUN apt-get update
RUN apt-get install -y sextractor swarp scamp
# sex,scamp,swarp are missing  (in coma they are in /usr/bin/sex /usr/bin/swarp and a newer /usr/local/bin/scamp
# scamp needs ATLAS, curl, fftw3, plplot
# COMA/work/kleyna/SCAMP-COMPILE/scamp


# Install SBCL
RUN apt-get install -y sbcl
RUN mkdir -p /usr/local/src/Lisp
WORKDIR /usr/local/src/Lisp
COPY sbcl-2.3.8-source.tar.bz2 .
RUN tar xjf sbcl-2.3.8-source.tar.bz2
WORKDIR ./sbcl-2.3.8
RUN bash make.sh
RUN bash install.sh
# Install over distro provided sbcl
RUN bash install.sh --prefix=/usr

WORKDIR /usr/local/src
COPY cdsclient.tar.gz .
RUN tar xzf cdsclient.tar.gz
WORKDIR cdsclient-3.84
RUN ./configure && make && make install

WORKDIR /root
COPY coma-json-server .

