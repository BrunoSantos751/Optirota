import plotly.graph_objects as go
import rustworkx as rx
import os
from src.OSM.consultaOSM import get_node_street_name

def plot_graph_with_names(G, nodes, ways, node_id_to_index, index_to_node_id):
    print("Gerando visualização do grafo em formato de mapa com Plotly...")

    edge_x = []
    edge_y = []
    
    node_x = []
    node_y = []
    node_text = []
    node_adjacencies = []
    # Lista para as anotações (setas de direção)
    annotations = []

    crossing_node_indices = set()
    
    min_lat, max_lat = float('inf'), float('-inf')
    min_lon, max_lon = float('inf'), float('-inf')

    for edge_idx in G.edge_indices():
        source_idx, target_idx = G.get_edge_endpoints_by_index(edge_idx)
        edge_data = G.get_edge_data_by_index(edge_idx)

        crossing_node_indices.add(source_idx)
        crossing_node_indices.add(target_idx)

        source_id = index_to_node_id[source_idx]
        target_id = index_to_node_id[target_idx]

        source_lat, source_lon = nodes[source_id]
        target_lat, target_lon = nodes[target_id]
        
        min_lat = min(min_lat, source_lat, target_lat)
        max_lat = max(max_lat, source_lat, target_lat)
        min_lon = min(min_lon, source_lon, target_lon)
        max_lon = max(max_lon, source_lon, target_lon)

        edge_x.extend([source_lon, target_lon, None])
        edge_y.extend([source_lat, target_lat, None])

        annotations.append(
            go.layout.Annotation(
                x=target_lon, y=target_lat,
                ax=source_lon, ay=source_lat,
                showarrow=True,
                arrowhead=5,
                arrowsize=1.5,
                arrowwidth=1,
                arrowcolor='blue',
                standoff=2,
                opacity=0.5
            )
        )

    for node_idx in crossing_node_indices:
        node_id = index_to_node_id[node_idx]
        lat, lon = nodes[node_id]
        
        node_x.append(lon)
        node_y.append(lat)
        
        street_name = get_node_street_name(node_id, ways)
        node_text.append(f"<b>Nó:</b> {node_id}<br><b>Rua:</b> {street_name}")

        adjacencies = len(G.neighbors(node_idx))
        node_adjacencies.append(adjacencies)

    edge_trace = go.Scattermapbox(
        lon=edge_x, lat=edge_y,
        mode='lines',
        line=dict(width=1.5, color='red'),
        hoverinfo='none',
        name="Ruas"
    )

    node_trace = go.Scattermapbox(
        lon=node_x, lat=node_y,
        mode='markers',
        hoverinfo='text',
        text=node_text,
        name="Cruzamentos",
        marker=go.scattermapbox.Marker(
            size=[5 + (adj * 2) for adj in node_adjacencies],
            color='blue',
            symbol='circle',
        )
    )

    center_lon = (min_lon + max_lon) / 2
    center_lat = (min_lat + max_lat) / 2
    
    fig = go.Figure(data=[edge_trace, node_trace],
                    layout=go.Layout(
                        title=go.layout.Title(text='<br>Grafo de Ruas - Visualização de Mapa', x=0.5),
                        showlegend=False,
                        hovermode='closest',
                        margin={"r":0,"t":0,"l":0,"b":0},
                        mapbox_style="open-street-map",
                        mapbox_zoom=14,
                        mapbox_center={"lat": center_lat, "lon": center_lon},
                        annotations=annotations
                    )
                   )
    
    file_path = "street_map.html"
    fig.write_html(file_path)
    
    print(f"\nO gráfico interativo em formato de mapa foi salvo em: {os.path.abspath(file_path)}")


import plotly.graph_objects as go
import os
from src.OSM.consultaOSM import get_node_street_name

def plot_path_only(path, nodes, ways):
    print("Gerando visualização do menor caminho em um novo mapa...")
    
    path_edge_x = []
    path_edge_y = []
    
    path_node_x = []
    path_node_y = []
    path_node_text = []
    path_node_colors = []
    path_node_sizes = []
    
    annotations = []

    min_lat, max_lat = float('inf'), float('-inf')
    min_lon, max_lon = float('inf'), float('-inf')

    for i in range(len(path) - 1):
        source_id = path[i]
        target_id = path[i + 1]

        if source_id not in nodes or target_id not in nodes:
            print(f"Aviso: Nó {source_id} ou {target_id} não encontrado nas coordenadas.")
            continue
            
        source_lat, source_lon = nodes[source_id]
        target_lat, target_lon = nodes[target_id]

        path_edge_x.extend([source_lon, target_lon, None])
        path_edge_y.extend([source_lat, target_lat, None])

        min_lat = min(min_lat, source_lat, target_lat)
        max_lat = max(max_lat, source_lat, target_lat)
        min_lon = min(min_lon, source_lon, target_lon)
        max_lon = max(max_lon, source_lon, target_lon)
        
        annotations.append(
            go.layout.Annotation(
                x=target_lon, y=target_lat,
                ax=source_lon, ay=source_lat,
                showarrow=True,
                arrowhead=5,
                arrowsize=2,
                arrowwidth=2,
                arrowcolor='red',
                standoff=3
            )
        )
    
    for i, node_id in enumerate(path):
        if node_id in nodes:
            lat, lon = nodes[node_id]
            street_name = get_node_street_name(node_id, ways)
            
            path_node_x.append(lon)
            path_node_y.append(lat)
            path_node_text.append(f"<b>Nó:</b> {node_id}<br><b>Rua:</b> {street_name}")

            if i == 0:
                path_node_colors.append('green')
                path_node_sizes.append(20)
                path_node_text[-1] = f"<b>Nó Inicial:</b> {node_id}<br><b>Rua:</b> {street_name}"
            elif i == len(path) - 1:
                path_node_colors.append('pink')
                path_node_sizes.append(20)
                path_node_text[-1] = f"<b>Nó Final:</b> {node_id}<br><b>Rua:</b> {street_name}"
            else:
                path_node_colors.append('blue')
                path_node_sizes.append(10)

    path_edge_trace = go.Scattermapbox(
        lon=path_edge_x, lat=path_edge_y,
        mode='lines',
        line=dict(width=5, color='red'),
        hoverinfo='none',
        name="Caminho"
    )
    
    path_node_trace = go.Scattermapbox(
        lon=path_node_x, lat=path_node_y,
        mode='markers',
        hoverinfo='text',
        text=path_node_text,
        name="Nós do Caminho",
        marker=go.scattermapbox.Marker(
            size=path_node_sizes,
            color=path_node_colors,
            symbol='circle'
        )
    )

    center_lon = (min_lon + max_lon) / 2
    center_lat = (min_lat + max_lat) / 2
    
    fig = go.Figure(data=[path_edge_trace, path_node_trace],
                    layout=go.Layout(
                        showlegend=False,
                        hovermode='closest',
                        margin={"r":0,"t":0,"l":0,"b":0},
                        mapbox_style="open-street-map",
                        mapbox_zoom=16,
                        mapbox_center={"lat": center_lat, "lon": center_lon},
                        annotations=annotations
                    )
                   )
    
    file_path = "street_map.html"
    fig.write_html(file_path)
    
    print(f"\nO gráfico do menor caminho foi salvo em: {os.path.abspath(file_path)}")