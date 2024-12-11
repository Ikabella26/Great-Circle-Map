import streamlit as st
import math
import plotly.graph_objects as go
from geopy.geocoders import Nominatim

# Fungsi untuk menghitung jarak menggunakan formula Haversine
def haversine(coord1, coord2):
    lat1, lon1 = coord1
    lat2, lon2 = coord2

    R = 6371  # Radius bumi dalam kilometer
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)

    a = math.sin(delta_phi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    return R * c  # Mengembalikan jarak dalam km

# Fungsi untuk mendapatkan koordinat berdasarkan nama lokasi menggunakan Geopy
geolocator = Nominatim(user_agent="GreatCircleDistanceApp")

def get_coordinates(location_name):
    location = geolocator.geocode(location_name)
    if location:
        return location.latitude, location.longitude
    else:
        st.warning(f"Could not find coordinates for {location_name}.")
        return None

# Fungsi untuk membuat peta
def create_map(segmen, koordinat1, koordinat2, projection="mercator", land_color="#D1E7E1", ocean_color="#A4D8E5"):
    fig = go.Figure()

    # Plot titik lokasi
    fig.add_trace(go.Scattergeo(
        lon=[koordinat1[1], koordinat2[1]],
        lat=[koordinat1[0], koordinat2[0]],
        mode='markers',
        marker=dict(size=12, color='red'),
        text=['Point 1', 'Point 2']
    ))

    # Plot jalur Great Circle
    fig.add_trace(go.Scattergeo(
        lon=[s[1] for s in segmen],
        lat=[s[0] for s in segmen],
        mode='lines',
        line=dict(width=3, color='blue'),
        name="Great Circle Path"
    ))

    # Update pengaturan geos untuk warna dasar peta
    fig.update_geos(
        projection_type=projection,
        showcountries=True,
        showcoastlines=True,
        showland=True,
        showocean=True,
        oceancolor=ocean_color,  # Warna laut
        landcolor=land_color,    # Warna tanah
        center=dict(lat=(koordinat1[0] + koordinat2[0]) / 2, lon=(koordinat1[1] + koordinat2[1]) / 2),
        projection_scale=2  # Zoom peta
    )

    # Update layout
    fig.update_layout(
        title="Great Circle Map",
        height=800,  # Ukuran peta
        width=1200   # Ukuran peta
    )
    return fig

# Streamlit App
st.set_page_config(page_title="Great Circle Distance Calculator", page_icon="🌍", layout="wide")
st.title("🌍 Great Circle Distance Calculator")

# Pilihan input pengguna
input_method = st.sidebar.selectbox("🔽 Select Input Method", ["Location Names", "Manual Coordinates"])

# Koordinat lokasi
koordinat1 = None
koordinat2 = None

# Menggunakan input lokasi nama atau koordinat manual
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

# Pilihan warna basemap
ocean_color = st.sidebar.color_picker('Pick an Ocean Color', '#A4D8E5')  # Default light blue
land_color = st.sidebar.color_picker('Pick a Land Color', '#D1E7E1')    # Default light green

# Menampilkan hasil jika kedua koordinat valid
if koordinat1 and koordinat2:
    jarak_haversine = haversine(koordinat1, koordinat2)
    segmen = interpolate_great_circle(koordinat1, koordinat2)

    st.markdown("### **:blue[Results:]**")
    st.markdown(f"**Haversine Distance:** {jarak_haversine:.2f} km")
    
    projection = st.selectbox("🌐 Select Map Projection", ["mercator", "orthographic"])
    fig = create_map(segmen, koordinat1, koordinat2, projection, land_color, ocean_color)
    
    st.plotly_chart(fig, use_container_width=True)
else:
    st.warning("Please provide valid inputs to calculate coordinates.")
