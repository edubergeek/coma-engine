FROM ubuntu:24.04

RUN apt-get update && apt-get install -y --no-install-recommends wget build-essential curl git ca-certificates
RUN apt-get install -y gfortran libgfortran5 pgplot5 libfftw3-double3 libfftw3-single3 libfftw3-dev
# Create symlinks for CFFI to find FFTW3 libraries
RUN (ln -s /usr/lib/aarch64-linux-gnu/libfftw3.so /usr/lib/libfftw3.so || \
  ln -s /usr/lib/x86_64-linux-gnu/libfftw3.so /usr/lib/libfftw3.so || true) && \
  (ln -s /usr/lib/aarch64-linux-gnu/libfftw3f.so /usr/lib/libfftw3f.so || \
  ln -s /usr/lib/x86_64-linux-gnu/libfftw3f.so /usr/lib/libfftw3f.so || true) && \
  (ln -s /usr/lib/aarch64-linux-gnu/libfftw3l.so /usr/lib/libfftw3l.so || \
  ln -s /usr/lib/x86_64-linux-gnu/libfftw3l.so /usr/lib/libfftw3l.so || true)
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
# Install SBCL and Quicklisp
# ------------------------------------------------------------------
RUN apt-get install -y sbcl

# Install Quicklisp
WORKDIR /root
RUN curl -O https://beta.quicklisp.org/quicklisp.lisp && \
  sbcl --non-interactive \
  --load quicklisp.lisp \
  --eval '(quicklisp-quickstart:install :path "/root/quicklisp")' && \
  rm quicklisp.lisp

# Install buildapp for creating executables
RUN sbcl --non-interactive \
  --load /root/quicklisp/setup.lisp \
  --eval '(ql:quickload :buildapp)' \
  --eval '(buildapp:build-buildapp "/usr/local/bin/buildapp")'

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
# Create directory structure for sci-backend data volume mounts
# ------------------------------------------------------------------
RUN mkdir -p /data/support/sci-backend/catalogs \
  /data/support/config \
  /data/support/sci-backend/cache \
  /data/support/sci-backend/orbits \
  /data/support/sci-backend/work && \
  chmod -R 755 /data

# ------------------------------------------------------------------
# Copy and build coma-sci-backend Lisp application
# ------------------------------------------------------------------
WORKDIR /root

# Copy the entire coma-sci-backend source tree (relative to COMA/ build context)
COPY coma-sci-backend /root/coma-sci-backend

# Create placeholder data files for build time (actual data provided via volume mounts at runtime)
# These allow the Lisp system to load during buildapp without errors
# Real data files will be in /data/support/sci-backend/catalogs (see docker-compose.yml)
RUN mkdir -p /root/coma-sci-backend/astro/observatories/data && \
  mkdir -p /root/coma-sci-backend/astro/small-body-name/data && \
  touch /root/coma-sci-backend/astro/observatories/data/mpc-obs-codes.txt && \
  touch /root/coma-sci-backend/astro/small-body-name/data/AllCometEls.txt && \
  touch /root/coma-sci-backend/astro/small-body-name/data/numbered_comets.txt && \
  touch /root/coma-sci-backend/astro/small-body-name/data/periodic_comets.csv && \
  touch /root/coma-sci-backend/astro/small-body-name/data/asteroid_names.csv && \
  echo "# Placeholder - actual data at runtime via /data/support/sci-backend/catalogs volume" > \
  /root/coma-sci-backend/astro/observatories/data/mpc-obs-codes.txt

# Install Quicklisp dependencies from qlfile
WORKDIR /root/coma-sci-backend
RUN sbcl --non-interactive \
  --load /root/quicklisp/setup.lisp \
  --eval '(ql:quickload :yason)' \
  --eval '(ql:quickload :alexandria)' \
  --eval '(ql:quickload :hunchentoot)' \
  --eval '(ql:quickload :drakma)' \
  --eval '(ql:quickload :cl-ppcre)' \
  --eval '(ql:quickload :cffi)' \
  --eval '(ql:quickload :bordeaux-threads)' \
  --eval '(ql:quickload :cl-fad)' \
  --eval '(ql:quickload :cxml)' \
  --eval '(ql:quickload :xmls)' \
  --eval '(ql:quickload :fare-csv)' \
  --eval '(ql:quickload :md5)' \
  --eval '(ql:quickload :salza2)'

# Build the coma-json-server executable with buildapp
# First try to load with debugging to get backtrace if it fails
RUN sbcl --noinform --non-interactive \
  --load /root/quicklisp/setup.lisp \
  --eval '(asdf:initialize-source-registry (quote (:source-registry (:tree "/root/coma-sci-backend/") :inherit-configuration)))' \
  --eval '(handler-bind ((error (lambda (c) (format t "~%~%ERROR: ~A~%~%BACKTRACE:~%" c) (sb-debug:print-backtrace :count 50) (sb-ext:exit :code 1)))) (asdf:load-system :coma-sci-backend))' \
  && echo "System loaded successfully!" \
  || (echo "Failed to load system - see backtrace above" && exit 1)

# If loading succeeded, build with buildapp
RUN buildapp --output /usr/local/bin/coma-json-server \
  --asdf-tree /root/coma-sci-backend \
  --load-system coma-sci-backend \
  --entry coma-json-server:main \
  || buildapp --output /usr/local/bin/coma-json-server \
  --asdf-tree /root/coma-sci-backend \
  --load-system coma-sci-backend \
  --entry coma-json-server:start-server

# Make executable
RUN chmod +x /usr/local/bin/coma-json-server

# Set working directory
WORKDIR /root

# Set library path for runtime
ENV LD_LIBRARY_PATH=/usr/local/lib:$LD_LIBRARY_PATH

# Expose port
EXPOSE 8080

# Start the server
CMD ["/usr/local/bin/coma-json-server"]

