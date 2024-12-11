import streamlit as st
import folium
from geopy.geocoders import Nominatim
import math
from folium.plugins import AntPath

# Haversine formula to calculate the great-circle distance
def haversine(coord1, coord2):
    lat1, lon1 = coord1
    lat2, lon2 = coord2
    R = 6371  # Earth's radius in kilometers
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)
    a = math.sin(delta_phi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c  

# Function to calculate the initial and final bearing
def calculate_bearing(coord1, coord2):
    lat1, lon1 = map(math.radians, coord1)
    lat2, lon2 = map(math.radians, coord2)
    delta_lon = lon2 - lon1
    x = math.sin(delta_lon) * math.cos(lat2)
    y = math.cos(lat1) * math.sin(lat2) - math.sin(lat1) * math.cos(lat2) * math.cos(delta_lon)
    initial_bearing = math.atan2(x, y)
    initial_bearing = (math.degrees(initial_bearing) + 360) % 360
    final_bearing = (initial_bearing + 180) % 360
    return initial_bearing, final_bearing

# Geocoding with geopy
geolocator = Nominatim(user_agent="GreatCircleDistanceApp")

def get_coordinates(location_name):
    location = geolocator.geocode(location_name)
    if location:
        return location.latitude, location.longitude
    else:
        st.warning(f"Could not find coordinates for {location_name}.")
        return None

# Function to create a map
def create_map(koordinat1, koordinat2, basemap="OpenStreetMap"):
    # Create a folium map centered around the midpoint
    m = folium.Map(location=[(koordinat1[0] + koordinat2[0]) / 2, (koordinat1[1] + koordinat2[1]) / 2],
                   zoom_start=3, tiles=basemap)
    
    # Plotting markers for both points
    folium.Marker(location=koordinat1, popup="Point 1").add_to(m)
    folium.Marker(location=koordinat2, popup="Point 2").add_to(m)
    
    # Draw a great circle path using AntPath plugin
    AntPath([koordinat1, koordinat2], color="blue", weight=2).add_to(m)
    
    return m

# Streamlit App
st.set_page_config(page_title="Great Circle Distance Calculator", page_icon="🌍", layout="wide")
st.title("🌍 Great Circle Distance Calculator")

# Input method and coordinates
input_method = st.sidebar.selectbox("🔽 Select Input Method", ["Location Names", "Manual Coordinates"])

koordinat1 = None
koordinat2 = None

if input_method == "Location Names":
    location_1_name = st.sidebar.text_input("📍 Location Name 1", "Jakarta, Indonesia")
    location_2_name = st.sidebar.text_input("📍 Location Name 2", "New York, USA")
    koordinat1 = get_coordinates(location_1_name)
    koordinat2 = get_coordinates(location_2_name)
elif input_method == "Manual Coordinates":
    lat1 = st.sidebar.number_input("📍 Latitude of Location 1", value=-6.2)
    lon1 = st.sidebar.number_input("📍 Longitude of Location 1", value=106.816666)
    lat2 = st.sidebar.number_input("📍 Latitude of Location 2", value=40.712776)
    lon2 = st.sidebar.number_input("📍 Longitude of Location 2", value=-74.005974)
    koordinat1 = (lat1, lon1)
    koordinat2 = (lat2, lon2)

# Display results if both coordinates are valid
if koordinat1 and koordinat2:
    # Calculate distance and bearing
    jarak_haversine = haversine(koordinat1, koordinat2)
    initial_bearing, final_bearing = calculate_bearing(koordinat1, koordinat2)

    st.markdown(f"**Haversine Distance:** {jarak_haversine:.2f} km")
    st.markdown(f"**Initial Bearing:** {initial_bearing:.2f}°")
    st.markdown(f"**Final Bearing:** {final_bearing:.2f}°")
    
    # Choose basemap
    basemap = st.selectbox("🌍 Choose Basemap", ["OpenStreetMap", "Stamen Terrain", "Stamen Toner", "CartoDB positron"])
    
    # Create and display map
    m = create_map(koordinat1, koordinat2, basemap)
    folium_static(m)  # Show map in Streamlit
else:
    st.warning("Please provide valid inputs to calculate coordinates.")
