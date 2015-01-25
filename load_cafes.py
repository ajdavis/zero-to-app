import csv
import json
import re
import sys

# Pattern matching simple decimal numbers.
float_pat = r'-?[0-9]+(\.[0-9]+)?'

# Pattern matching addresses, which are like:
# '123 MAIN ST (40.73, -73.98)'
location_pat = re.compile(
    r'(?P<address>(.|\n)+)\n\((?P<lat>%s), (?P<lon>%s)' % (
        float_pat, float_pat),
    re.MULTILINE)

csv_in = csv.DictReader(open('sidewalk-cafes.csv'))
with open('sidewalk-cafes-2.csv', 'w+') as f:

    n_lines = 0
    for line in csv_in:
        name = (line.get('Camis Trade Name') or line.get('Entity Name'))
        name = re.sub(r'\s+', ' ', name).strip().title()
        name = name.replace("'S", "'s")  # title() bug, e.g. "Jesse'S".
        street = line['Address Street Name']
        street = re.sub(r'\s+', ' ', street).strip().title()
        location_field = line['Location 1']
        match = location_pat.match(location_field)
        assert match, repr(location_field)
        group_dict = match.groupdict()
        lon, lat = float(group_dict['lon']), float(group_dict['lat'])
        f.write(json.dumps({
            'name': name,
            'street': street,
            'location': {
                'type': 'Point',
                'coordinates': [lon, lat]}}))

        f.write('\n')

        # Show progress.
        sys.stdout.write('.')
        sys.stdout.flush()

print('')
