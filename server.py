import urllib

from bson import json_util
from flask import Flask, redirect, url_for, Response
from flask import render_template
from flask import request
from pymongo import MongoClient
from werkzeug.routing import NumberConverter


db = MongoClient().test
app = Flask(__name__, static_path='/zero-to-app/static')


# Accept more 'float' numbers than Werkzeug does by default: also accept
# numbers beginning with minus, or with no trailing digits.
# From https://gist.github.com/akhenakh/3376839
class NegativeFloatConverter(NumberConverter):
    regex = r'\-?\d+(\.\d+)?'
    num_convert = float

    def __init__(self, mapping, minimum=None, maximum=None):
        NumberConverter.__init__(self, mapping, 0, minimum, maximum)


app.url_map.converters['float'] = NegativeFloatConverter


def address_to_lat_lon(addr):
    url = 'http://maps.google.com/?q=' + urllib.quote(addr) + '&output=js'

    # Get XML location.
    xml = urllib.urlopen(url).read()

    if '<error>' in xml:
        raise Exception('%s\n' % url)
    else:
        # Strip lat/long coordinates from XML.
        center = xml[xml.find('{center')+9:xml.find('}', xml.find('{center'))]
        center = center.replace('lat:', '').replace('lng:', '')
        lat, lng = center.split(',')
        return float(lat), float(lng)


@app.route('/zero-to-app/near/<float:lat>/<float:lon>')
def near(lat, lon):
    return render_template('near.html', results=results, lat=lat, lon=lon)


@app.route('/zero-to-app/results/json', methods=['POST'])
def results():
    request_data = request.get_json()
    num = int(request_data['num'])
    lat = float(request_data['lat'])
    lon = float(request_data['lon'])

    # NOTE: lon, lat order!!
    result = db.command(
        'geoNear', 'cafes',
        near={'type': 'Point', 'coordinates': [lon, lat]},
        spherical=True,
        num=num)

    return Response(json_util.dumps(result), mimetype='application/json')


@app.route('/zero-to-app/address', methods=['POST'])
def address():
    lat, lon = address_to_lat_lon(request.form.get('address'))
    return redirect(url_for('near', lat=lat, lon=lon))


@app.route('/zero-to-app')
def main():
    n_cafes = db.cafes.count()
    return render_template('main.html', n_cafes=n_cafes)


if __name__ == '__main__':
    print('Go visit http://localhost:5000/zero-to-app')
    app.run(host='0.0.0.0', debug=True)

