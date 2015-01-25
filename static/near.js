$(function() {
    // CONFIGURATION.
    var rowsPerPage = 10;

    var resultTemplate = Handlebars.compile($('#result-template').html()),
        infoWindowTemplate = Handlebars.compile($('#info-window-template').html()),
        $searchForm = $('#search-form');

    Handlebars.registerHelper('distanceFormat', function(distance) {
        return distance.toFixed(0).toString();
    });

    // GLOBAL STATE.
    // Rows are kept sorted by distance.
    // Each has id, seq, distance, name, latlon, and street.
    var lat = 0,
        lon = 0,
        rows = [],
        map,
        mapMarkers = [],
        centerMarker,
        mapInfoWindows = [];

    // Generic error handler.
    function errBack(jqXHR, textStatus, errorThrown) {
        // Failure.
        alert(errorThrown);
    }

    // Get at most 'num' rows from server and set to global 'rows'.
    function getRows(num, callback) {
        $.ajax({
            url: '/zero-to-app/results/json',
            type: 'post',
            contentType: 'application/json',
            data: JSON.stringify({
                lat: lat,
                lon: lon,
                num: num
            })
        }).success(function(data) {
            rows = [];
            data.results.forEach(function(result) {
                var obj = result.obj,
                    name = (
                        obj['Camis Trade Name'] || obj['Entity Name']
                    ).toLocaleLowerCase(),
                    street = obj['Address Street Name'].toLocaleLowerCase(),
                    lonlat = obj.location.coordinates,
                    row = {
                        id: obj._id['$oid'],
                        seq: rows.length + 1,
                        distance: result.dis,
                        name: name,
                        street: street,
                        // Reorder the GeoJSON coordinates from server.
                        latlon: [lonlat[1], lonlat[0]]
                    };

                rows.push(row);
            });

            callback();

        }).error(errBack);
    }

    function updateTable() {
        $('#results')
            .html(resultTemplate({rows: rows}))
            .find('tr').click(function() {
                var rowId = $(this).attr('data-rowid');

                // Find the appropriate map info window and show it. There are at
                // most 'rowsPerPage' info windows in the array.
                for (var i = 0; i < mapInfoWindows.length; ++i) {
                    var infoWindow = mapInfoWindows[i];
                    if (infoWindow.rowId == rowId) {
                        closeAllInfoWindows();
                        infoWindow.open(map, infoWindow.marker);
                        return;
                    }
                }
            });
    }

    function updateMap() {
        clearMapPoints();
        addPointsToMap(rows);
        var center = new google.maps.LatLng(lat, lon);
        centerMarker.setPosition(center);
        map.setCenter(center);
        map.setZoom(14);
    }

    // Display the table and map.
    function showPage() {
        function onRowsReady() {
            updateTable();
            updateMap();
        }
        
        getRows(rowsPerPage, onRowsReady);
    }

    // Map stuff.
    function initializeMap() {
        var center = new google.maps.LatLng(lat, lon);
        var mapOptions = {
            zoom: 14,
            center: center,
            mapTypeId: google.maps.MapTypeId.ROADMAP
        };

        map = new google.maps.Map(
            document.getElementById('map-canvas'),
            mapOptions);

        // Center point.
        centerMarker = new google.maps.Marker({
            map: map,
            draggable: true,
            animation: google.maps.Animation.DROP,
            position: center
        });

        google.maps.event.addListener(centerMarker, 'dragend', function() {
            lat = centerMarker.getPosition().lat();
            lon = centerMarker.getPosition().lng();
            showPage();
        });

        // Start.
        $searchForm.submit();
    }

    google.maps.event.addDomListener(window, 'load', initializeMap);

    function makeInfoWindow(row, marker) {
        var contentString = infoWindowTemplate(row);
        var infoWindow = new google.maps.InfoWindow({content: contentString});
        infoWindow.rowId = row.id;
        infoWindow.marker = marker;
        google.maps.event.addListener(marker, 'click', function() {
            closeAllInfoWindows();
            infoWindow.open(map, marker);
        });
        return infoWindow;
    }

    function clearMapPoints() {
        mapMarkers.forEach(function(marker) {
            marker.setMap(null);
        });

        mapMarkers = [];
        closeAllInfoWindows();
        mapInfoWindows = [];
    }

    function closeAllInfoWindows() {
        mapInfoWindows.forEach(function(infoWindow) {
            infoWindow.close();
        })
    }

    // Add a list of [lat, lon] pairs.
    function addPointsToMap(rowsShown) {
        var circle = {
            path: google.maps.SymbolPath.CIRCLE,
              fillColor: "blue",
              fillOpacity: 0.5,
              scale: 6,
              strokeColor: "black",
              strokeWeight: 1
        };

        rowsShown.forEach(function(row) {
            var latlng = new google.maps.LatLng(row.latlon[0], row.latlon[1]),
                marker = new google.maps.Marker({
                    map: map,
                    draggable: false,
                    position: latlng,
                    icon: circle
                });

            mapMarkers.push(marker);
            mapInfoWindows.push(makeInfoWindow(row, marker));
        });
    }

    showPage();
    $searchForm.submit(function() {
        var geocoder = new google.maps.Geocoder();
        geocoder.geocode({address: $('#address').val()}, function(results) {
            var loc = results[0].geometry.location;
            lat = loc.lat();
            lon = loc.lng();
            showPage();
        });

        return false;
    });
});

