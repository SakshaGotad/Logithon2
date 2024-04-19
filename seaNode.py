import folium
from folium.plugins import MarkerCluster
import json
import ipywidgets as widgets
from IPython.display import display

# Load port GeoJSON data
port_geojson_path = 'C:/Desktop/docs/third year/sem 6/Pollux/NEW/global-ports-3.geojson'

with open(port_geojson_path, 'r') as f:
    all_ports_data = json.load(f)

# Define the function to check if coordinates are within the Mediterranean Sea boundaries
def is_in_mediterranean(coords):
    min_longitude = -6.0
    max_longitude = 36.0
    min_latitude = 30.0
    max_latitude = 46.0
    
    longitude = coords[0]
    latitude = coords[1]
    return min_longitude <= longitude <= max_longitude and min_latitude <= latitude <= max_latitude

# Create a Folium map centered around the Mediterranean Sea
m = folium.Map(location=[35, 15], zoom_start=5)

# Create a MarkerCluster layer for the ports
marker_cluster = MarkerCluster().add_to(m)

# Filter and add Mediterranean Sea ports to the map with popups showing their names
visible_ports_data = [feature for feature in all_ports_data['features'] if is_in_mediterranean(feature['geometry']['coordinates'])]

ports_data = {feature['properties']['portname']: feature['geometry']['coordinates'] for feature in visible_ports_data}

for feature in visible_ports_data:
    port_coords = feature['geometry']['coordinates']
    port_name = feature['properties'].get('portname', 'Unknown')
    popup_text = f"Port Name: {port_name}"
    
    folium.Marker(location=port_coords[::-1], popup=popup_text).add_to(marker_cluster)

# Create dropdown widgets for port selection
ports = list(ports_data.keys())
port1_dropdown = widgets.Dropdown(options=ports, description='Port 1:')
port2_dropdown = widgets.Dropdown(options=ports, description='Port 2:')
submit_button = widgets.Button(description='Submit')

# Function to handle button click event
def on_submit_button_clicked(button):
    port1 = port1_dropdown.value
    port2 = port2_dropdown.value
    print(f'Selected Ports: {port1} and {port2}')

    # Get coordinates for the selected ports
    port1_coords = ports_data[port1]
    port2_coords = ports_data[port2]

    # Create a new map with only the two selected ports and a line between them
    new_map = folium.Map(location=[(port1_coords[1] + port2_coords[1]) / 2, (port1_coords[0] + port2_coords[0]) / 2], zoom_start=5)
    folium.Marker(port1_coords[::-1], popup=port1).add_to(new_map)
    folium.Marker(port2_coords[::-1], popup=port2).add_to(new_map)
    folium.PolyLine(locations=[port1_coords[::-1], port2_coords[::-1]], color='blue', weight=2, opacity=1).add_to(new_map)
    
    # Display the new map
    display(new_map)

# Attach the button click event handler
submit_button.on_click(on_submit_button_clicked)

# Display the widgets and map
display(port1_dropdown, port2_dropdown, submit_button, m)
