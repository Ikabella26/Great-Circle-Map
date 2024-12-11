import streamlit as st
import plotly.graph_objects as go
from math import radians, degrees, sin, cos, atan2, sqrt

# Fungsi untuk menghitung koordinat lintasan lingkaran besar
def great_circle(lat1, lon1, lat2, lon2, num_points=100):
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])

    d_lon = lon2 - lon1
    d_lat = lat2 - lat1

    a = sin(d_lat / 2)**2 + cos(lat1) * cos(lat2) * sin(d_lon / 2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))

    distance = 6371 * c  # Jarak dalam kilometer

    coords = []
    for i in range(num_points + 1):
        f = i / num_points
        A = sin((1 - f) * c) / sin(c)
        B = sin(f * c) / sin(c)
        x = A * cos(lat1) * cos(lon1) + B * cos(lat2) * cos(lon2)
        y = A * cos(lat1) * sin(lon1) + B * cos(lat2) * sin(lon2)
        z = A * sin(lat1) + B * sin(lat2)

        lat = atan2(z, sqrt(x**2 + y**2))
        lon = atan2(y, x)

        coords.append((degrees(lat), degrees(lon)))

    return coords, distance

# Judul aplikasi
st.title("Interactive Great Circle Map")

# Input interaktif
st.sidebar.header("Input Coordinates")
lat1 = st.sidebar.number_input("Starting Latitude (-90 to 90):", min_value=-90.0, max_value=90.0, value=0.0)
lon1 = st.sidebar.number_input("Starting Longitude (-180 to 180):", min_value=-180.0, max_value=180.0, value=0.0)
lat2 = st.sidebar.number_input("Ending Latitude (-90 to 90):", min_value=-90.0, max_value=90.0, value=45.0)
lon2 = st.sidebar.number_input("Ending Longitude (-180 to 180):", min_value=-180.0, max_value=180.0, value=45.0)

# Hitung lintasan lingkaran besar
coords, distance = great_circle(lat1, lon1, lat2, lon2)

# Tampilkan peta
fig = go.Figure()

# Tambahkan garis lintasan
lats, lons = zip(*coords)
fig.add_trace(go.Scattergeo(
    lon=lons,
    lat=lats,
    mode='lines',
    line=dict(width=2, color='blue'),
    name=f'Great Circle ({distance:.2f} km)'
))

# Tambahkan titik awal dan akhir
fig.add_trace(go.Scattergeo(
    lon=[lon1, lon2],
    lat=[lat1, lat2],
    mode='markers+text',
    marker=dict(size=8, color=['red', 'green']),
    text=['Start', 'End'],
    textposition='top center'
))

# Sesuaikan tampilan peta
fig.update_layout(
    title_text=f"Great Circle Path from ({lat1}, {lon1}) to ({lat2}, {lon2})", 
    title_x=0.5,
    geo=dict(
        projection_type='equirectangular',
        showland=True,
        landcolor='lightgray',
        countrycolor='gray',
    ),
    margin=dict(l=0, r=0, t=30, b=0)
)

# Tampilkan peta
st.plotly_chart(fig)

# Tampilkan informasi tambahan
st.sidebar.subheader("Details")
st.sidebar.markdown(f"**Starting Point:** {lat1}°N, {lon1}°E")
st.sidebar.markdown(f"**Ending Point:** {lat2}°N, {lon2}°E")
st.sidebar.markdown(f"**Distance:** {distance:.2f} km")

st.markdown(
    """### How it Works
    - **Great Circle Path**: The shortest path between two points on a sphere.
    - **Interactive Inputs**: Use the sidebar to change the coordinates.
    - **Visualization**: The map updates dynamically to reflect the inputs.
    """)
