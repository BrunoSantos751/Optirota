import math
from collections import defaultdict
from src.Algoritimos.astar_euclidean import astar as astar_euclidean # Importa o astar_euclidean

class VRPSolver:
    def __init__(self, graph, nodes, node_id_to_index, index_to_node_id, depot_id, vehicles, customers):
        self.graph = graph
        self.nodes = nodes
        self.node_id_to_index = node_id_to_index
        self.index_to_node_id = index_to_node_id
        self.depot_id = depot_id
        self.vehicles = vehicles  # Lista de dicionários: [{'id': 1, 'capacity': 100, 'speed': 50}]
        self.customers = customers # Lista de dicionários: [{'id': cust_id, 'demand': 10, 'time_window_start': 9, 'time_window_end': 17, 'service_time': 0}]
        self.distance_matrix = {}
        self.customer_data = {c['id']: c for c in customers}
        self.vehicle_data = {v['id']: v for v in vehicles}

    def _calculate_distance(self, start_node_id, end_node_id):
        # Usa astar_euclidean para calcular a distância e o tempo
        path, distance, time = astar_euclidean(self.graph, start_node_id, end_node_id, self.nodes, self.node_id_to_index, self.index_to_node_id)
        return distance, time

    def _build_distance_matrix(self):
        all_locations = [self.depot_id] + [c['id'] for c in self.customers]
        for i in all_locations:
            for j in all_locations:
                if i == j:
                    self.distance_matrix[(i, j)] = (0, 0)
                elif (i, j) not in self.distance_matrix:
                    dist, time = self._calculate_distance(i, j)
                    self.distance_matrix[(i, j)] = (dist, time)
                    self.distance_matrix[(j, i)] = (dist, time) # Assumindo simetria

    def solve(self):
        self._build_distance_matrix()
        
        unassigned_customers = set(c['id'] for c in self.customers)
        routes = defaultdict(list) # {vehicle_id: [depot, cust1, cust2, ..., depot]}
        vehicle_current_load = defaultdict(int)
        vehicle_current_time = defaultdict(int)
        
        # Inicializa as rotas com o depósito
        for vehicle in self.vehicles:
            routes[vehicle['id']].append(self.depot_id)
            vehicle_current_time[vehicle['id']] = 0 # Assumindo que os veículos começam no depósito no tempo 0

        while unassigned_customers:
            best_customer = None
            best_vehicle_id = None
            best_insertion_cost = float('inf')
            
            for customer_id in unassigned_customers:
                customer_demand = self.customer_data[customer_id]['demand']
                customer_tw_start = self.customer_data[customer_id]['time_window_start']
                customer_tw_end = self.customer_data[customer_id]['time_window_end']
                customer_service_time = self.customer_data[customer_id].get('service_time', 0) # Adiciona tempo de serviço
                
                for vehicle in self.vehicles:
                    vehicle_id = vehicle['id']
                    vehicle_capacity = self.vehicle_data[vehicle_id]['capacity']

                    # CVRP Constraint: Check capacity
                    if vehicle_current_load[vehicle_id] + customer_demand > vehicle_capacity:
                        continue # Cannot assign this customer to this vehicle, capacity exceeded

                    last_node_in_route = routes[vehicle_id][-1]
                    dist_to_customer, time_to_customer = self.distance_matrix[(last_node_in_route, customer_id)]
                    
                    # VRPTW Constraint: Check time window
                    arrival_time = vehicle_current_time[vehicle_id] + time_to_customer
                    
                    # If arrives too early, wait until time window starts
                    wait_time = max(0, customer_tw_start - arrival_time)
                    service_start_time = arrival_time + wait_time
                    
                    if service_start_time > customer_tw_end:
                        continue # Cannot assign this customer, violates time window

                    current_cost = dist_to_customer # Still using distance as primary cost for now
                    
                    if current_cost < best_insertion_cost:
                        best_insertion_cost = current_cost
                        best_customer = customer_id
                        best_vehicle_id = vehicle_id
            
            if best_customer is not None:
                routes[best_vehicle_id].append(best_customer)
                unassigned_customers.remove(best_customer)
                
                # Update load and time for the assigned vehicle
                vehicle_current_load[best_vehicle_id] += self.customer_data[best_customer]['demand']
                
                last_node_in_route = routes[best_vehicle_id][-2] # Previous node
                dist, time_travel = self.distance_matrix[(last_node_in_route, best_customer)]
                
                # Recalculate arrival and departure time considering service time and waiting
                arrival_time = vehicle_current_time[best_vehicle_id] + time_travel
                wait_time = max(0, self.customer_data[best_customer]['time_window_start'] - arrival_time)
                departure_time = arrival_time + wait_time + self.customer_data[best_customer].get('service_time', 0)
                
                vehicle_current_time[best_vehicle_id] = departure_time
            else:
                # No more customers can be assigned under current logic (all assigned or no valid vehicle found)
                break
        
        # Retornar ao depósito para cada rota
        for vehicle_id in routes:
            if routes[vehicle_id][-1] != self.depot_id:
                # Calculate time to return to depot
                last_customer_id = routes[vehicle_id][-1]
                dist_to_depot, time_to_depot = self.distance_matrix[(last_customer_id, self.depot_id)]
                
                # Check if returning to depot is possible within vehicle's operational time (if any)
                # For simplicity, assuming no hard vehicle end time for now, just adding travel time
                vehicle_current_time[vehicle_id] += time_to_depot
                routes[vehicle_id].append(self.depot_id)

        print("VRP Solver: Rotas geradas com heurística Vizinho Mais Próximo (com CVRP e VRPTW). ")
        return dict(routes)

# Exemplo de uso (para testes internos, pode ser removido ou adaptado depois)
if __name__ == "__main__":
    # Este bloco precisaria de um grafo e dados de clientes/veículos reais para rodar.
    # Por exemplo, você precisaria carregar dados do OSM e construir um grafo primeiro.
    print("Módulo vrp_solver.py executado diretamente. Nenhuma ação VRP real foi realizada sem dados de entrada.")


