from geopy.geocoders import Nominatim

def get_coordinates(place_name):
    geolocator = Nominatim(user_agent="osm_route_optimizer")
    location = geolocator.geocode(place_name)
    if location:
        return location.latitude, location.longitude  # Return (lat, lon)
    else:
        print(f"Could not find coordinates for {place_name}")
        return None

# Example usage
pune_location = "Mangalwar peth, Pune"
coords = get_coordinates(pune_location)

if coords:
    print(f"Coordinates of {pune_location}: {coords}")


import folium
import requests

# Function to get route from OSM
def get_osm_route(start, end):
    base_url = "http://router.project-osrm.org/route/v1/driving/"
    coords = f"{start[1]},{start[0]};{end[1]},{end[0]}"
    response = requests.get(f"{base_url}{coords}?overview=full&geometries=geojson")

    if response.status_code == 200:
        data = response.json()
        if data["routes"]:
            return data["routes"][0]["geometry"]["coordinates"]
    return None

# Define locations
start_location = get_coordinates("Mangalwar peth, Pune")  # Start point
end_location = get_coordinates("Swargate, Pune")  # Destination

if start_location and end_location:
    # Get optimized route from OSM
    route = get_osm_route(start_location, end_location)

    # Create a map
    m = folium.Map(location=start_location, zoom_start=13)

    # Add markers
    folium.Marker(start_location, popup="Start:Mangalwar peth", icon=folium.Icon(color="green")).add_to(m)
    folium.Marker(end_location, popup="End: Swargate", icon=folium.Icon(color="red")).add_to(m)

    # Draw route if found
    if route:
        route = [(lat, lon) for lon, lat in route]  # Convert to (lat, lon)
        folium.PolyLine(route, color="blue", weight=5, opacity=0.7).add_to(m)
        print("Route found and added to the map.")
    else:
        print("No route found.")

    # Save map
    m.save("osm_route_map.html")
    print("Map saved as osm_route_map.html - Open it in your browser!")

    """--------------------
        """

