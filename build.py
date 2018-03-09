#!/usr/bin/env python3
import re
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
    ),
    dict(
        name='stable_pg96',
        PG='REL9_6_STABLE',
        GEOS='svn-3.6',
        GDAL='2.2',
        PROJ='4.9'
    ),
    dict(
        name='stable_pg95',
        PG='REL9_5_STABLE',
        GEOS='svn-3.6',
        GDAL='2.2',
        PROJ='4.9'
    ),
    dict(
        name='stable_pg94',
        PG='REL9_4_STABLE',
        GEOS='svn-3.6',
        GDAL='2.2',
        PROJ='4.9'
    ),
    dict(
        name='trusty',
        PG='REL9_3_STABLE',
        GEOS='svn-3.4',
        GDAL='1.11',
        PROJ='4.8'
    )
]

for env in environments:
    if env['name'] == 'latest':
        tag = 'latest'
    else:
        versions = { k : ''.join(re.findall('\d+', v)) for k, v in env.items() }
        tag = 'pg{PG}-geos{GEOS}-gdal{GDAL}-proj{PROJ}'.format_map(versions)
    image = 'dbaston/postgis-build-env:{}'.format(tag)

    subprocess.check_call([
        'docker', 'build',
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
        
