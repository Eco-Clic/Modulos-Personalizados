import folium
from folium.plugins import MarkerCluster, MiniMap, Fullscreen, MeasureControl

# Coordenadas y cantidad de habitaciones de las ubicaciones

# Definición de ubicaciones agrupadas por regiones
ubicaciones = {
    "Badalona": [
        (41.4594893423169, 2.250681454063872, "Carrer del Dipòsit, 13, 08915 Badalona, Barcelona, Espanya", 3),
        (41.45018429541878, 2.2474933810516156, "Plaça de la Vila, 1, 08911 Badalona, Barcelona", 1),
        (41.44554920403716, 2.2393278098866722, "Plaça de Pep Ventura, 34, Badalona, España", 4),
        (41.44645984442209, 2.2381054540631715, "Carrer de Saragossa, 38, Badalona, España", 3),
        (41.4462327448726, 2.22505268289848, "Grup Verge de la Salut, 5, 08914 Badalona, Barcelona, España", 4),
    ],
    "Barcelona (Sagrada Familia)": [
        (41.411517560106915, 2.204531865708402, "Carrer del Marroc, Barcelona, España", 3),
        (41.406512705802655, 2.1977184963904626, "Carrer del Marroc, 1, Barcelona, España", 1),
        (41.41551284352379, 2.1872189252262313, "Avenida Meridiana, 214, Barcelona, España", 3),
    ],
    "Barcelona (Raval)": [
        (41.37717008174868, 2.1684825963889334, "Carrer de Santa Elena, 10, Barcelona, Espanya", 4),
    ],
    "Badia del Vallès": [
        (41.50941741948244, 2.1107906387253323, "Carrer de l'Algarve, 7, Badia del Vallès, Espanya", 2),
    ],
    "Barberà del Vallès": [
        (41.512818748128815, 2.1234842387255006, "Ronda de ľEst, Barberà del Vallès, España", 4),
        (41.533918626975144, 2.1146628963972094, "Carrer de Martí l'Humà, 1-9, Sabadell, España", 3),
    ],
    "Sant Cugat del Vallès": [
        (41.46951097714468, 2.079325967298701, "Carrer del Rosselló, 15 Habitación 1", 4),
    ],
    "Hospitalet de Llobregat": [
        (41.36811410325441, 2.1312363249655544, "Carrer Santa Eulàlia, 7, L'Hospitalet de Llobregat", 3),
        (41.37781383457292, 2.1160992384574717, "Carrer del Cardenal Reig, 28, L'Hospitalet de Llobregat", 3),
    ],
    "Premià de Mar": [
        (41.490503213384656, 2.3548212961360244, "Carrer Jaume Balmes, 4, Premià de Mar", 4),
    ],
    "Sabadell": [
        (41.55780832121032, 2.096908682648302, "Avenida Francesc Macià, 51, Sabadell", 4),
    ],
}

# Inicializar mapa con atribución
mapa = folium.Map(
    location=[41.4594893423169, 2.250681454063872],
    zoom_start=10,
    tiles="Stamen Terrain",
    attr='Map tiles by Stamen Design, under CC BY 3.0. Data by OpenStreetMap, under ODbL.'
)

# Añadir MiniMap
minimap = MiniMap(toggle_display=True)
mapa.add_child(minimap)

# Añadir Fullscreen plugin
fullscreen = Fullscreen()
mapa.add_child(fullscreen)

# Añadir Control de Medición
measure_control = MeasureControl(primary_length_unit='meters')
mapa.add_child(measure_control)

# Crear MarkerCluster
marker_cluster = MarkerCluster().add_to(mapa)

# Función para obtener color basado en la cantidad de habitaciones
def obtener_color(habitaciones):
    return ['blue', 'green', 'orange', 'red'][habitaciones - 1]

# Función para añadir ubicaciones a los clusters
def añadir_marcadores(ubicaciones, cluster):
    for region, puntos in ubicaciones.items():
        for lat, lon, direccion, habitaciones in puntos:
            popup_text = f"""
            <div style="font-size: 14px;">
                <b>Dirección:</b> {direccion}<br>
                <b>Habitaciones:</b> {habitaciones}<br>
                <b>Ver en Google Maps:</b> 
                <a href='https://www.google.com/maps?q={lat},{lon}' target='_blank'>Link</a>
            </div>
            """
            folium.Marker(
                [lat, lon],
                popup=popup_text,
                tooltip=direccion,
                icon=folium.Icon(color=obtener_color(habitaciones), icon="home", prefix="fa")
            ).add_to(cluster)

# Añadir los marcadores al cluster
añadir_marcadores(ubicaciones, marker_cluster)


# Añadir control de capas
folium.LayerControl().add_to(mapa)

# Guardar el mapa en un archivo HTML
mapa.save("mapa_mejorado.html")
print("Mapa guardado como mapa_mejorado.html")
