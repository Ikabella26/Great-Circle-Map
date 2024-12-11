import streamlit as st
import math
import plotly.graph_objects as go
from geopy.geocoders import Nominatim

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

    # Final bearing
    final_bearing = (initial_bearing + 180) % 360
    return initial_bearing, final_bearing

# Function to interpolate the great-circle path
def interpolate_great_circle(coord1, coord2, num_points=100):
    lat1, lon1 = coord1
    lat2, lon2 = coord2
    points = []

    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
    delta_sigma = math.acos(math.sin(lat1) * math.sin(lat2) + math.cos(lat1) * math.cos(lat2) * math.cos(lon2 - lon1))

    for i in range(num_points):
        A = math.sin((1 - i / (num_points - 1)) * delta_sigma) / math.sin(delta_sigma)
        B = math.sin(i / (num_points - 1) * delta_sigma) / math.sin(delta_sigma)
        x = A * math.cos(lat1) * math.cos(lon1) + B * math.cos(lat2) * math.cos(lon2)
        y = A * math.cos(lat1) * math.sin(lon1) + B * math.cos(lat2) * math.sin(lon2)
        z = A * math.sin(lat1) + B * math.sin(lat2)

        lat = math.atan2(z, math.sqrt(x ** 2 + y ** 2))
        lon = math.atan2(y, x)
        points.append([math.degrees(lat), math.degrees(lon)])

    return points

# Function to create a map
def create_map(segmen, koordinat1, koordinat2, projection="mercator"):
    fig = go.Figure()

    fig.add_trace(go.Scattergeo(
        lon=[koordinat1[1], koordinat2[1]],
        lat=[koordinat1[0], koordinat2[0]],
        mode='markers',
        marker=dict(size=12, color='red'),
        text=['Point 1', 'Point 2']
    ))

    fig.add_trace(go.Scattergeo(
        lon=[s[1] for s in segmen],
        lat=[s[0] for s in segmen],
        mode='lines',
        line=dict(width=3, color='blue'),
        name="Great Circle Path"
    ))

    fig.update_geos(
        projection_type=projection,
        showcountries=True,
        showcoastlines=True,
        showland=True,
        showocean=True,
        oceancolor="LightBlue",
        landcolor="LightGreen",
        center=dict(lat=(koordinat1[0] + koordinat2[0]) / 2, lon=(koordinat1[1] + koordinat2[1]) / 2),
        projection_scale=2  # Zoom in the map
    )

    fig.update_layout(
        title="Great Circle Map",
        height=800,  # Increase map height
        width=1200   # Increase map width
    )
    return fig

# Streamlit App
st.title("🌍 Great Circle Distance Calculator")

# Sidebar for input selection
input_method = st.sidebar.selectbox("🔽 Select Input Method", ["Location Names", "Manual Coordinates"])

# Geocoder using Geopy
geolocator = Nominatim(user_agent="GreatCircleDistanceApp")

def get_coordinates(location_name):
    location = geolocator.geocode(location_name)
    if location:
        return location.latitude, location.longitude
    else:
        st.warning(f"Could not find coordinates for {location_name}.")
        return None

# Coordinates variables
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
    jarak_haversine = haversine(koordinat1, koordinat2)
    initial_bearing, final_bearing = calculate_bearing(koordinat1, koordinat2)

    st.markdown("### **:blue[Results:]**")
    st.markdown(f"**<span style='color:teal;'>Haversine Distance:</span>** {jarak_haversine:.2f} km", unsafe_allow_html=True)
    st.markdown(f"**<span style='color:teal;'>Initial Bearing:</span>** {initial_bearing:.2f}°", unsafe_allow_html=True)
    st.markdown(f"**<span style='color:teal;'>Final Bearing:</span>** {final_bearing:.2f}°", unsafe_allow_html=True)

    segmen = interpolate_great_circle(koordinat1, koordinat2)
    projection = st.selectbox("🌐 Select Map Projection", ["mercator", "orthographic"])
    fig = create_map(segmen, koordinat1, koordinat2, projection)
    st.plotly_chart(fig, use_container_width=True)
else:
    st.warning("Please provide valid inputs to calculate coordinates.")
