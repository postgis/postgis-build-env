FROM debian:stable-slim

RUN apt-get update && \
  apt-get install -y --no-install-recommends \
  autoconf \
  automake \
  bison \
  build-essential \
  ca-certificates \
  clang \
  cmake \
  curl \
  docbook-xml \
  eatmydata \
  flex \
  gdb \
  git \
  libboost-serialization-dev \
  libboost-test-dev \
  libboost-thread-dev \
  libcunit1-dev \
  libcurl4-gnutls-dev \
  libgmp-dev \
  libjson-c-dev \
  libmpfr-dev \
  libpcre3-dev \
  libprotobuf-c-dev \
  libreadline-dev \
  libsqlite3-dev \
  libtiff-dev \
  libtool \
  libxml2-dev \
  libxml2-utils \
  pkg-config \
  protobuf-c-compiler \
  sudo \
  sqlite3 \
  valgrind \
  wget \
  xsltproc \
  zlib1g-dev && \
  apt-get clean && \
  rm -rf /var/lib/apt/lists/*

WORKDIR /src

RUN echo /usr/lib/x86_64-linux-gnu/libeatmydata.so >> /etc/ld.so.preload

ARG BUILD_THREADS=4

ARG CGAL_BRANCH=5.3
RUN wget https://github.com/CGAL/cgal/releases/download/v${CGAL_BRANCH}/CGAL-${CGAL_BRANCH}.tar.xz && \
    tar xJf CGAL-${CGAL_BRANCH}.tar.xz && \
    cd CGAL-${CGAL_BRANCH} && mkdir build && cd build && \
    cmake -DCMAKE_BUILD_TYPE:STRING=Release -DCMAKE_INSTALL_PREFIX=/src/CGAL .. && \
    make && make install && cd ../.. && \
    cd /src && rm -rf CGAL-${CGAL_BRANCH}

ARG SFCGAL_BRANCH=master
RUN git clone --depth 1 --branch ${SFCGAL_BRANCH} https://gitlab.com/Oslandia/SFCGAL.git && \
     cd SFCGAL && \
     mkdir cmake-build && \
     cd cmake-build && \
     cmake -DCGAL_DIR="/src/CGAL" -DCMAKE_PREFIX_PATH=/src/CGAL .. && \
     make -j${BUILD_THREADS} && \
     make install && \
     cd /src && rm -rf SFCGAL

ARG BUILD_DATE
ENV PGDATA=/var/lib/postgresql

RUN useradd postgres && \
    mkdir -p ${PGDATA} && chown postgres ${PGDATA} && \
    mkdir -p /src/postgis && chown postgres /src/postgis
   
ENV PATH="/usr/local/pgsql/bin:${PATH}"

ARG PROJ_BRANCH=master
RUN git clone --depth 1 --branch ${PROJ_BRANCH} https://github.com/OSGeo/PROJ && \
    cd PROJ && \
    ./autogen.sh && ./configure && make -j${BUILD_THREADS} && make install && \
    cd /src && rm -rf PROJ

ARG GDAL_BRANCH=master
RUN git clone --depth 1 --branch ${GDAL_BRANCH} https://github.com/OSGeo/gdal && \
    cd gdal/gdal && \
    ./autogen.sh && ./configure && make -j${BUILD_THREADS} && make install && \
    cd /src && rm -rf gdal

ARG GEOS_BRANCH=master
RUN git clone --depth 1 --branch ${GEOS_BRANCH} https://github.com/libgeos/geos && \
    cd geos && \
    mkdir cmake-build && \
    cd cmake-build && \
    cmake -DCMAKE_BUILD_TYPE=Release .. && \
    make -j${BUILD_THREADS} && make install && \
    cd /src && rm -rf geos

ARG POSTGRES_BRANCH=master
ARG PG_CC=gcc
RUN git clone --depth 1 --branch ${POSTGRES_BRANCH} https://github.com/postgres/postgres && \
    cd postgres && \
    ./configure --enable-cassert --enable-debug CC=${PG_CC} CFLAGS="-ggdb -Og -g3 -fno-omit-frame-pointer" && \
    make -j${BUILD_THREADS} && make install && \
    cd /src && rm -rf postgres

WORKDIR /src/postgis

RUN ldconfig /usr/local/pgsql/lib
USER postgres

# create cluster now to save time on build
RUN /usr/local/pgsql/bin/initdb -D /var/lib/postgresql
