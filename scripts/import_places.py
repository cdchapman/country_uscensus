#!/usr/bin/env python3
# PYTHON_ARGCOMPLETE_OK
# This file is part of Tryton.  The COPYRIGHT file at the top level of
# this repository contains the full copyright notices and license terms.
from __future__ import print_function

import csv
import os
import sys
from argparse import ArgumentParser

from urllib.error import HTTPError
from urllib.parse import urljoin
from urllib.request import urlopen

from io import BytesIO, TextIOWrapper

try:
    import argcomplete
except ImportError:
    argcomplete = None

try:
    from progressbar import ETA, Bar, ProgressBar, SimpleProgress
except ImportError:
    ProgressBar = None

try:
    from proteus import Model, config
except ImportError:
    prog = os.path.basename(sys.argv[0])
    sys.exit("proteus must be installed to use %s" % prog)

CLASSCODES = {
    'independent city (united states)': ['C7'],
    'consolidated city-county': ['C3'],
    'county': ['H1', 'H4', 'H5', 'H6'],
    'county subdivision': [
        'T1', 'T5', 'T9', 'Z1', 'Z2', 'Z3', 'Z5', 'Z7', 'Z9'],
    'division': ['M2', 'U1', 'U2'],
    'incorporated place': ['C1', 'C2', 'C5', 'C6', 'C8', 'C9'],
}
CLASSCODES2TYPE = {c: t for t, a in CLASSCODES.items() for c in a}

def _progress(iterable):
    if ProgressBar:
        pbar = ProgressBar(
            widgets=[SimpleProgress(), Bar(), ETA()])
    else:
        pbar = iter
    return pbar(iterable)


def fetch(url):
    sys.stderr.write('Fetching')
    try:
        responce = urlopen(url)
    except HTTPError as e:
        sys.exit("\nError downloading %s: %s" % (url, e.reason))
    data = responce.read()
    print('.', file=sys.stderr)
    return data


def get_states():
    Country = Model.get('country.country')
    Subdivision = Model.get('country.subdivision')

    try:
        _, = Country.find([('code', '=', 'US')])
    except ValueError:
        sys.exit("Error finding the country of the United States: "
                 "countries must be imported first using the "
                 "'trytond_import_countries' script.")

    domain = [
        ('country.code', '=', 'US'),
        ('parent', '=', None),
    ]

    return {c.code[-2:]: c for c in Subdivision.find(domain)}

def get_counties(code=None):
    Subdivision = Model.get('country.subdivision')

    domain = [
        ('country.code', '=', 'US'),
        ('fips_level', '=', 'county'),
    ]

    if code:
        domain.append(('parent.code', '=', code))

    return {
        (c.parent.code, c.code_fips): c for c in Subdivision.find(domain)}

def get_places(code=None):
    Subdivision = Model.get('country.subdivision')

    domain = [
        ('country.code', '=', 'US'),
        ('fips_level', '=', 'place'),
    ]

    if code:
        domain.append(('parent.parent.code', '=', code))

    return {(c.parent.parent.code, c.code_fips): c
            for c in Subdivision.find(domain)}

def update_states(subdivisions, data):
    print("Update states", file=sys.stderr)
    Subdivision = Model.get('country.subdivision')

    records = []
    for row in _progress(list(csv.DictReader(
            TextIOWrapper(BytesIO(data), encoding='utf-8'), delimiter='|'))):
        code = row['STATE']
        if code in subdivisions:
            record = subdivisions[code]
        else:
            print(f"Could not find a subdivision with code '{code}'.")
            continue

        record.code_fips = row['STATEFP']
        record.code_gnis = int(row['STATENS'])

        records.append(record)

    Subdivision.save(records)
    return {c.code_fips: c for c in records}

def update_counties(states, counties, data):
    print("Update counties", file=sys.stderr)
    Subdivision = Model.get('country.subdivision')

    records = []
    for row in _progress(list(csv.DictReader(
            TextIOWrapper(BytesIO(data), encoding='utf-8'), delimiter='|'))):
        state = states[row['STATEFP']]
        subdivision_code = state.code
        county_fips = row['COUNTYFP']
        if (subdivision_code, county_fips) in counties:
            record = counties[(subdivision_code, county_fips)]
        else:
            record = Subdivision(parent=state, code_fips=county_fips)
        record.name = row['COUNTYNAME']
        record.code_gnis = int(row['COUNTYNS'])
        record.type = CLASSCODES2TYPE.get(row['CLASSFP'])
        record.country = state.country

        records.append(record)

    Subdivision.save(records)
    return {(c.parent.code, c.code_fips): c for c in records}

def update_places(states, counties, places, data):
    print("Update places", file=sys.stderr)
    Subdivision = Model.get('country.subdivision')

    records = []
    for row in _progress(list(csv.DictReader(
            TextIOWrapper(BytesIO(data), encoding='utf-8'), delimiter='|'))):
        state = states[row['STATEFP']]
        subdivision_code = state.code
        county = counties[(subdivision_code, row['COUNTYFP'])]
        place_fips = row['PLACEFP']
        if (subdivision_code, place_fips) in places:
            record = places[(subdivision_code, place_fips)]
        else:
            record = Subdivision(parent=county, code_fips=place_fips)
        record.name = row['PLACENAME']
        record.code_gnis = int(row['PLACENS'])
        record.type = CLASSCODES2TYPE.get(row['CLASSFP'])
        record.country = state.country

        records.append(record)

    Subdivision.save(records)

def main(database, args, config_file=None):
    config.set_trytond(database, config_file=config_file)
    with config.get_config().set_context(active_test=False):
        do_import(args)

def do_import(args):
    _base = 'https://www2.census.gov/geo/docs/reference/codes2020/'
    _states = 'national_state2020.txt'
    _counties = 'national_county2020.txt'
    _county = 'cou/st{fips}_{code}_cou2020.txt'
    _places = 'national_place_by_county2020.txt'
    _place = 'place_by_cou/st{fips}_{code}_place_by_county2020.txt'

    states_by_code = get_states()
    states = update_states(states_by_code, fetch(urljoin(_base, _states)))

    if args.all:
        county_url = urljoin(_base, _counties)
        counties = get_counties()
        counties = update_counties(states, counties, fetch(county_url))

        place_url = urljoin(_base, _places)
        places = get_places()
        update_places(states, counties, places, fetch(place_url))

    for code in args.codes:
        print(code, file=sys.stderr)
        state = states_by_code[code.upper()]
        code_subdivision = 'US-%s' % code.upper()

        counties = get_counties(code=code_subdivision)
        county_url = urljoin(_base, _county.format(
            fips=state.code_fips, code=code.lower()))
        counties = update_counties(states, counties, fetch(county_url))

        places = get_places(code=code_subdivision)
        place_url = urljoin(_base, _place.format(
            fips=state.code_fips, code=code.lower()))
        update_places(states, counties, places, fetch(place_url))


def run():
    parser = ArgumentParser()
    parser.add_argument('-d', '--database', dest='database', required=True)
    parser.add_argument('-c', '--config', dest='config_file',
        help='the trytond config file')
    parser.add_argument('--all', action='store_true',
        help='import codes for all states')
    parser.add_argument('codes', nargs='*', default=[])
    if argcomplete:
        argcomplete.autocomplete(parser)

    args = parser.parse_args()
    main(args.database, args, args.config_file)


if __name__ == '__main__':
    run()
