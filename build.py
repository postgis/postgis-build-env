#!/usr/bin/env python3
import argparse
import datetime
import json
import os
import re
import subprocess

all_environments=[
    # put last modified first to iterate faster
        dict(
            name='latest',
            PG='master',
            GEOS='main',
            GDAL='master',
            PROJ='master',
            PG_CC='gcc',
            SFCGAL='master'
        )    ,
        dict(
            name='stable_pg18',
            PG='REL_18_STABLE',
            GEOS='main',
            GDAL='release/3.11',
            PROJ='9.6',
            PG_CC='gcc',
            SFCGAL='v2.2.0'
        ) ,

        dict(
            name='stable_pg17',
            PG='REL_17_STABLE',
            GEOS='3.13',
            GDAL='release/3.9',
            PROJ='9.4',
            PG_CC='gcc',
            SFCGAL='v2.1.0'
        ),
        dict(
            name='stable_pg16',
            PG='REL_16_STABLE',
            GEOS='3.12',
            GDAL='release/3.8',
            PROJ='9.2.1',
            PG_CC='gcc'
        ),
        dict(
            name='stable_pg15',
            PG='REL_15_STABLE',
            GEOS='3.11',
            GDAL='release/3.5',
            PROJ='9.0',
            PG_CC='clang'
        ),
        dict(
            name='stable_pg15',
            PG='REL_15_STABLE',
            GEOS='3.11',
            GDAL='release/3.5',
            PROJ='9.0',
            PG_CC='clang'
        ),
        dict(
            name='stable_pg15',
            PG='REL_15_STABLE',
            GEOS='3.11',
            GDAL='release/3.5',
            PROJ='9.0',
            PG_CC='gcc'
        ),
        dict(
            name='stable_pg15',
            PG='REL_15_STABLE',
            GEOS='3.11',
            GDAL='release/3.5',
            PROJ='9.0',
            PG_CC='gcc'
        ),
        dict(
            name='stable_pg14',
            PG='REL_14_STABLE',
            GEOS='3.10',
            GDAL='release/3.4',
            PROJ='8.0',
            PG_CC='gcc'
        ),
        dict(
            name='stable_pg14',
            PG='REL_14_STABLE',
            GEOS='3.10',
            GDAL='release/3.4',
            PROJ='8.0',
            PG_CC='clang'
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


def build_metadata(env):
    env = env.copy()
    if env['PG_CC'] == 'clang':
        env['compiler_tag'] = "-clang"
    else:
        env['compiler_tag'] = ''

    env.setdefault('SFCGAL', 'master')
    versions = { k : ''.join(re.findall(r'\d+', v) or v) for k, v in env.items() }
    if env['name'] == 'latest':
        tag = 'latest{compiler_tag}'.format_map(versions)
    else:
        tag = 'pg{PG}{compiler_tag}-geos{GEOS}-gdal{GDAL}-proj{PROJ}'.format_map(versions)
    env['tag'] = tag
    return env


def select_environments(env_batch, tag):
    environments = all_environments[0:3] if env_batch == 'weekly' else all_environments
    environments = [build_metadata(env) for env in environments]
    if tag:
        environments = [env for env in environments if env['tag'] == tag]
        if not environments:
            raise SystemExit("No environment generates tag {}".format(tag))
    return environments


def unique_by_tag(environments):
    seen = set()
    unique = []
    for env in environments:
        if env['tag'] in seen:
            continue
        seen.add(env['tag'])
        unique.append(env)
    return unique


parser = argparse.ArgumentParser()
parser.add_argument('batch', nargs='?', default='all', choices=['all', 'weekly'])
parser.add_argument('--repository', action='append', default=[],
                    help='Repository to tag and publish, for example postgis/postgis-build-env')
parser.add_argument('--tag', help='Build only the environment that generates this tag')
parser.add_argument('--print-matrix', action='store_true',
                    help='Print a GitHub Actions matrix and exit')
parser.add_argument('--push', dest='push', action='store_true', default=True)
parser.add_argument('--no-push', dest='push', action='store_false')
args = parser.parse_args()

repositories = args.repository or ['postgis/postgis-build-env']
environments = select_environments(args.batch, args.tag)

if args.print_matrix:
    print(json.dumps({
        'include': [
            {
                'name': env['name'],
                'tag': env['tag'],
                'pg': env['PG'],
                'geos': env['GEOS'],
                'gdal': env['GDAL'],
                'proj': env['PROJ'],
                'compiler': env['PG_CC'],
                'sfcgal': env['SFCGAL'],
            }
            for env in unique_by_tag(environments)
        ]
    }))
    raise SystemExit(0)

print("Env Batch selected:", args.batch, environments)

for env in environments:
    images = ['{}:{}'.format(repository, env['tag']) for repository in repositories]

    build_command = [
        'docker', 'build',
        '--pull',
        '--build-arg', 'BUILD_DATE={}'.format(datetime.date.today().strftime("%Y%m%d")),
        '--build-arg', 'POSTGRES_BRANCH={PG}'.format_map(env),
        '--build-arg', 'GEOS_BRANCH={GEOS}'.format_map(env),
        '--build-arg', 'GDAL_BRANCH={GDAL}'.format_map(env),
        '--build-arg', 'PROJ_BRANCH={PROJ}'.format_map(env),
        '--build-arg', 'PG_CC={PG_CC}'.format_map(env),
        '--build-arg', 'SFCGAL_BRANCH={SFCGAL}'.format_map(env),
        '--build-arg', 'BUILD_THREADS={}'.format(os.environ.get('BUILD_THREADS', 'auto')),
    ]
    for image in images:
        build_command.extend(['-t', image])
    build_command.append('.')
    subprocess.check_call(build_command)
    if args.push:
        for image in images:
            subprocess.check_call(['docker', 'push', image])
