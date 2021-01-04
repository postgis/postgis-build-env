#!/usr/bin/env python3
import datetime
import re
import subprocess

environments=[
# put last modified first to iterate faster
    dict(
        name='latest',
        PG='master',
        GEOS='master',
        GDAL='master',
        PROJ='master',
        PG_CC='gcc'
    ),
    dict(
        name='stable_pg13',
        PG='REL_13_STABLE',
        GEOS='3.9',
        GDAL='release/3.1',
        PROJ='7.1',
        PG_CC='clang'
    ),
    dict(
        name='stable_pg13',
        PG='REL_13_STABLE',
        GEOS='3.9',
        GDAL='release/3.1',
        PROJ='7.1',
        PG_CC='gcc'
    ),
    dict(
        name='stable_pg12',
        PG='REL_12_STABLE',
        GEOS='3.8',
        GDAL='release/3.0',
        PROJ='6.1.1',
        PG_CC='clang'
    ),
    dict(
        name='stable_pg12',
        PG='REL_12_STABLE',
        GEOS='3.8',
        GDAL='release/3.0',
        PROJ='6.1.1',
        PG_CC='gcc'
    ),
    dict(
        name='stable_pg11',
        PG='REL_11_STABLE',
        GEOS='3.7',
        GDAL='release/2.4',
        PROJ='5.2',
        PG_CC='gcc'
    ),
    dict(
        name='stable_pg10',
        PG='REL_10_STABLE',
        GEOS='svn-3.6',
        GDAL='release/2.3',
        PROJ='4.9',
        PG_CC='gcc'
    ),
    dict(
        name='stable_pg96',
        PG='REL9_6_STABLE',
        GEOS='svn-3.6',
        GDAL='release/2.2',
        PROJ='4.9',
        PG_CC='gcc'
    ),
    dict(
        name='old_pg95',
        PG='REL9_5_STABLE',
        GEOS='svn-3.6',
        GDAL='release/2.1',
        PROJ='4.9',
        PG_CC='gcc'
    )
]

for env in environments:
    if env['PG_CC'] == 'clang':
        env['compiler_tag'] = "-clang"
    else:
        env['compiler_tag'] = ''

    versions = { k : ''.join(re.findall('\d+', v) or v) for k, v in env.items() }
    if env['name'] == 'latest':
        tag = 'latest{compiler_tag}'.format_map(versions)
    else:
        tag = 'pg{PG}{compiler_tag}-geos{GEOS}-gdal{GDAL}-proj{PROJ}'.format_map(versions)
    image = 'postgis/postgis-build-env:{}'.format(tag)

    subprocess.check_call([
        'docker', 'build',
        '--pull',
        '--build-arg', 'BUILD_DATE={}'.format(datetime.date.today().strftime("%Y%m%d")),
        '--build-arg', 'POSTGRES_BRANCH={PG}'.format_map(env),
        '--build-arg', 'GEOS_BRANCH={GEOS}'.format_map(env),
        '--build-arg', 'GDAL_BRANCH={GDAL}'.format_map(env),
        '--build-arg', 'PROJ_BRANCH={PROJ}'.format_map(env),
        '--build-arg', 'PG_CC={PG_CC}'.format_map(env),
        '-t', image,
        '.'
    ])
    subprocess.check_call([
        'docker', 'push', image
    ])
        
