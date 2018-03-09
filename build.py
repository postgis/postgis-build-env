#!/usr/bin/env python3
import subprocess

environments=[
    dict(
        name='latest',
        PG='master',
        GEOS='master',
        GDAL='trunk',
        PROJ='master'
    ),
    dict(
        name='stable',
        PG='REL_10_STABLE',
        GEOS='svn-3.6',
        GDAL='2.2',
        PROJ='4.9'
    )
]

for env in environments:
    subprocess.check_call([
        'docker', 'build',
        '--build-arg', 'POSTGRES_BRANCH={PG}'.format_map(env),
        '--build-arg', 'GEOS_BRANCH={GEOS}'.format_map(env),
        '--build-arg', 'GDAL_BRANCH={GDAL}'.format_map(env),
        '--build-arg', 'PROJ_BRANCH={PROJ}'.format_map(env),
        '-t', 'dbaston/postgis_build_env:{name}'.format_map(env),
        '.'
    ])
    subprocess.check_call([
        'docker', 'push', 'dbaston/postgis_build_env:{name}'.format_map(env)
    ])
        
