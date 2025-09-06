from src.OSM.consultaOSM import get_osm_data, print_crossings
from src.Grafo.build import build_graph
from src.Grafo.visualizar import plot_graph_with_names

# --- Defina um bounding box de teste (exemplo: centro de Maceió) ---
# formato: [lat_min, lon_min, lat_max, lon_max]
bbox = [-9.67, -35.74, -9.65, -35.72]

def testar_grafo():
    print("\n=== Teste Grafo OSM ===")
    print("Baixando dados OSM...")
    data = get_osm_data(bbox)

    print("Construindo grafo...")
    G, nodes, vertices, ways = build_graph(data)

    print(f"Nós totais: {len(nodes)}")
    print(f"Cruzamentos (vértices): {len(vertices)}")
    print(f"Arestas no grafo: {G.number_of_edges()}")

    # Mostrar alguns cruzamentos
    print_crossings(G, nodes, vertices, ways, limit=3)

    # Desenhar grafo
    print("Exibindo grafo...")
    plot_graph_with_names(G, nodes, ways)

if __name__ == "__main__":
    testar_grafo()
