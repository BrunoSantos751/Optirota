"""
Medição Rápida de Tempo de Execução - A*
Versão simplificada para testes rápidos
"""

import time
import random
import sys
import os
from tabulate import tabulate

# Adicionar caminho do projeto
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.Algoritimos.astar import astar
from src.Algoritimos.dijkstra import dijkstra
from src.Grafo.build import build_graph
from src.OSM.consultaOSM import get_osm_data

def quick_performance_test():
    """Teste rápido de performance"""
    print("🚀 TESTE RÁPIDO DE PERFORMANCE A*")
    print("="*50)
    
    # Carregar dados pequenos para teste rápido
    print("📍 Carregando dados de teste...")
    bbox = (-9.67107, -35.73166, -9.63134, -35.66720)  # Área pequena
    
    try:
        data = get_osm_data(bbox)
        G, nodes, vertices, ways, node_id_to_index, index_to_node_id = build_graph(data)
        print(f"✅ Grafo carregado: {G.num_nodes()} nós, {G.num_edges()} arestas")
    except Exception as e:
        print(f"❌ Erro ao carregar dados: {e}")
        return
    
    # Gerar 5 testes rápidos
    vertices_list = list(vertices)[:100]  # Limitar para testes rápidos
    results = []
    
    print("\n⏱️ Executando testes de tempo...")
    
    for i in range(100):
        start_id = random.choice(vertices_list)
        end_id = random.choice(vertices_list)
        
        if start_id == end_id:
            continue
            
        print(f"🔍 Teste {i+1}: {start_id} → {end_id}")
        
        # Medir A*
        start_time = time.perf_counter()
        astar_path, astar_dist, astar_nodes = astar(
            G, start_id, end_id, nodes, node_id_to_index, index_to_node_id
        )
        astar_time = time.perf_counter() - start_time
        
        # Medir Dijkstra
        start_time = time.perf_counter()
        dijkstra_path, dijkstra_dist = dijkstra(
            G, start_id, end_id, node_id_to_index, index_to_node_id
        )
        dijkstra_time = time.perf_counter() - start_time
        
        if astar_path and dijkstra_path:
            speedup = dijkstra_time / astar_time
            results.append([
                f"Teste {i+1}",
                f"{astar_time*1000:.2f}ms",
                f"{dijkstra_time*1000:.2f}ms", 
                f"{speedup:.1f}x",
                f"{astar_nodes} nós"
            ])
        else:
            results.append([f"Teste {i+1}", "FALHOU", "FALHOU", "-", "-"])
    
    # Mostrar resultados
    if results:
        print(f"\n📊 RESULTADOS:")
        headers = ["Teste", "A* (ms)", "Dijkstra (ms)", "Speedup", "Nós Explorados"]
        print(tabulate(results, headers=headers, tablefmt="grid"))
    
    print(f"\n✅ Teste concluído!")

if __name__ == "__main__":
    quick_performance_test()
    