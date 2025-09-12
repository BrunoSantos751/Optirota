import math
import rustworkx as rx
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
    G = rx.PyDiGraph()  # Grafo direcionado (equivalente ao nx.DiGraph)
    nodes = {}
    node_usage = defaultdict(int)
    ways = []
    
    # Mapeamentos entre IDs originais e índices do RustworkX
    node_id_to_index = {}  # ID original -> índice no grafo
    index_to_node_id = {}  # índice no grafo -> ID original
    
    # Separar nodes e ways
    for el in data["elements"]:
        if el["type"] == "node":
            nodes[el["id"]] = (el["lat"], el["lon"])
        elif el["type"] == "way" and "highway" in el.get("tags", {}):
            # Adicionar filtro para ruas com nome
            if "name" in el["tags"]:
                ways.append(el)
                for nid in el["nodes"]:
                    node_usage[nid] += 1
    
    # Identificar vértices (cruzamentos e extremidades de ruas com nome)
    vertices = set()
    for way in ways:
        node_ids = way["nodes"]
        # Adicionar o primeiro e o último nó do 'way' como vértices
        if len(node_ids) > 1:
            vertices.add(node_ids[0])
            vertices.add(node_ids[-1])
        
        # Adicionar nós que são cruzamentos (têm mais de uma aresta)
        for nid in node_ids:
            if node_usage[nid] > 1:
                vertices.add(nid)
    
    # Adicionar todos os vértices ao grafo RustworkX
    for vertex_id in vertices:
        if vertex_id in nodes:
            lat, lon = nodes[vertex_id]
            # Adicionar nó com dados originais
            node_data = {
                'original_id': vertex_id,
                'lat': lat,
                'lon': lon
            }
            node_index = G.add_node(node_data)
            node_id_to_index[vertex_id] = node_index
            index_to_node_id[node_index] = vertex_id
    
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
                    
                    # Verificar se ambos os nós existem no grafo
                    if n1 in node_id_to_index and n2 in node_id_to_index:
                        n1_idx = node_id_to_index[n1]
                        n2_idx = node_id_to_index[n2]
                        
                        # Dados da aresta
                        edge_data = {
                            'weight': dist,
                            'street': street_name
                        }
                        
                        # --- Tratamento de mão ---
                        if oneway in ["yes", "true", "1"]:
                            G.add_edge(n1_idx, n2_idx, edge_data)
                        elif oneway == "-1":
                            G.add_edge(n2_idx, n1_idx, edge_data)
                        else:  # assume mão dupla
                            G.add_edge(n1_idx, n2_idx, edge_data)
                            G.add_edge(n2_idx, n1_idx, edge_data)
                
                # reinicia caminho a partir do cruzamento
                path = [nid]
    
    # Retornar também os mapeamentos para facilitar uso posterior
    return G, nodes, vertices, ways, node_id_to_index, index_to_node_id
