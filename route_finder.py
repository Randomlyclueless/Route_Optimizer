import osmnx as ox
import networkx as nx
import folium
import heapq

# Configure OSMnx settings
ox.settings.timeout = 300
ox.settings.overpass_endpoint = "https://overpass.kumi.systems/api/interpreter"

def get_coordinates(place_name):
    """Get latitude and longitude for a place name."""
    try:
        return ox.geocode(place_name)
    except Exception as e:
        print(f"Error: Could not find coordinates for '{place_name}'. Please check the name and try again.")
        return None

def dijkstra_manual(graph, start_node, end_node):
    """Manually implement Dijkstra's algorithm to find the shortest path."""
    distances = {node: float('inf') for node in graph.nodes}
    distances[start_node] = 0
    previous_nodes = {node: None for node in graph.nodes}
    priority_queue = [(0, start_node)]

    while priority_queue:
        current_distance, current_node = heapq.heappop(priority_queue)

        if current_node == end_node:
            break

        if current_distance > distances[current_node]:
            continue

        for neighbor, edge_data in graph[current_node].items():
            # Correct edge weight access
            weight = edge_data.get('length', 1)  
            distance = current_distance + weight

            if distance < distances[neighbor]:
                distances[neighbor] = distance
                previous_nodes[neighbor] = current_node
                heapq.heappush(priority_queue, (distance, neighbor))

    # Reconstruct the shortest path
    path = []
    current = end_node
    while current is not None:
        path.append(current)
        current = previous_nodes[current]
    path.reverse()

    if len(path) < 2:
        print("No valid path found.")
        return []

    return path

def visualize_route(graph, shortest_path, start_point, end_point):
    """Visualize the route on a map using Folium."""
    if not shortest_path:
        print("No valid route to visualize.")
        return

    # Convert nodes to coordinates
    route_coordinates = [(graph.nodes[node]['y'], graph.nodes[node]['x']) for node in shortest_path]

    # Create a map centered at the start point
    m = folium.Map(location=start_point, zoom_start=13)

    # Add markers for start and end points
    folium.Marker(location=start_point, popup="Start", icon=folium.Icon(color="green")).add_to(m)
    folium.Marker(location=end_point, popup="End", icon=folium.Icon(color="red")).add_to(m)

    # Draw route line
    folium.PolyLine(locations=route_coordinates, color="blue", weight=5, opacity=0.7).add_to(m)

    # Save map to file
    m.save("shortest_route.html")
    print("Map saved as 'shortest_route.html'. Open it in your browser.")

def main():
    # User input for starting and ending locations
    start_place = input("Enter the starting point (e.g., Pune, Maharashtra): ")
    end_place = input("Enter the ending point (e.g., Mumbai, Maharashtra): ")

    # Get coordinates for start and end points
    start_point = get_coordinates(start_place)
    end_point = get_coordinates(end_place)

    if start_point is None or end_point is None:
        print("Invalid location(s). Exiting.")
        return

    # Fetch road network
    print("Fetching road network data...")
    try:
        graph = ox.graph_from_place("Pune, India", network_type='drive')
    except Exception as e:
        print(f"Failed to fetch road network data: {e}")
        return

    # Find nearest nodes to start and end points
    start_node = ox.distance.nearest_nodes(graph, start_point[1], start_point[0])
    end_node = ox.distance.nearest_nodes(graph, end_point[1], end_point[0])

    # Get shortest path using Dijkstra
    print("Calculating shortest path using Dijkstra's algorithm...")
    shortest_path = dijkstra_manual(graph, start_node, end_node)

    if shortest_path:
        print(f"Shortest path found with {len(shortest_path)} nodes.")
    else:
        print("No valid path found.")

    # Visualize the route
    visualize_route(graph, shortest_path, start_point, end_point)

if __name__ == "__main__":
    main()
