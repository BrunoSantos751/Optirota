import heapq
import math

def haversine_heuristic(lat1, lon1, lat2, lon2):
    R = 6371000
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi/2)**2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda/2)**2
    return 2 * R * math.atan2(math.sqrt(a), math.sqrt(1 - a))

def astar(G, start_id, end_id, nodes, node_id_to_index, index_to_node_id):
    if start_id not in node_id_to_index or end_id not in node_id_to_index:
        return None, float('inf'), 0
    
    start_idx = node_id_to_index[start_id]
    end_idx = node_id_to_index[end_id]
    
    end_lat, end_lon = nodes[end_id]
    
    g_score = {node: float('inf') for node in G.node_indices()}
    g_score[start_idx] = 0
    
    f_score = {node: float('inf') for node in G.node_indices()}
    start_lat, start_lon = nodes[start_id]
    f_score[start_idx] = haversine_heuristic(start_lat, start_lon, end_lat, end_lon)
    
    open_set = [(f_score[start_idx], start_idx)]
    closed_set = set()
    
    predecessores = {node: None for node in G.node_indices()}
    nos_explorados = 0
    
    while open_set:
        current_f, current_idx = heapq.heappop(open_set)
        
        if current_idx in closed_set:
            continue
            
        closed_set.add(current_idx)
        nos_explorados += 1
        
        if current_idx == end_idx:
            caminho = []
            no_atual = end_idx
            while no_atual is not None:
                caminho.append(index_to_node_id[no_atual])
                no_atual = predecessores[no_atual]
            
            caminho.reverse()
            return caminho, g_score[end_idx], nos_explorados
        
        for vizinho_idx in G.successor_indices(current_idx):
            if vizinho_idx in closed_set:
                continue
                
            aresta_data = G.get_edge_data(current_idx, vizinho_idx)
            tentative_g_score = g_score[current_idx] + aresta_data['weight']
            
            if tentative_g_score < g_score[vizinho_idx]:
                predecessores[vizinho_idx] = current_idx
                g_score[vizinho_idx] = tentative_g_score
                
                vizinho_id = index_to_node_id[vizinho_idx]
                vizinho_lat, vizinho_lon = nodes[vizinho_id]
                h_score = haversine_heuristic(vizinho_lat, vizinho_lon, end_lat, end_lon)
                
                f_score[vizinho_idx] = g_score[vizinho_idx] + h_score
                
                heapq.heappush(open_set, (f_score[vizinho_idx], vizinho_idx))
    
    return None, float('inf'), nos_explorados