from src.OSM.consultaOSM import get_osm_data, print_crossings
from src.Grafo.build import build_graph
from src.Grafo.visualizar import plot_graph_with_names


# Exemplo: bounding box pequena em Ponta Verde, Maceió  
bbox = (-9.659998, -35.708648, -9.657515, -35.704620) #Sul/Oeste/Norte/leste (Baixo/esquerda/Cima)

data = get_osm_data(bbox)
G, nodes, vertices, ways = build_graph(data)

print(f"Total de vértices (cruzamentos reais): {len(vertices)}")
print(f"Total de arestas: {G.number_of_edges()}")

# Mostrar os cruzamentos de forma segura
print_crossings(G, nodes, vertices, ways, limit=20)  # limita a 20 cruzamentos para teste
plot_graph_with_names(G,nodes,ways)