import networkx as nx
import matplotlib.pyplot as plt
from src.OSM.consultaOSM import get_node_street_name

#Desenha o grafo com nomes das ruas principais nos cruzamentos e nas arestas.
def plot_graph_with_names(G, nodes, ways):

    plt.figure(figsize=(14, 14))

    # Coordenadas dos nodes
    pos = {nid: (lon, lat) for nid, (lat, lon) in nodes.items() if nid in G.nodes}

    # Desenhar nodes
    nx.draw_networkx_nodes(G, pos, node_size=70, node_color='red', alpha=0.8)

    # Desenhar arestas
    nx.draw_networkx_edges(G, pos, arrowstyle='-|>', arrowsize=15, edge_color='gray', alpha=0.5)

    # Labels dos nodes (nome do cruzamento: principal rua que passa por ele)
    node_labels = {nid: get_node_street_name(nid, ways) for nid in G.nodes()}
    nx.draw_networkx_labels(G, pos, labels=node_labels, font_size=8, font_color='blue')

    # Labels das arestas (nome da rua)
    edge_labels = {(u, v): d['street'] for u, v, d in G.edges(data=True)}
    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_size=6, alpha=0.7)

    plt.title("Grafo de cruzamentos e ruas com nomes", fontsize=16)
    plt.axis('off')
    plt.show()
