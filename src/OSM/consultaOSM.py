import requests

# --- Função para consultar OSM via Overpass API ---
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

# --- Função para obter nome da rua de um nó (cruzamento) ---
def get_node_street_name(node_id, ways):
    ruas = set()
    for way in ways:
        if node_id in way["nodes"]:
            ruas.add(way.get("tags", {}).get("name", f"rua sem nome (Node {node_id})"))
    if not ruas:
        return f"rua sem nome (Node {node_id})"
    return " / ".join(ruas)



# --- Impressão segura dos cruzamentos ---
def print_crossings(G, nodes, vertices, ways, limit=None):
    """
    Mostra os cruzamentos e suas conexões, ignorando nodes sem arestas.

    Args:
        G : nx.DiGraph - grafo
        nodes : dict - {node_id: (lat, lon)}
        vertices : set - nodes que são cruzamentos
        ways : list - ways do OSM para pegar nomes das ruas
        limit : int - opcional, limita a quantidade de cruzamentos impressos
    """
    count = 0
    for v in vertices:
        if v not in G:
            continue  # ignora nodes sem arestas
        nome_cruzamento = get_node_street_name(v, ways)
        print(f"\nCruzamento: {nome_cruzamento} ({nodes[v]}) conecta para:")

        vizinhos = list(G.neighbors(v))
        if not vizinhos:
            print(" -> Nenhuma rua conectada")
        else:
            for viz in vizinhos:
                rua = G[v][viz]['street']
                rua_desc = f"{rua} (Node {viz})" if rua == "rua sem nome" else rua
                print(f" -> {rua_desc}, distância: {G[v][viz]['weight']:.1f} m")
        count += 1
        if limit and count >= limit:
            break

















    