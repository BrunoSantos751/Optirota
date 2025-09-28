import os
import colorsys
import math
import numpy as np
import folium
from src.OSM.consultaOSM import get_node_street_name

def _generate_distinct_colors(n):
    """Gera n cores visualmente distintas."""
    if n == 0: return []
    colors = []
    for i in range(n):
        hue = i / n
        lightness = 0.5 + (0.1 * (i % 2))
        saturation = 0.9
        r, g, b = colorsys.hls_to_rgb(hue, lightness, saturation)
        colors.append('#%02x%02x%02x' % (int(r*255), int(g*255), int(b*255)))
    return colors

def _create_circle_shape(center_lat, center_lon, radius_km):
    """Gera pontos (lats, lons) para formar um círculo em um mapa."""
    R = 6371; d = radius_km / R
    center_lat_rad = math.radians(center_lat); center_lon_rad = math.radians(center_lon)
    lats, lons = [], []
    for angle in np.linspace(0, 2 * math.pi, 100):
        lat_rad = math.asin(math.sin(center_lat_rad) * math.cos(d) + math.cos(center_lat_rad) * math.sin(d) * math.cos(angle))
        lon_rad = center_lon_rad + math.atan2(math.sin(angle) * math.sin(d) * math.cos(center_lat_rad), math.cos(d) - math.sin(center_lat_rad) * math.sin(lat_rad))
        lats.append(math.degrees(lat_rad)); lons.append(math.degrees(lon_rad))
    return lats, lons

def plot_graph_with_names(G, nodes, ways, node_id_to_index, index_to_node_id, depot_id=None, service_radius_km=None):
    print("Gerando visualização do grafo com Folium...")
    if not nodes:
        print("Não há nós para plotar."); return

    lats = [n[0] for n in nodes.values()]; lons = [n[1] for n in nodes.values()]
    center_lat = sum(lats) / len(lats); center_lon = sum(lons) / len(lons)

    mapa = folium.Map(location=[center_lat, center_lon], zoom_start=14, tiles="cartodbpositron", control_scale=True)

    if service_radius_km and depot_id and depot_id in nodes:
        depot_lat, depot_lon = nodes[depot_id]
        folium.Circle(
            location=[depot_lat, depot_lon], radius=service_radius_km * 1000, color='blue', 
            fill=True, fill_color='blue', fill_opacity=0.1, popup=f"Raio de serviço: {service_radius_km} km"
        ).add_to(mapa)

    edges_group = folium.FeatureGroup(name="Ruas")
    for edge_idx in G.edge_indices():
        source_idx, target_idx = G.get_edge_endpoints_by_index(edge_idx)
        source_id, target_id = index_to_node_id[source_idx], index_to_node_id[target_idx]
        points = [nodes[source_id], nodes[target_id]]
        folium.PolyLine(locations=points, color='grey', weight=2, opacity=0.8).add_to(edges_group)
    edges_group.add_to(mapa)
    
    nodes_group = folium.FeatureGroup(name="Cruzamentos")
    for node_idx in G.node_indices():
        node_id = index_to_node_id[node_idx]; lat, lon = nodes[node_id]
        popup_text = f"<b>Nó:</b> {node_id}<br><b>Rua:</b> {get_node_street_name(node_id, ways)}"
        if node_id == depot_id:
            folium.Marker(location=[lat, lon], popup=f"<b>DEPÓSITO:</b> {node_id}", icon=folium.Icon(color='red', icon='star')).add_to(mapa)
        else:
            folium.CircleMarker(location=[lat, lon], radius=4, color='blue', fill=True, fill_color='blue', popup=popup_text).add_to(nodes_group)
    nodes_group.add_to(mapa)

    folium.LayerControl().add_to(mapa)
    file_path = "street_map.html"; mapa.save(file_path)
    print(f"\nO gráfico interativo foi salvo em: {os.path.abspath(file_path)}")

def plot_path_only(path, nodes, ways):
    print("Gerando visualização do menor caminho com Folium...")
    if not path or not path[0] in nodes:
        print("Caminho inválido ou nó inicial não encontrado."); return

    mapa = folium.Map(location=nodes[path[0]], zoom_start=16, tiles="cartodbpositron", control_scale=True)

    path_points = [nodes[node_id] for node_id in path if node_id in nodes]
    folium.PolyLine(locations=path_points, color='blue', weight=5).add_to(mapa)

    for i, node_id in enumerate(path):
        if node_id in nodes:
            lat, lon = nodes[node_id]; popup_text = f"<b>Nó:</b> {node_id}<br><b>Rua:</b> {get_node_street_name(node_id, ways)}"
            if i == 0:
                folium.Marker(location=[lat, lon], popup=f"<b>INÍCIO:</b><br>{popup_text}", icon=folium.Icon(color='green', icon='play')).add_to(mapa)
            elif i == len(path) - 1:
                folium.Marker(location=[lat, lon], popup=f"<b>FIM:</b><br>{popup_text}", icon=folium.Icon(color='red', icon='stop')).add_to(mapa)
            else:
                folium.CircleMarker(location=[lat, lon], radius=4, color='blue', fill=True, popup=popup_text).add_to(mapa)
    
    file_path = "path_map.html"; mapa.save(file_path)
    print(f"\nO mapa do menor caminho foi salvo em: {os.path.abspath(file_path)}")

def plot_vrp_routes(routes, depot_id, nodes, ways, distance_matrix, service_radius_km=None):
    
    print("Gerando visualização das rotas VRP com Folium...")
    if not routes or not depot_id in nodes:
        print("Dados de rota inválidos ou depósito não encontrado."); return

    mapa = folium.Map(location=nodes[depot_id], zoom_start=14, tiles="cartodbpositron", control_scale=True)

    if service_radius_km:
        folium.Circle(location=nodes[depot_id], radius=service_radius_km * 1000, color='#3186cc', fill=True, fill_color='#3186cc', fill_opacity=0.1, popup=f"Raio de serviço: {service_radius_km} km").add_to(mapa)

    total_segments = sum(len(data['route']) - 1 for data in routes.values() if data.get('route'))
    segment_colors = _generate_distinct_colors(total_segments)
    color_index = 0
    
    for vehicle_id, data in sorted(routes.items()):
        route_stops = data['route']
        if not route_stops: continue
        
        # Loop através de cada trecho para criar uma camada individual na legenda
        for j in range(len(route_stops) - 1):
            source_stop, target_stop = route_stops[j], route_stops[j+1]
            _, _, segment_path = distance_matrix.get((source_stop, target_stop), (0, 0, []))
            
            if segment_path and color_index < len(segment_colors):
                path_points = [nodes[node_id] for node_id in segment_path if node_id in nodes]
                
                # Cria um nome descritivo para cada trecho na legenda
                trace_name = f"{vehicle_id}: {j+1} ({target_stop})"
                if target_stop == depot_id:
                    trace_name = f"{vehicle_id}: Retorno"

                # Cria um grupo de camadas para cada trecho individualmente
                segment_group = folium.FeatureGroup(name=trace_name)
                
                folium.PolyLine(
                    locations=path_points, 
                    color=segment_colors[color_index], 
                    weight=5, 
                    opacity=0.8
                ).add_to(segment_group)
                
                color_index += 1
                segment_group.add_to(mapa)

    # Marcadores de clientes e depósito (permanecem visíveis)
    folium.Marker(location=nodes[depot_id], popup=f"<b>DEPÓSITO: {depot_id}</b>", icon=folium.Icon(color='blue', icon='star')).add_to(mapa)
    all_customer_ids = {c_id for data in routes.values() for c_id in data['route'] if c_id != depot_id}
    for cust_id in all_customer_ids:
        if cust_id in nodes:
            folium.CircleMarker(location=nodes[cust_id], radius=6, color='black', fill=True, fill_color='white', fill_opacity=1, popup=f"<b>Cliente:</b> {cust_id}<br><b>Rua:</b> {get_node_street_name(cust_id, ways)}").add_to(mapa)

    folium.LayerControl().add_to(mapa)
    
    file_path = "vrp_routes_map.html"
    mapa.save(file_path)
    print(f"\nO mapa com as rotas VRP foi salvo em: {os.path.abspath(file_path)}")