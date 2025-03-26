from flask import Flask, render_template, request
from geopy.geocoders import Nominatim
import folium
import requests

app = Flask(__name__)

def get_coordinates(place_name):
    geolocator = Nominatim(user_agent="osm_route_optimizer")
    location = geolocator.geocode(place_name)
    if location:
        return location.latitude, location.longitude
    return None

def get_osm_route(start, end):
    base_url = "http://router.project-osrm.org/route/v1/driving/"
    coords = f"{start[1]},{start[0]};{end[1]},{end[0]}"
    response = requests.get(f"{base_url}{coords}?overview=full&geometries=geojson")
    if response.status_code == 200:
        data = response.json()
        if data["routes"]:
            route_info = data["routes"][0]
            distance = route_info["distance"] / 1000  # Convert to kilometers
            duration = route_info["duration"] / 60  # Convert to minutes
            return route_info["geometry"]["coordinates"], distance, duration
    return None, None, None

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        start_location_name = request.form["start_location"]
        end_location_name = request.form["end_location"]

        start_location = get_coordinates(start_location_name)
        end_location = get_coordinates(end_location_name)

        if start_location and end_location:
            route, distance, duration = get_osm_route(start_location, end_location)

            # Create a map
            m = folium.Map(location=start_location, zoom_start=13)
            folium.Marker(start_location, popup=f"Start: {start_location_name}", icon=folium.Icon(color="green")).add_to(m)
            folium.Marker(end_location, popup=f"End: {end_location_name}", icon=folium.Icon(color="red")).add_to(m)

            if route:
                route = [(lat, lon) for lon, lat in route]
                folium.PolyLine(route, color="blue", weight=5, opacity=0.7).add_to(m)

                # Add distance and duration to the map
                folium.Marker(
                    location=[(start_location[0] + end_location[0]) / 2, (start_location[1] + end_location[1]) / 2],
                    popup=f"Distance: {distance:.2f} km\nEstimated Time: {duration:.2f} mins",
                    icon=folium.Icon(color="orange")
                ).add_to(m)

            # Save map to HTML
            map_file = "templates/map.html"
            m.save(map_file)
            return render_template("map.html", distance=distance, duration=duration)

    return render_template("index.html")

if __name__ == "__main__":
    app.run(debug=True)