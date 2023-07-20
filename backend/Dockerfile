FROM ubuntu:20.04

RUN apt-get update && apt-get install -y --no-install-recommends wget build-essential
RUN apt-get install -y fftw3 gfortran libgfortran4:amd64 pgplot5

RUN ln -s /usr/lib/x86_64-linux-gnu/libfftw3.so.3.5.8 /usr/local/lib/libfftw3.so
RUN ln -s /usr/lib/x86_64-linux-gnu/libfftw3f.so.3.5.8 /usr/local/lib/libfftw3f.so

# build commands
RUN mkdir -p /usr/local/src/Lisp
WORKDIR /usr/local/src/Lisp
COPY sbcl-2.3.1-source.tar.bz2 .
RUN tar xjf sbcl-2.3.1-source.tar.bz2

COPY sbcl-2.3.1-x86-64-linux-binary.tar.bz2 .
RUN tar xjf sbcl-2.3.1-x86-64-linux-binary.tar.bz2
WORKDIR ./sbcl-2.3.1-x86-64-linux
RUN bash install.sh

WORKDIR /usr/local/src
COPY cdsclient.tar.gz .
RUN tar xzf cdsclient.tar.gz
WORKDIR cdsclient-3.84
RUN ./configure && make && make install

WORKDIR /root
COPY coma-json-server .

#EXPOSE 5054
#ENTRYPOINT ["python3", "-m", "rq_dashboard"]
#ENTRYPOINT ["sleep", "86400"]
