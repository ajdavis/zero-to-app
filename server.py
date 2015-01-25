import urllib

from bson import json_util
from flask import Flask, Response
from flask import render_template
from flask import request
from pymongo import MongoClient


db = MongoClient().test
app = Flask(__name__, static_path='/zero-to-app/static')


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


@app.route('/zero-to-app/address/json', methods=['POST'])
def address():
    lat, lon = address_to_lat_lon(request.get_json()['address'])
    return Response(json_util.dumps({'lat': lat, 'lon': lon}),
                    mimetype='application/json')


@app.route('/zero-to-app')
def main():
    return render_template('index.html')


if __name__ == '__main__':
    print('Go visit http://localhost:5000/zero-to-app')
    app.run(host='0.0.0.0', debug=True)
