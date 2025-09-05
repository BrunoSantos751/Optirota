import math
import networkx as nx
from collections import defaultdict

# --- Função para calcular distância Haversine ---
def haversine(lat1, lon1, lat2, lon2):
    R = 6371000  # raio da Terra em metros
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi/2)**2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda/2)**2
    return 2 * R * math.atan2(math.sqrt(a), math.sqrt(1 - a))

# --- Função para construir o grafo ---
def build_graph(data):
    G = nx.DiGraph()
    nodes = {}
    node_usage = defaultdict(int)
    ways = []

    # Separar nodes e ways
    for el in data["elements"]:
        if el["type"] == "node":
            nodes[el["id"]] = (el["lat"], el["lon"])
        elif el["type"] == "way" and "highway" in el.get("tags", {}):
            ways.append(el)
            for nid in el["nodes"]:
                node_usage[nid] += 1

    # Identificar vértices (apenas cruzamentos reais)
    vertices = set()
    for way in ways:
        for nid in way["nodes"]:
            if node_usage[nid] > 1:  # só nodes que aparecem em mais de um way
                vertices.add(nid)

    # Criar arestas (segmentos entre vértices)
    for way in ways:
        node_ids = way["nodes"]
        oneway = way["tags"].get("oneway", "no").lower()
        street_name = way.get("tags", {}).get("name", "rua sem nome")
        path = []

        for nid in node_ids:
            path.append(nid)
            if nid in vertices:
                if len(path) > 1:
                    # calcular distância acumulada
                    dist = 0
                    for i in range(len(path)-1):
                        lat1, lon1 = nodes[path[i]]
                        lat2, lon2 = nodes[path[i+1]]
                        dist += haversine(lat1, lon1, lat2, lon2)

                    n1, n2 = path[0], path[-1]

                    # --- Tratamento de mão ---
                    if oneway in ["yes", "true", "1"]:
                        G.add_edge(n1, n2, weight=dist, street=street_name)
                    elif oneway == "-1":
                        G.add_edge(n2, n1, weight=dist, street=street_name)
                    else:  # assume mão dupla
                        G.add_edge(n1, n2, weight=dist, street=street_name)
                        G.add_edge(n2, n1, weight=dist, street=street_name)

                # reinicia caminho a partir do cruzamento
                path = [nid]

    return G, nodes, vertices, ways
