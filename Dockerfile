FROM debian:trixie-slim

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
  docbook5-xml \
  eatmydata \
  flex \
  gdb \
  git \
  libboost-serialization-dev \
  libboost-test-dev \
  libboost-thread-dev \
  libclang-rt-dev \
  libcunit1-dev \
  libcurl4-gnutls-dev \
  libgmp-dev \
  libicu-dev \
  libjson-c-dev \
  libmpfr-dev \
  libpcre2-dev \
  libprotobuf-c-dev \
  libreadline-dev \
  libsqlite3-dev \
  libtiff-dev \
  libtool \
  libxml2-dev \
  libxml2-utils \
  llvm \
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

# Determine a safe default parallelism: CGAL/SFCGAL cc1plus compilation
# can spike to 2-3 GiB per job, so a hardcoded BUILD_THREADS=4 requires
# roughly 10 GiB of container memory and reliably OOMs on smaller hosts.
# The "auto" default caps at one job per 3 GiB of container memory and
# at nproc, with a hard ceiling of 4. Override at build time with
# --build-arg BUILD_THREADS=N.
ARG BUILD_THREADS=auto
RUN set -e; \
    if [ "$BUILD_THREADS" = "auto" ]; then \
        MEM_GB=$(awk '/MemTotal/ {printf "%d", $2 / 1024 / 1024}' /proc/meminfo); \
        CPU=$(nproc); \
        T=$(( MEM_GB / 3 )); \
        [ "$T" -lt 1 ] && T=1; \
        [ "$T" -gt "$CPU" ] && T=$CPU; \
        [ "$T" -gt 4 ] && T=4; \
    else \
        T="$BUILD_THREADS"; \
    fi; \
    printf '#!/bin/sh\necho %s\n' "$T" > /usr/local/bin/build-threads; \
    chmod +x /usr/local/bin/build-threads; \
    echo "BUILD_THREADS resolved to: $(build-threads)"


# nlohmann/json - header-only library for SFCGAL (with CMake support)
RUN set -ex \
    && mkdir -p /usr/src \
    && cd /usr/src \
    # Get the latest release version dynamically
    && NLOHMANN_JSON_VERSION=$(curl -s https://api.github.com/repos/nlohmann/json/releases/latest | grep '"tag_name":' | sed -E 's/.*"v([^"]+)".*/\1/') \
    && echo "Installing nlohmann/json version: ${NLOHMANN_JSON_VERSION}" \
    # Download and extract the full source with CMake support
    && curl -L "https://github.com/nlohmann/json/archive/refs/tags/v${NLOHMANN_JSON_VERSION}.tar.gz" -o nlohmann-json.tar.gz \
    && tar -xzf nlohmann-json.tar.gz \
    && cd "json-${NLOHMANN_JSON_VERSION}" \
    && mkdir build \
    && cd build \
    && cmake .. -DCMAKE_BUILD_TYPE=${DOCKER_CMAKE_BUILD_TYPE} -DJSON_BuildTests=OFF \
    && make install \
    && cd /usr/src \
    && rm -rf "json-${NLOHMANN_JSON_VERSION}" nlohmann-json.tar.gz \
    && echo "nlohmann/json ${NLOHMANN_JSON_VERSION} installed with CMake support" > /_pgis_nlohmann_json_version.txt

ARG CGAL_BRANCH=6.0.2
RUN wget https://github.com/CGAL/cgal/releases/download/v${CGAL_BRANCH}/CGAL-${CGAL_BRANCH}.tar.xz && \
    tar xJf CGAL-${CGAL_BRANCH}.tar.xz && \
    cd CGAL-${CGAL_BRANCH} && mkdir build && cd build && \
    cmake -DCMAKE_BUILD_TYPE:STRING=Release -DCMAKE_INSTALL_PREFIX=/src/CGAL .. && \
    make && make install && cd ../.. && \
    cd /src && rm -rf CGAL-${CGAL_BRANCH}

ARG SFCGAL_BRANCH=master
RUN git clone --depth 1 --branch ${SFCGAL_BRANCH} https://gitlab.com/sfcgal/SFCGAL.git && \
     cd SFCGAL && \
     mkdir cmake-build && \
     cd cmake-build && \
     cmake -DCGAL_DIR="/src/CGAL" -DCMAKE_PREFIX_PATH=/src/CGAL .. && \
     make -j"$(build-threads)" && \
     make install && \
     cd /src && rm -rf SFCGAL

ARG PROJ_BRANCH=master
RUN git clone --depth 1 --branch ${PROJ_BRANCH} https://github.com/OSGeo/PROJ && \
    cd PROJ && \
    mkdir cmake-build && \
    #./autogen.sh && ./configure && make -j"$(build-threads)" && make install && \
    cd cmake-build && \
    cmake .. && \
    make -j"$(build-threads)" && \
    make install && \
    #projsync --system-directory --source-id us_noaa && \
    #projsync --system-directory --source-id ch_swisstopo && \
    cd /src && rm -rf PROJ


ARG BUILD_DATE
ENV PGDATA=/var/lib/postgresql

RUN useradd postgres -p paYAHIZz4VZyc -G sudo && \
    mkdir -p ${PGDATA} && chown postgres ${PGDATA} && \
    mkdir -p /src/postgis && chown postgres /src/postgis

ENV PATH="/usr/local/pgsql/bin:${PATH}"

ARG GDAL_BRANCH=master
RUN git clone --depth 1 --branch ${GDAL_BRANCH} https://github.com/OSGeo/gdal && \
    cd gdal && \
    # gdal project directory structure - has been changed !
    if [ -d "gdal" ] ; then \
        echo "Directory 'gdal' dir exists -> older version!" ; \
        cd gdal ; \
    fi && \
    if [ -f "./autogen.sh" ]; then \
      # Building with autoconf ( old/deprecated )
      ./autogen.sh && \
      ./configure \
      ; \
    else \
        # Building with cmake
        mkdir build && cd build && \
        cmake -DCMAKE_BUILD_TYPE=Release .. \
        ; \
    fi && \
    make -j"$(build-threads)" && make install && \
    cd /src && rm -rf gdal

ARG GEOS_BRANCH=master
RUN git clone --depth 1 --branch ${GEOS_BRANCH} https://github.com/libgeos/geos && \
    cd geos && \
    mkdir cmake-build && \
    cd cmake-build && \
    cmake -DCMAKE_BUILD_TYPE=Release .. && \
    make -j"$(build-threads)" && make install && \
    cd /src && rm -rf geos

ARG POSTGRES_BRANCH=master
ARG PG_CC=gcc
RUN git clone --depth 1 --branch ${POSTGRES_BRANCH} https://github.com/postgres/postgres && \
    cd postgres && \
    ./configure --enable-cassert --enable-debug CC=${PG_CC} CFLAGS="-ggdb -Og -g3 -fno-omit-frame-pointer" && \
    make -j"$(build-threads)" && make install && \
    cd /src && rm -rf postgres

# disable requiring password to sudo
RUN echo '%sudo ALL=(ALL) NOPASSWD:ALL' >> /etc/sudoers
WORKDIR /src/postgis

RUN ldconfig /usr/local/pgsql/lib
USER postgres

# create cluster now to save time on build
RUN /usr/local/pgsql/bin/initdb -D /var/lib/postgresql \
  -c fsync=off \
  -c synchronous_commit=off \
  -c full_page_writes=off \
  -c wal_level=minimal \
  -c max_wal_senders=0
