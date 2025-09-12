import requests


def get_osm_data(bbox):
    overpass_url = "http://overpass-api.de/api/interpreter"
    query = f"""
    [out:json];
    way["highway"]({bbox[0]},{bbox[1]},{bbox[2]},{bbox[3]});
    out body;
    >;
    out skel qt;
    """
    response = requests.get(overpass_url, params={'data': query})
    return response.json()

def get_node_street_name(node_id, ways):
    ruas = set()
    for way in ways:
        if node_id in way["nodes"]:
            ruas.add(way.get("tags", {}).get("name", f"rua sem nome (Node {node_id})"))
    
    if not ruas:
        return f"rua sem nome (Node {node_id})"
    
    return " / ".join(sorted(ruas))

def print_crossings(G, nodes, vertices, ways, node_id_to_index, index_to_node_id, limit=None):
    count = 0
    
    for vertex_id in vertices:
        if vertex_id not in node_id_to_index:
            continue
            
        vertex_idx = node_id_to_index[vertex_id]
        
        try:
            node_data = G[vertex_idx]
        except IndexError:
            continue
        
        nome_cruzamento = get_node_street_name(vertex_id, ways)
        lat, lon = nodes[vertex_id]
        
        print(f" \nNode ID: {vertex_id}\nCruzamento: {nome_cruzamento} ({lat:.6f}, {lon:.6f}) conecta para:")
        
        try:
            # Lidar com arestas de saída
            out_edges_list = G.out_edges(vertex_idx)
            if not out_edges_list:
                print(" -> Nenhuma rua conectada (saída)")
            else:
                for edge_info in out_edges_list:
                    if isinstance(edge_info, int):
                        edge_idx = edge_info
                        source_idx, target_idx = G.get_edge_endpoints_by_index(edge_idx)
                        edge_data = G.get_edge_data_by_index(edge_idx)
                    elif isinstance(edge_info, tuple) and len(edge_info) == 3:
                        source_idx, target_idx, edge_data = edge_info
                    elif isinstance(edge_info, dict):
                        edge_data = edge_info
                        target_idx = G.successors(vertex_idx)[0] if G.successors(vertex_idx) else -1
                        if target_idx == -1: continue
                    else:
                        continue # Pular iteração com formato desconhecido
                    
                    target_id = index_to_node_id[target_idx]
                    rua = edge_data.get('street', 'rua sem nome')
                    peso = edge_data.get('weight', 0)
                    
                    rua_desc = f"{rua} (Node {target_id})" if rua == "rua sem nome" else rua
                    print(f" -> {rua_desc}, distância: {peso:.1f} m")
            
            in_edges_list = G.in_edges(vertex_idx)
            if in_edges_list and len(in_edges_list) != len(out_edges_list):
                print("   Conexões de entrada:")
                for edge_info in in_edges_list:
                    if isinstance(edge_info, int):
                        edge_idx = edge_info
                        source_idx, _ = G.get_edge_endpoints_by_index(edge_idx)
                        edge_data = G.get_edge_data_by_index(edge_idx)
                    elif isinstance(edge_info, tuple) and len(edge_info) == 3:
                        source_idx, _, edge_data = edge_info
                    elif isinstance(edge_info, dict):
                        edge_data = edge_info
                        source_idx = G.predecessors(vertex_idx)[0] if G.predecessors(vertex_idx) else -1
                        if source_idx == -1: continue
                    else:
                        continue
                        
                    source_id = index_to_node_id[source_idx]
                    rua = edge_data.get('street', 'rua sem nome')
                    peso = edge_data.get('weight', 0)
                    
                    rua_desc = f"{rua} (Node {source_id})" if rua == "rua sem nome" else rua
                    print(f"   <- {rua_desc}, distância: {peso:.1f} m")
        
        except Exception as e:
            print(f" -> Erro ao processar conexões: {str(e)}")
        
        count += 1
        if limit and count >= limit:
            break
