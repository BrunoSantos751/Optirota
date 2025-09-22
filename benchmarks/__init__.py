"""
Script principal para executar benchmarks
Execute este arquivo para rodar todos os testes
"""

import sys
import os
from datetime import datetime

# Adicionar caminho para imports
sys.path.insert(0, os.path.dirname(__file__))

def main():
    """Função principal"""
    print("🚀 OptiRota - Sistema de Benchmark")
    print("="*50)
    print(f"⏰ Início: {datetime.now().strftime('%H:%M:%S')}")
    
    print("\nEscolha o tipo de benchmark:")
    print("1. 🏃 Teste Rápido (2-3 minutos)")
    print("2. 🔬 Análise Completa (10-15 minutos)")
    print("3. 📊 Comparação A* vs Dijkstra")
    
    choice = input("\nDigite sua escolha (1/2/3): ").strip()
    
    if choice == "1":
        print("\n🏃 Executando Teste Rápido...")
        from benchmarks.astar_performance import quick_performance_test
        quick_performance_test()
        
    elif choice == "2":
        print("\n🔬 Executando Análise Completa...")
        from benchmarks.astar_performance import main as full_analysis
        full_analysis()
        
    elif choice == "3":
        print("\n📊 Executando Comparação...")
        from src.Algoritimos.performance_comparison import run_performance_test
        
        # Carregar dados para comparação
        from src.OSM.consultaOSM import get_osm_data
        from src.Grafo.build import build_graph
        
        bbox = (-9.67107, -35.73166, -9.65107, -35.71166)
        data = get_osm_data(bbox)
        G, nodes, vertices, ways, node_id_to_index, index_to_node_id = build_graph(data)
        
        run_performance_test(G, nodes, node_id_to_index, index_to_node_id, num_tests=10)
    else:
        print("❌ Opção inválida!")

if __name__ == "__main__":
    main()
    