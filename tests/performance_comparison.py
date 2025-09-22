import sys
import os
import time
import random
import matplotlib.pyplot as plt
import json
from src.Algoritimos.dijkstra import dijkstra
from src.Algoritimos.astar import astar

current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(current_dir))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

class PerformanceComparator:
    def __init__(self, G, nodes, node_id_to_index, index_to_node_id):
        self.G = G
        self.nodes = nodes
        self.node_id_to_index = node_id_to_index
        self.index_to_node_id = index_to_node_id
        self.results = []
    
    def generate_random_pairs(self, num_pairs=10):
        vertices = list(self.node_id_to_index.keys())
        pairs = []
        
        for _ in range(num_pairs):
            start_id = random.choice(vertices)
            end_id = random.choice(vertices)
            
            while start_id == end_id:
                end_id = random.choice(vertices)
            
            pairs.append((start_id, end_id))
        
        return pairs
    
    def run_comparison(self, num_tests=10):
        print(f"Iniciando comparação de desempenho com {num_tests} testes...")
        
        test_pairs = self.generate_random_pairs(num_tests)
        
        dijkstra_times = []
        astar_times = []
        dijkstra_nodes_explored = []
        astar_nodes_explored = []
        test_distances = []
        valid_tests = 0
        
        for i, (start_id, end_id) in enumerate(test_pairs, 1):
            print(f"Teste {i}/{num_tests}: {start_id} -> {end_id}")
            
            start_time = time.time()
            dijkstra_path, dijkstra_dist = dijkstra(
                self.G, start_id, end_id, 
                self.node_id_to_index, self.index_to_node_id
            )
            dijkstra_time = time.time() - start_time
            
            start_time = time.time()
            astar_path, astar_dist, astar_explored = astar(
                self.G, start_id, end_id, self.nodes,
                self.node_id_to_index, self.index_to_node_id
            )
            astar_time = time.time() - start_time
            
            dijkstra_explored = len([idx for idx in self.G.node_indices()])
            
            if dijkstra_path is not None and astar_path is not None:
                dijkstra_times.append(dijkstra_time)
                astar_times.append(astar_time)
                dijkstra_nodes_explored.append(dijkstra_explored)
                astar_nodes_explored.append(astar_explored)
                test_distances.append(dijkstra_dist)
                valid_tests += 1
                
                distance_diff = abs(dijkstra_dist - astar_dist)
                if distance_diff > 1.0:
                    print(f"AVISO: Diferença nas distâncias: {distance_diff:.2f}m")
            else:
                print(f"  - Caminho não encontrado")
        
        if valid_tests > 0:
            results = {
                'valid_tests': valid_tests,
                'total_tests': num_tests,
                'dijkstra': {
                    'avg_time': sum(dijkstra_times) / len(dijkstra_times),
                    'min_time': min(dijkstra_times),
                    'max_time': max(dijkstra_times),
                    'avg_nodes_explored': sum(dijkstra_nodes_explored) / len(dijkstra_nodes_explored)
                },
                'astar': {
                    'avg_time': sum(astar_times) / len(astar_times),
                    'min_time': min(astar_times),
                    'max_time': max(astar_times),
                    'avg_nodes_explored': sum(astar_nodes_explored) / len(astar_nodes_explored)
                },
                'speedup_factor': sum(dijkstra_times) / sum(astar_times) if sum(astar_times) > 0 else 0,
                'node_reduction_factor': (sum(dijkstra_nodes_explored) / sum(astar_nodes_explored)) if sum(astar_nodes_explored) > 0 else 0
            }
            
            self.results.append(results)
            return results
        else:
            print("Nenhum teste válido foi executado.")
            return None
    
    def print_results(self, results):
        if results is None:
            return "Nenhum resultado disponível."
        
        output = []
        output.append("="*50)
        output.append("RESULTADOS DA COMPARAÇÃO DE DESEMPENHO")
        output.append("="*50)
        
        output.append(f"Testes válidos: {results['valid_tests']}/{results['total_tests']}")
        
        output.append(f"\nDIJKSTRA:")
        output.append(f"   Tempo médio: {results['dijkstra']['avg_time']*1000:.2f}ms")
        output.append(f"   Tempo mínimo: {results['dijkstra']['min_time']*1000:.2f}ms")
        output.append(f"   Tempo máximo: {results['dijkstra']['max_time']*1000:.2f}ms")
        output.append(f"   Nós explorados (média): {results['dijkstra']['avg_nodes_explored']:.0f}")
        
        output.append(f"\nA* (A-ESTRELA):")
        output.append(f"   Tempo médio: {results['astar']['avg_time']*1000:.2f}ms")
        output.append(f"   Tempo mínimo: {results['astar']['min_time']*1000:.2f}ms")
        output.append(f"   Tempo máximo: {results['astar']['max_time']*1000:.2f}ms")
        output.append(f"   Nós explorados (média): {results['astar']['avg_nodes_explored']:.0f}")
        
        output.append(f"\nCOMPARAÇÃO:")
        output.append(f"   A* é {results['speedup_factor']:.2f}x mais rápido que Dijkstra")
        output.append(f"   A* explora {results['node_reduction_factor']:.2f}x menos nós que Dijkstra")
        
        efficiency_improvement = ((results['dijkstra']['avg_time'] - results['astar']['avg_time']) / results['dijkstra']['avg_time']) * 100
        output.append(f"   Melhoria de eficiência: {efficiency_improvement:.1f}%")
        
        return "\n".join(output)
    
    def plot_comparison(self, results, save_path="performance_comparison.png"):
        if results is None:
            print("Nenhum resultado disponível para plotar.")
            return
        
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
        
        algorithms = ['Dijkstra', 'A*']
        times = [results['dijkstra']['avg_time']*1000, results['astar']['avg_time']*1000]
        colors = ['#ff7f0e', '#1f77b4']
        
        bars1 = ax1.bar(algorithms, times, color=colors)
        ax1.set_ylabel('Tempo Médio (ms)')
        ax1.set_title('Comparação de Tempo de Execução')
        ax1.grid(True, alpha=0.3)
        
        for bar, time in zip(bars1, times):
            height = bar.get_height()
            ax1.text(bar.get_x() + bar.get_width()/2., height + height*0.01,
                    f'{time:.2f}ms', ha='center', va='bottom')
        
        nodes_explored = [results['dijkstra']['avg_nodes_explored'], results['astar']['avg_nodes_explored']]
        
        bars2 = ax2.bar(algorithms, nodes_explored, color=colors)
        ax2.set_ylabel('Nós Explorados (média)')
        ax2.set_title('Comparação de Nós Explorados')
        ax2.grid(True, alpha=0.3)
        
        for bar, nodes in zip(bars2, nodes_explored):
            height = bar.get_height()
            ax2.text(bar.get_x() + bar.get_width()/2., height + height*0.01,
                    f'{nodes:.0f}', ha='center', va='bottom')
        
        plt.tight_layout()
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"Gráfico salvo em: {os.path.abspath(save_path)}")
        plt.show()
    
    def save_results(self, results, filepath="performance_results.json"):
        if results is None:
            print("Nenhum resultado para salvar.")
            return
        
        with open(filepath, 'w') as f:
            json.dump(results, f, indent=2)
        
        print(f"Resultados salvos em: {os.path.abspath(filepath)}")

def run_performance_test(G, nodes, node_id_to_index, index_to_node_id, num_tests=10):
    comparator = PerformanceComparator(G, nodes, node_id_to_index, index_to_node_id)
    results = comparator.run_comparison(num_tests)
    
    if results:
        comparator.print_results(results)
        comparator.plot_comparison(results)
        comparator.save_results(results)
    
    return comparator.print_results(results)