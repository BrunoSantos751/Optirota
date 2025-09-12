import heapq

def dijkstra(G, start_id, end_id, node_id_to_index, index_to_node_id):
    if start_id not in node_id_to_index or end_id not in node_id_to_index:
        return None, float('inf')
    
    start_idx = node_id_to_index[start_id]
    end_idx = node_id_to_index[end_id]
    
    distancias = {node: float('inf') for node in G.node_indices()}
    distancias[start_idx] = 0
    
    fila_prioridade = [(0, start_idx)]
    predecessores = {node: None for node in G.node_indices()}
    
    caminho_encontrado = False
    while fila_prioridade:
        dist_atual, no_atual_idx = heapq.heappop(fila_prioridade)
        
        if no_atual_idx == end_idx:
            caminho_encontrado = True
            break
            
        if dist_atual > distancias[no_atual_idx]:
            continue
            
        for vizinho_idx in G.successor_indices(no_atual_idx):
            aresta_data = G.get_edge_data(no_atual_idx, vizinho_idx)
            nova_dist = dist_atual + aresta_data['weight']
            
            if nova_dist < distancias[vizinho_idx]:
                distancias[vizinho_idx] = nova_dist
                predecessores[vizinho_idx] = no_atual_idx
                heapq.heappush(fila_prioridade, (nova_dist, vizinho_idx))
    
    if not caminho_encontrado:
        return None, float('inf')

    caminho = []
    no_passado_idx = end_idx
    while no_passado_idx is not None:
        caminho.append(index_to_node_id[no_passado_idx])
        no_passado_idx = predecessores[no_passado_idx]
    
    caminho.reverse()
    
    return caminho, distancias[end_idx]

