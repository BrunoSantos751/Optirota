import random
import time
import heapq

def gerar_grafo_esparso(V, E_max):
    G = {v: [] for v in range(V)}
    edges = 0
    while edges < E_max:
        u = random.randint(0, V - 1)
        v = random.randint(0, V - 1)
        if u != v:
            peso = random.randint(1, 10)
            G[u].append((v, peso))
            edges += 1
    return G

def dijkstra_heap(G, start):
    V = len(G)
    dist = [float('inf')] * V
    dist[start] = 0
    heap = [(0, start)]
    while heap:
        d, u = heapq.heappop(heap)
        if d > dist[u]:
            continue
        for v, w in G[u]:
            nd = d + w
            if nd < dist[v]:
                dist[v] = nd
                heapq.heappush(heap, (nd, v))
    return dist

def dijkstra_array(G, start):
    V = len(G)
    dist = [float('inf')] * V
    dist[start] = 0
    visited = [False] * V
    for _ in range(V):
        u = -1
        min_dist = float('inf')
        for i in range(V):
            if not visited[i] and dist[i] < min_dist:
                min_dist = dist[i]
                u = i
        if u == -1:
            break
        visited[u] = True
        for v, w in G[u]:
            if dist[u] + w < dist[v]:
                dist[v] = dist[u] + w
    return dist

def testar_eficiencia(V, E):
    print(f"Grafo com {V} vértices e {E} arestas")
    G = gerar_grafo_esparso(V, E)
    start = 0
    
    t0 = time.time()
    dist_heap = dijkstra_heap(G, start)
    t1 = time.time()
    print(f"Dijkstra com heap: {t1 - t0:.4f} segundos")
    
    t2 = time.time()
    dist_array = dijkstra_array(G, start)
    t3 = time.time()
    print(f"Dijkstra com array: {t3 - t2:.4f} segundos")
    
    # Verifica se as distâncias são as mesmas
    igual = all(abs(a - b) < 1e-6 for a, b in zip(dist_heap, dist_array))
    print(f"Resultados iguais? {'Sim' if igual else 'Não'}\n")

if __name__ == "__main__":
    # Teste em grafo pequeno (para ver resultado rápido)
    testar_eficiencia(500, 1000)
    
    # Teste em grafo maior (demora mais tempo)
    testar_eficiencia(2000, 4000)
