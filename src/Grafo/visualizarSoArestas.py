import plotly.graph_objects as go
import rustworkx as rx
import os

def plot_graph_with_names_optimized(G, nodes, ways, node_id_to_index, index_to_node_id):
    print("Gerando visualização do grafo em formato de mapa com Plotly...")

    # Listas para as arestas
    edge_x = []
    edge_y = []
    
    # Lista para as anotações (setas de direção)
    annotations = []

    min_lat, max_lat = float('inf'), float('-inf')
    min_lon, max_lon = float('inf'), float('-inf')

    # Iterar sobre as arestas para coletar dados
    for edge_idx in G.edge_indices():
        source_idx, target_idx = G.get_edge_endpoints_by_index(edge_idx)

        source_id = index_to_node_id[source_idx]
        target_id = index_to_node_id[target_idx]

        source_lat, source_lon = nodes[source_id]
        target_lat, target_lon = nodes[target_id]
        
        # Atualizar a bounding box
        min_lat = min(min_lat, source_lat, target_lat)
        max_lat = max(max_lat, source_lat, target_lat)
        min_lon = min(min_lon, source_lon, target_lon)
        max_lon = max(max_lon, source_lon, target_lon)

        edge_x.extend([source_lon, target_lon, None])
        edge_y.extend([source_lat, target_lat, None])

        # Adicionar anotações para as setas de direção
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

    # Criar o traço para as arestas (as ruas)
    edge_trace = go.Scattermapbox(
        lon=edge_x, lat=edge_y,
        mode='lines',
        line=dict(width=1.5, color='red'),
        hoverinfo='none',
        name="Ruas"
    )

    # Calcular o centro da bounding box
    center_lon = (min_lon + max_lon) / 2
    center_lat = (min_lat + max_lat) / 2
    
    # Criar a figura com os traços e layout de mapa
    fig = go.Figure(data=[edge_trace], # Removido o traço dos nós aqui
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
    
    # Salvar a figura em um arquivo HTML
    file_path = "street_map.html"
    fig.write_html(file_path)
    
    print(f"\nO gráfico interativo em formato de mapa foi salvo em: {os.path.abspath(file_path)}")