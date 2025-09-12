import plotly.graph_objects as go
import rustworkx as rx
from src.OSM.consultaOSM import get_node_street_name

def plot_graph_with_names(G, nodes, ways, node_id_to_index, index_to_node_id):
    """
    Plota o grafo usando a biblioteca Plotly, gerando um arquivo HTML interativo
    com nomes de ruas e direções.
    """
    print("Gerando visualização interativa do grafo com Plotly...")

    # Listas para as arestas (linhas do grafo)
    edge_x = []
    edge_y = []
    
    # Listas para os nós
    node_x = []
    node_y = []
    node_text = []

    # Listas para os rótulos de texto das arestas
    edge_label_x = []
    edge_label_y = []
    edge_label_text = []

    # Lista para as anotações (setas de direção)
    annotations = []

    # Iterar sobre as arestas do grafo RustworkX
    for edge_idx in G.edge_indices():
        source_idx, target_idx = G.get_edge_endpoints_by_index(edge_idx)
        edge_data = G.get_edge_data_by_index(edge_idx)

        source_id = index_to_node_id[source_idx]
        target_id = index_to_node_id[target_idx]

        source_lat, source_lon = nodes[source_id]
        target_lat, target_lon = nodes[target_id]

        # Adicionar as coordenadas das arestas (para o trace de linhas)
        edge_x.extend([source_lon, target_lon, None])
        edge_y.extend([source_lat, target_lat, None])

        # Adicionar informações para os rótulos e setas
        street_name = edge_data.get('street', 'rua sem nome')
        
        # Calcular o ponto médio da aresta para o rótulo
        mid_lon = (source_lon + target_lon) / 2
        mid_lat = (source_lat + target_lat) / 2
        
        edge_label_x.append(mid_lon)
        edge_label_y.append(mid_lat)
        edge_label_text.append(street_name)

        # Adicionar anotação para a seta de direção
        annotations.append(
            go.layout.Annotation(
                x=target_lon, y=target_lat,
                ax=source_lon, ay=source_lat,
                xref='x', yref='y',
                axref='x', ayref='y',
                showarrow=True,
                arrowhead=5,
                arrowsize=1.5,
                arrowwidth=1,
                arrowcolor='#888',
                standoff=2,
                opacity=0.5
            )
        )

    # Iterar sobre os nós para obter as coordenadas e informações
    for node_id, (lat, lon) in nodes.items():
        node_x.append(lon)
        node_y.append(lat)
        
        street_name = get_node_street_name(node_id, ways)
        node_text.append(f"<b>Nó:</b> {node_id}<br><b>Rua:</b> {street_name}")

    # Criar o traço para as arestas (as linhas do grafo)
    edge_trace = go.Scatter(
        x=edge_x, y=edge_y,
        mode='lines',
        line=dict(width=0.5, color='#888'),
        hoverinfo='none',
        name="Arestas"
    )

    # Criar o traço para os rótulos de texto das arestas
    edge_label_trace = go.Scatter(
        x=edge_label_x, y=edge_label_y,
        mode='text',
        text=edge_label_text,
        textfont=dict(
            size=8,
            color='black'
        ),
        hoverinfo='text',
        hovertext=edge_label_text,
        name="Nomes das Ruas"
    )

    # Criar o traço para os nós
    node_trace = go.Scatter(
        x=node_x, y=node_y,
        mode='markers',
        hoverinfo='text',
        text=node_text,
        marker=dict(
            showscale=False,
            colorscale='YlGnBu',
            reversescale=True,
            color=[],
            size=10,
            colorbar=dict(
                thickness=15,
                title='Conexões de Nós',
                xanchor='left'
            ),
            line=dict(width=2)
        ),
        name="Nós"
    )

    # Aumentar o tamanho do marcador para os cruzamentos
    node_adjacencies = []
    for node_idx in G.node_indices():
        adjacencies = len(G.neighbors(node_idx))
        node_adjacencies.append(adjacencies)
    
    node_trace.marker.color = node_adjacencies
    node_trace.marker.size = [5 + (adj * 2) for adj in node_adjacencies]

    # Criar a figura com todos os traços e layout
    fig = go.Figure(data=[edge_trace, edge_label_trace, node_trace],
                    layout=go.Layout(
                        title=go.layout.Title(text='<br>Grafo de Ruas', x=0.5),
                        showlegend=False,
                        hovermode='closest',
                        margin=dict(b=20, l=5, r=5, t=40),
                        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                        annotations=annotations + [dict(
                            text="Fonte: OpenStreetMap",
                            showarrow=False,
                            xref="paper", yref="paper",
                            x=0.005, y=-0.002
                        )]
                    )
                   )
    
    # Salvar a figura em um arquivo HTML
    file_path = "street_graph.html"
    fig.write_html(file_path)
    
    print(f"\nO gráfico interativo foi salvo em: {file_path}")