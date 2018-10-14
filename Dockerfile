FROM debian:stretch

RUN apt-get update && apt-get install -y \
  autoconf \
  gdb \
  bison \
  build-essential \
  cmake \
  curl \
  flex \
  git \
  libboost-test-dev \
  libboost-thread-dev \
  libcgal-dev \
  libcunit1-dev \
  libgmp-dev \
  libjson-c-dev \
  libmpfr-dev \
  libpcre3-dev \
  libprotobuf-c-dev \
  libreadline-dev \
  libtool \
  libxml2-dev \
  libxml2-utils \
  pkg-config \
  protobuf-c-compiler \
  sudo \
  wget \
  xsltproc \
  zlib1g-dev \
  cmake \
  libboost-test-dev \
  libboost-thread-dev \
  libgmp-dev \
  libmpfr-dev \
  zlib1g-dev && \
  rm -rf /var/lib/apt/lists/*

WORKDIR /src
RUN wget https://github.com/Oslandia/SFCGAL/archive/v1.3.0.tar.gz && \
    tar xzvf v1.3.0.tar.gz && \
    rm v1.3.0.tar.gz && \
    cd SFCGAL-1.3.0 && \
    mkdir cmake-build && \
    cd cmake-build && \
    cmake .. && \
    make -j4 && \
    make install && \
    cd /src && rm -rf SFCGAL-1.3.0

ARG BUILD_DATE
ENV PGDATA=/var/lib/postgresql

RUN useradd postgres && \
    mkdir -p ${PGDATA} && chown postgres ${PGDATA} && \
    mkdir -p /src/postgis && chown postgres /src/postgis
   
ENV PATH="/usr/local/pgsql/bin:${PATH}"

ARG GDAL_BRANCH=trunk
RUN git clone --depth 1 --branch ${GDAL_BRANCH} https://github.com/OSGeo/gdal && \
    cd gdal/gdal && \
    ./autogen.sh && ./configure && make -j && make install && \
    cd /src && rm -rf gdal

ARG GEOS_BRANCH=master
RUN git clone --depth 1 --branch ${GEOS_BRANCH} https://github.com/OSGeo/geos && \
    cd geos && \
    ./autogen.sh && ./configure && make -j && make install && \
    cd /src && rm -rf geos

ARG POSTGRES_BRANCH=master
RUN git clone --depth 1 --branch ${POSTGRES_BRANCH} https://github.com/postgres/postgres && \
    cd postgres && \
    ./configure && make -j && make install && \
    cd /src && rm -rf postgres

ARG PROJ_BRANCH=master
RUN git clone --depth 1 --branch ${PROJ_BRANCH} https://github.com/OSGEO/proj.4 && \
    cd proj.4 && \
    ./autogen.sh && ./configure && make -j && make install && \
    cd /src && rm -rf proj.4

WORKDIR /src/postgis

RUN ldconfig /usr/local/pgsql/lib
USER postgres

# create cluster now to save time on build
RUN /usr/local/pgsql/bin/initdb -D /var/lib/postgresql
