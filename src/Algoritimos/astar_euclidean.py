import heapq
import math

def euclidean_heuristic(lat1, lon1, lat2, lon2):
    return math.sqrt((lat1 - lat2)**2 + (lon1 - lon2)**2)

def astar(G, start_id, end_id, nodes, node_id_to_index, index_to_node_id):
    if start_id not in node_id_to_index or end_id not in node_id_to_index:
        return None, float('inf'), 0
    
    start_idx = node_id_to_index[start_id]
    end_idx = node_id_to_index[end_id]
    
    end_lat, end_lon = nodes[end_id]
    
    g_score = {node: float('inf') for node in G.node_indices()}
    g_score[start_idx] = 0
    
    start_lat, start_lon = nodes[start_id]
    f_start = euclidean_heuristic(start_lat, start_lon, end_lat, end_lon)
    
    open_set = [(f_start, start_idx)]
    predecessores = {node: None for node in G.node_indices()}
    nos_explorados = 0
    
    while open_set:
        current_f, current_idx = heapq.heappop(open_set)
        nos_explorados += 1
        
        if current_idx == end_idx:
            caminho = []
            while current_idx is not None:
                caminho.append(index_to_node_id[current_idx])
                current_idx = predecessores[current_idx]
            return caminho[::-1], g_score[end_idx], nos_explorados
        
        for vizinho_idx in G.successor_indices(current_idx):
            aresta_data = G.get_edge_data(current_idx, vizinho_idx)
            tentative_g = g_score[current_idx] + aresta_data['weight']
            
            if tentative_g < g_score[vizinho_idx]:
                predecessores[vizinho_idx] = current_idx
                g_score[vizinho_idx] = tentative_g
                
                vizinho_id = index_to_node_id[vizinho_idx]
                vizinho_lat, vizinho_lon = nodes[vizinho_id]
                h_score = euclidean_heuristic(vizinho_lat, vizinho_lon, end_lat, end_lon)
                
                f_score = tentative_g + h_score
                heapq.heappush(open_set, (f_score, vizinho_idx))
    
    return None, float('inf'), nos_explorados
