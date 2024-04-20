var map = L.map('map').setView([51.505, -0.09], 13);

L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
}).addTo(map);

var flagIcon = L.icon({
    iconUrl: 'flag.jpg',
    iconSize: [30, 30],
    iconAnchor: [15, 30],
});

var startFlag = L.marker([51.505, -0.09], { icon: flagIcon, draggable: true }).addTo(map);
var endFlag = L.marker([51.515, -0.1], { icon: flagIcon, draggable: true }).addTo(map);

startFlag.on('dragend', updateRoute);
endFlag.on('dragend', updateRoute);

var route;

function updateRoute() {
    var startLatLng = startFlag.getLatLng();
    var endLatLng = endFlag.getLatLng();

    // Remove previous route if exists
    if (route) {
        map.removeLayer(route);
    }

    // Fetch route using OpenRouteService
    fetchRoute(startLatLng, endLatLng);
}

function fetchRoute(start, end) {
    var url = `https://api.openrouteservice.org/v2/directions/driving-car?start=${start.lng},${start.lat}&end=${end.lng},${end.lat}`;

    fetch(url, {
        method: 'GET',
        headers: {
            'Authorization': '5b3ce3597851110001cf624872f31c52a8ea4ba2b8af751e1eb70011'
        }
    })
    .then(response => response.json())
    .then(data => {
        var routeCoordinates = data.features[0].geometry.coordinates.map(coord => [coord[1], coord[0]]);
        route = L.polyline(routeCoordinates, { color: 'blue' }).addTo(map);
    })
    .catch(error => {
        console.error('Error fetching route:', error);
    });
}
