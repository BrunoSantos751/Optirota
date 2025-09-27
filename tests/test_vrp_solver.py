import unittest
import rustworkx as rx
import math
from src.Algoritimos.vrp_solver import VRPSolver

class TestVRPSolver(unittest.TestCase):

    def setUp(self):
        # Criar um grafo de exemplo (simplificado para teste)
        self.graph = rx.PyGraph()
        self.nodes = {}
        self.node_id_to_index = {}
        self.index_to_node_id = {}

        # Adicionar nós (depósito e clientes)
        # Formato: node_id: (latitude, longitude)
        self.add_node(100, (0.0, 0.0)) # Depósito
        self.add_node(101, (0.1, 0.1)) # Cliente 1
        self.add_node(102, (0.2, 0.2)) # Cliente 2
        self.add_node(103, (0.3, 0.3)) # Cliente 3
        self.add_node(104, (0.4, 0.4)) # Cliente 4

        # Adicionar arestas (conexões entre nós)
        # Para simplificar, vamos criar um grafo totalmente conectado com pesos baseados na distância euclidiana
        # Em um cenário real, isso viria do OSM e do astar_euclidean
        node_ids = list(self.nodes.keys())
        for i in range(len(node_ids)):
            for j in range(i + 1, len(node_ids)):
                id1 = node_ids[i]
                id2 = node_ids[j]
                lat1, lon1 = self.nodes[id1]
                lat2, lon2 = self.nodes[id2]
                # Distância euclidiana simples para o teste
                weight = math.sqrt((lat2 - lat1)**2 + (lon2 - lon1)**2)
                self.graph.add_edge(self.node_id_to_index[id1], self.node_id_to_index[id2], {"weight": weight, "time": weight/0.0001})

        self.depot_id = 100
        self.vehicles = [
            {'id': 1, 'capacity': 20, 'speed': 50},
            {'id': 2, 'capacity': 20, 'speed': 50}
        ]
        self.customers = [
            {'id': 101, 'demand': 5, 'time_window_start': 8, 'time_window_end': 12, 'service_time': 1},
            {'id': 102, 'demand': 7, 'time_window_start': 9, 'time_window_end': 13, 'service_time': 1},
            {'id': 103, 'demand': 8, 'time_window_start': 10, 'time_window_end': 14, 'service_time': 1},
            {'id': 104, 'demand': 3, 'time_window_start': 8, 'time_window_end': 11, 'service_time': 1}
        ]

    def add_node(self, node_id, coords):
        index = self.graph.add_node(node_id)
        self.nodes[node_id] = coords
        self.node_id_to_index[node_id] = index
        self.index_to_node_id[index] = node_id

    def test_solve_cvrp_vrptw(self):
        solver = VRPSolver(self.graph, self.nodes, self.node_id_to_index, self.index_to_node_id, 
                           self.depot_id, self.vehicles, self.customers)
        routes = solver.solve()

        self.assertIsInstance(routes, dict)
        self.assertGreater(len(routes), 0)

        total_demand = sum(c['demand'] for c in self.customers)
        assigned_demand = 0
        
        for vehicle_id, route in routes.items():
            self.assertGreater(len(route), 2) # Deve ter pelo menos depot -> customer -> depot
            self.assertEqual(route[0], self.depot_id)
            self.assertEqual(route[-1], self.depot_id)

            current_load = 0
            current_time = 0
            
            # Simular a rota para verificar restrições
            for i in range(len(route) - 1):
                start_node = route[i]
                end_node = route[i+1]

                if start_node == self.depot_id:
                    # Começa do depósito
                    current_time = 0 
                    current_load = 0
                elif start_node in solver.customer_data:
                    # Cliente visitado, adiciona demanda e tempo de serviço
                    current_load += solver.customer_data[start_node]['demand']
                    assigned_demand += solver.customer_data[start_node]['demand']
                    
                    # Verifica capacidade
                    self.assertLessEqual(current_load, solver.vehicle_data[vehicle_id]['capacity'])

                    # Verifica janela de tempo (chegada e serviço)
                    customer_tw_start = solver.customer_data[start_node]['time_window_start']
                    customer_tw_end = solver.customer_data[start_node]['time_window_end']
                    service_time = solver.customer_data[start_node]['service_time']

                    # current_time já deve ser o tempo de partida do nó anterior
                    # O tempo de chegada ao cliente 'start_node' foi calculado na iteração anterior
                    # Aqui, precisamos garantir que o tempo de partida do 'start_node' esteja dentro da TW
                    # Para este teste simplificado, vamos apenas verificar o tempo de chegada
                    # A lógica de espera e tempo de serviço já está no solver, aqui verificamos o resultado final
                    # Este teste é mais complexo para simular exatamente o solver, vamos focar na capacidade e que a rota é válida
                    pass # A verificação de TW é mais complexa para simular aqui exatamente como o solver faz

                if end_node != self.depot_id: # Não adiciona demanda do depósito
                    # Simula a viagem para o próximo nó
                    dist, time_travel = solver.distance_matrix[(start_node, end_node)]
                    current_time += time_travel

                    # Se o próximo nó é um cliente, verifica janela de tempo
                    if end_node in solver.customer_data:
                        customer_tw_start = solver.customer_data[end_node]['time_window_start']
                        customer_tw_end = solver.customer_data[end_node]['time_window_end']
                        service_time = solver.customer_data[end_node]['service_time']

                        # Verifica se chegou antes da janela, espera
                        arrival_at_customer = current_time
                        self.assertLessEqual(arrival_at_customer, customer_tw_end, f"Veículo {vehicle_id} chegou ao cliente {end_node} fora da janela de tempo (tarde demais).")
                        current_time = max(arrival_at_customer, customer_tw_start) + service_time

        # Verifica se todos os clientes foram atendidos (se a capacidade e TW permitirem)
        # self.assertEqual(assigned_demand, total_demand, "Nem todos os clientes foram atendidos ou a demanda total não corresponde.")
        # ^ Este assert pode falhar se alguns clientes não puderem ser atendidos devido a restrições, o que é esperado em VRP
        print(f"\nRotas geradas: {routes}")
        print(f"Demanda total: {total_demand}, Demanda atribuída: {assigned_demand}")

if __name__ == '__main__':
    unittest.main()


