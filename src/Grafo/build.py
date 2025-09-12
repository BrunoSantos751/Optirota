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
            ways.append(el)
            for nid in el["nodes"]:
                node_usage[nid] += 1
    
    # Identificar vértices (apenas cruzamentos reais)
    vertices = set()
    for way in ways:
        for nid in way["nodes"]:
            if node_usage[nid] > 1:  # só nodes que aparecem em mais de um way
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

# --- Funções auxiliares para trabalhar com o grafo RustworkX ---

def get_node_by_original_id(G, original_id, node_id_to_index):
    """Obter dados de um nó pelo ID original"""
    if original_id in node_id_to_index:
        node_idx = node_id_to_index[original_id]
        return G[node_idx]
    return None

def get_edge_data(G, n1_original_id, n2_original_id, node_id_to_index):
    """Obter dados de uma aresta pelos IDs originais dos nós"""
    if n1_original_id in node_id_to_index and n2_original_id in node_id_to_index:
        n1_idx = node_id_to_index[n1_original_id]
        n2_idx = node_id_to_index[n2_original_id]
        
        # Encontrar a aresta
        edge_list = G.out_edges(n1_idx)
        for edge_idx in edge_list:
            if G.get_edge_endpoints_by_index(edge_idx)[1] == n2_idx:
                return G.get_edge_data_by_index(edge_idx)
    return None

def shortest_path_with_original_ids(G, start_id, end_id, node_id_to_index, index_to_node_id):
    """
    Encontra o caminho mais curto entre dois nós usando IDs originais
    Retorna: (caminho_com_ids_originais, distância_total)
    """
    if start_id not in node_id_to_index or end_id not in node_id_to_index:
        return None, float('inf')
    
    start_idx = node_id_to_index[start_id]
    end_idx = node_id_to_index[end_id]
    
    try:
        # Usar Dijkstra para encontrar o caminho mais curto
        path_indices = rx.dijkstra_shortest_path(
            G, start_idx, end_idx,
            weight_fn=lambda edge_data: edge_data['weight']
        )
        
        # Converter índices de volta para IDs originais
        path_original_ids = [index_to_node_id[idx] for idx in path_indices]
        
        # Calcular distância total
        total_distance = 0
        for i in range(len(path_indices) - 1):
            # Encontrar aresta entre nós consecutivos
            current_idx = path_indices[i]
            next_idx = path_indices[i + 1]
            
            edge_list = G.out_edges(current_idx)
            for edge_idx in edge_list:
                if G.get_edge_endpoints_by_index(edge_idx)[1] == next_idx:
                    edge_data = G.get_edge_data_by_index(edge_idx)
                    total_distance += edge_data['weight']
                    break
        
        return path_original_ids, total_distance
        
    except rx.NoPathFound:
        return None, float('inf')

def get_all_neighbors(G, original_id, node_id_to_index, index_to_node_id):
    """Obter todos os vizinhos de um nó pelo ID original"""
    if original_id not in node_id_to_index:
        return []
    
    node_idx = node_id_to_index[original_id]
    neighbor_indices = G.neighbors(node_idx)
    
    return [index_to_node_id[idx] for idx in neighbor_indices]

# --- Exemplo de uso ---
def exemplo_uso(data):
    """Exemplo de como usar a versão migrada"""
    
    # Construir o grafo
    G, nodes, vertices, ways, node_id_to_index, index_to_node_id = build_graph(data)
    
    print(f"Grafo construído com {G.num_nodes()} nós e {G.num_edges()} arestas")
    
    # Exemplo: encontrar caminho mais curto entre dois pontos
    if len(vertices) >= 2:
        vertices_list = list(vertices)
        start_id = vertices_list[0]
        end_id = vertices_list[1]
        
        path, distance = shortest_path_with_original_ids(
            G, start_id, end_id, node_id_to_index, index_to_node_id
        )
        
        if path:
            print(f"Caminho de {start_id} para {end_id}: {path}")
            print(f"Distância total: {distance:.2f} metros")
        else:
            print(f"Nenhum caminho encontrado entre {start_id} e {end_id}")
    
    # Exemplo: obter vizinhos de um nó
    if vertices:
        first_vertex = list(vertices)[0]
        neighbors = get_all_neighbors(G, first_vertex, node_id_to_index, index_to_node_id)
        print(f"Vizinhos do nó {first_vertex}: {neighbors}")
    
    return G, node_id_to_index, index_to_node_id

# --- Funções de compatibilidade para facilitar migração ---

class GraphWrapper:
    """
    Wrapper para facilitar a migração, fornecendo interface similar ao NetworkX
    """
    def __init__(self, rustworkx_graph, node_id_to_index, index_to_node_id, nodes_data):
        self.G = rustworkx_graph
        self.node_id_to_index = node_id_to_index
        self.index_to_node_id = index_to_node_id
        self.nodes_data = nodes_data
    
    def shortest_path(self, source, target, weight='weight'):
        """Interface compatível com nx.shortest_path"""
        path, _ = shortest_path_with_original_ids(
            self.G, source, target, self.node_id_to_index, self.index_to_node_id
        )
        return path if path else []
    
    def shortest_path_length(self, source, target, weight='weight'):
        """Interface compatível com nx.shortest_path_length"""
        _, distance = shortest_path_with_original_ids(
            self.G, source, target, self.node_id_to_index, self.index_to_node_id
        )
        return distance
    
    def has_edge(self, u, v):
        """Verificar se existe aresta entre dois nós"""
        if u in self.node_id_to_index and v in self.node_id_to_index:
            u_idx = self.node_id_to_index[u]
            v_idx = self.node_id_to_index[v]
            return self.G.has_edge(u_idx, v_idx)
        return False
    
    def neighbors(self, node_id):
        """Obter vizinhos de um nó"""
        return get_all_neighbors(self.G, node_id, self.node_id_to_index, self.index_to_node_id)

def build_graph_with_wrapper(data):
    """
    Versão que retorna um wrapper para facilitar a migração gradual
    """
    G, nodes, vertices, ways, node_id_to_index, index_to_node_id = build_graph(data)
    wrapper = GraphWrapper(G, node_id_to_index, index_to_node_id, nodes)
    return wrapper, nodes, vertices, ways