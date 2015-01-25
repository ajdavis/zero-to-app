Zero to App in 30 Minutes with Python and MongoDB
=================================================

Build a Yelp-like app that finds New York City cafés and lets you rate them and
comment on them. You'll see how rapidly a simple app can be built using open
source tools and a public data set.

Café data from [NYC Open Data](https://data.cityofnewyork.us/Business/Sidewalk-Cafes/6k68-kc8u).

Adapted from
[an example app I built](http://emptysqua.re/blog/paging-geo-mongodb/) to
demonstrate MongoDB 2.6's new "minDistance" operator.

Setup
-----
Install and run a local [MongoDB](http://www.mongodb.org/downloads) server.

Install the Python packages in `requirements.txt`.

Load café data and index it:

```
mongoimport --drop --collection cafes sidewalk-cafes.csv
mongo --eval "printjson(db.cafes.createIndex({location: '2dsphere'}))"
```

Run
---

Run `python server.py` from the project directory.

About
-----

Author: A. Jesse Jiryu Davis
