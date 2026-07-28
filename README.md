Scripts to generate Docker images with build environments for PostGIS.

Generated images are hosted at [Docker Hub](https://hub.docker.com/r/postgis/postgis-build-env/tags/).

To use:
Builds all
```
python3 build.py 
```

Builds ones marked as frequently changing.  This is the command the jenkins bot uses for building.
```
python3 build.py weekly
```

Build progress is here - https://debbie.postgis.net/job/PostGIS-build-env/

[![Build Status](https://debbie.postgis.net/buildStatus/icon?job=PostGIS-build-env%2Flabel%3Ddocker)](https://debbie.postgis.net/job/PostGIS-build-env/label=docker/)

Each image records the source branch and commit used for PostgreSQL, GEOS,
GDAL, PROJ, and SFCGAL in:

```
/usr/local/share/postgis-build-env/build-commits.env
```

To print that metadata from a running container:

```
postgis-build-env-commits
```
