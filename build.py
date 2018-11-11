#!/usr/bin/env python3
import datetime
import re
import subprocess

environments=[
    dict(
        name='latest',
        PG='master',
        GEOS='master',
        GDAL='master',
        PROJ='master'
    ),
    dict(
        name='stable_pg11',
        PG='REL_11_STABLE',
        GEOS='3.7',
        GDAL='release/2.3',
        PROJ='5.2'
    ),
    dict(
        name='stable_pg10',
        PG='REL_10_STABLE',
        GEOS='svn-3.6',
        GDAL='release/2.3',
        PROJ='4.9'
    ),
    dict(
        name='stable_pg96',
        PG='REL9_6_STABLE',
        GEOS='svn-3.6',
        GDAL='release/2.2',
        PROJ='4.9'
    ),
    dict(
        name='old_pg95',
        PG='REL9_5_STABLE',
        GEOS='svn-3.5',
        GDAL='release/1.11',
        PROJ='4.8'
    ),
# Pre-PostGIS 3.0
#    dict(
#        name='stable_pg95',
#        PG='REL9_5_STABLE',
#        GEOS='svn-3.6',
#        GDAL='release/2.2',
#        PROJ='4.9'
#    ),
#    dict(
#        name='old',
#        PG='REL9_4_STABLE',
#        GEOS='svn-3.5',
#        GDAL='release/1.11',
#        PROJ='4.8'
#    ),
]

for env in environments:
    if env['name'] == 'latest':
        tag = 'latest'
    else:
        versions = { k : ''.join(re.findall('\d+', v) or v) for k, v in env.items() }
        tag = 'pg{PG}-geos{GEOS}-gdal{GDAL}-proj{PROJ}'.format_map(versions)
    image = 'postgis/postgis-build-env:{}'.format(tag)

    subprocess.check_call([
        'docker', 'build',
        '--pull',
        '--build-arg', 'BUILD_DATE={}'.format(datetime.date.today().strftime("%Y%m%d")),
        '--build-arg', 'POSTGRES_BRANCH={PG}'.format_map(env),
        '--build-arg', 'GEOS_BRANCH={GEOS}'.format_map(env),
        '--build-arg', 'GDAL_BRANCH={GDAL}'.format_map(env),
        '--build-arg', 'PROJ_BRANCH={PROJ}'.format_map(env),
        '-t', image,
        '.'
    ])
    subprocess.check_call([
        'docker', 'push', image
    ])
        
