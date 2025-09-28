import math
from collections import defaultdict
from src.Algoritimos.astar_euclidean import astar as astar_euclidean
import itertools

def _calculate_distance_time_path(graph, nodes, node_id_to_index, index_to_node_id, start_node_id, end_node_id, vehicle_speed_kmh=50):
    if start_node_id == end_node_id: return 0, 0, [start_node_id]
    path, distance_meters, _ = astar_euclidean(graph, start_node_id, end_node_id, nodes, node_id_to_index, index_to_node_id)
    if path is None: return float('inf'), float('inf'), None
    speed_mps = vehicle_speed_kmh * 1000 / 3600
    time_seconds = distance_meters / speed_mps if speed_mps > 0 else float('inf')
    return distance_meters, time_seconds, path

def _build_distance_matrix(graph, nodes, node_id_to_index, index_to_node_id, depot_id, customers, vehicles):
    print("Iniciando construção da matriz de distâncias com A*...")
    distance_matrix = {}
    all_locations = [depot_id] + [c['id'] for c in customers]
    avg_speed = sum(v.get('speed_kmh', 50) for v in vehicles) / len(vehicles) if vehicles else 50
    for i in all_locations:
        for j in all_locations:
            if i == j: continue
            if (i, j) not in distance_matrix:
                dist, time, path = _calculate_distance_time_path(graph, nodes, node_id_to_index, index_to_node_id, i, j, avg_speed)
                distance_matrix[(i, j)] = (dist, time, path)
    print("Matriz de distâncias construída com sucesso.")
    return distance_matrix

def _get_route_info(route_sequence, customer_data, distance_matrix, depot_id):
    """
    Função de validação que calcula o cronograma, duração e métricas de uma sequência de clientes.
    Ajusta o horário de partida do depósito para garantir a viabilidade das janelas de tempo.
    Retorna um dicionário com os dados ou None se a rota for inviável.
    """
    if not route_sequence:
        return None

    full_route = [depot_id] + route_sequence + [depot_id]
    
    first_customer_id = full_route[1]
    _, time_to_first, _ = distance_matrix.get((depot_id, first_customer_id), (float('inf'), float('inf'), []))
    if time_to_first == float('inf'):
        return None

    departure_time = max(0, customer_data[first_customer_id].get('time_window_start', 0) - time_to_first)

    while True:
        current_time = departure_time
        adjustment_needed = 0

        for i in range(len(full_route) - 1):
            u, v = full_route[i], full_route[i+1]
            _, travel_time, _ = distance_matrix.get((u, v), (0, 0, []))

            if travel_time == float('inf'): return None
            
            arrival_at_v = current_time + travel_time

            if v in customer_data:
                cust_v = customer_data[v]
                service_start = max(arrival_at_v, cust_v.get('time_window_start', 0))

                if service_start > cust_v.get('time_window_end', float('inf')):
                    adjustment_needed = service_start - cust_v.get('time_window_end')
                    break

                current_time = service_start + cust_v.get('service_time', 0)
            else:
                current_time = arrival_at_v
        
        if adjustment_needed > 0:
            departure_time -= adjustment_needed
            if departure_time < 0: return None
        else:
            break

    # --- Lógica de cálculo final (com a correção) ---
    schedule = {depot_id: {'arrival': departure_time, 'departure': departure_time}}
    current_time = departure_time
    total_distance = 0
    total_travel_time = 0
    total_service_time = 0

    for i in range(len(full_route) - 1):
        u, v = full_route[i], full_route[i+1]
        dist, travel_time, _ = distance_matrix.get((u, v), (0, 0, []))
        
        total_distance += dist
        total_travel_time += travel_time
        arrival_at_v = current_time + travel_time

        if v in customer_data:
            cust_v = customer_data[v]
            service_time = cust_v.get('service_time', 0)
            total_service_time += service_time
            service_start = max(arrival_at_v, cust_v.get('time_window_start', 0))
            departure_from_v = service_start + service_time
            schedule[v] = {'arrival': arrival_at_v, 'service_start': service_start, 'departure': departure_from_v}
            current_time = departure_from_v
        else: 
            schedule[v]['arrival'] = arrival_at_v
            current_time = arrival_at_v
            
    duration = current_time - departure_time
    wait_time = max(0, duration - total_travel_time - total_service_time)
    
    metrics = {
        'total_distance_meters': total_distance, 'total_travel_time_seconds': total_travel_time,
        'total_service_time_seconds': total_service_time, 'total_wait_time_seconds': wait_time
    }
    
    return {'schedule': schedule, 'duration': duration, 'metrics': metrics, 'route': full_route}

def _cluster_customers(customers, distance_matrix):
    """Agrupa clientes por proximidade de suas janelas de tempo de início."""
    clusters = []
    # Ordena clientes pela janela de início para processar em ordem cronológica
    unclustered = sorted(customers, key=lambda c: c['time_window_start'])

    while unclustered:
        # Começa um novo cluster com o próximo cliente disponível (o com horário mais cedo)
        new_cluster = [unclustered.pop(0)]
        
        i = 0
        while i < len(unclustered):
            candidate = unclustered[i]
            last_cust_in_cluster = new_cluster[-1]

            if candidate['time_window_start'] < last_cust_in_cluster['time_window_start'] + 7200:

                new_cluster.append(unclustered.pop(i))
            else:
                i += 1
        
        clusters.append(new_cluster)
        
    return clusters

def _find_nearest_neighbor_route(cluster_customer_ids, customer_data, distance_matrix, depot_id):
    """
    Encontra a melhor rota para um cluster usando a heurística do Vizinho Mais Próximo,
    testando cada cliente como ponto de partida para melhorar a qualidade.
    """
    best_route = {'info': None, 'duration': float('inf')}

    # Tenta iniciar a rota a partir de cada cliente no cluster
    for start_node in cluster_customer_ids:
        unvisited = list(cluster_customer_ids)
        current_route = []
        
        # Inicia a rota a partir do start_node
        current_node = start_node
        current_route.append(current_node)
        unvisited.remove(current_node)

        # Constrói o resto da rota, sempre buscando o vizinho mais próximo
        while unvisited:
            nearest_neighbor = None
            min_time = float('inf')

            # Encontra o vizinho mais próximo em tempo de viagem
            for neighbor in unvisited:
                _, time, _ = distance_matrix.get((current_node, neighbor), (0, float('inf'), []))
                if time < min_time:
                    min_time = time
                    nearest_neighbor = neighbor
            
            # Se não houver vizinho alcançável, a rota a partir deste ponto é inválida
            if nearest_neighbor is None:
                current_route = [] # Invalida a rota para esta iteração
                break
            
            current_route.append(nearest_neighbor)
            unvisited.remove(nearest_neighbor)
            current_node = nearest_neighbor

        # Se uma rota completa foi construída, usa a função _get_route_info para
        # validar as janelas de tempo e obter o custo real (duração)
        if current_route:
            route_info = _get_route_info(current_route, customer_data, distance_matrix, depot_id)
            if route_info and route_info['duration'] < best_route['duration']:
                best_route['info'] = route_info
                best_route['duration'] = route_info['duration']

    return best_route


def solve_vrp_heuristic(graph, nodes, node_id_to_index, index_to_node_id, depot_id, vehicles, customers):
    if not customers: return {}, "Nenhum cliente para atender.", None
    distance_matrix = _build_distance_matrix(graph, nodes, node_id_to_index, index_to_node_id, depot_id, customers, vehicles)
    customer_data = {c['id']: c for c in customers}

    print("FASE 1: Agrupando clientes em missões lógicas...")
    clusters = _cluster_customers(customers, distance_matrix)
    print(f"Clientes agrupados em {len(clusters)} clusters.")
    
    final_routes = {}
    unassigned_customers_final = set(c['id'] for c in customers)
    used_vehicles = set()

    # Usar uma lista como fila para poder adicionar clusters redivididos.
    # Ordenar pela demanda total para processar os mais "pesados" primeiro.
    clusters_to_process = sorted(clusters, key=lambda c: sum(cust['demand'] for cust in c), reverse=True)

    print("FASE 2: Encontrando a rota para cada cluster com a heurística do Vizinho Mais Próximo...")
    while clusters_to_process:
        cluster = clusters_to_process.pop(0) # Pega o próximo cluster da fila
        cluster_demand = sum(cust['demand'] for cust in cluster)
        cluster_customer_ids = [c['id'] for c in cluster]
        
        # Encontra o menor veículo DISPONÍVEL que pode atender ao cluster
        best_vehicle = None
        available_vehicles = [v for v in vehicles if v['id'] not in used_vehicles]
        
        for v in sorted(available_vehicles, key=lambda v: v['capacity']):
            if v['capacity'] >= cluster_demand:
                best_vehicle = v
                break
        
        if best_vehicle:
            # Se um veículo foi encontrado, a lógica segue como antes
            print(f"Analisando cluster {cluster_customer_ids} para o Veículo {best_vehicle['id']}...")
            
            best_route_for_cluster = _find_nearest_neighbor_route(
                cluster_customer_ids, customer_data, distance_matrix, depot_id
            )
            
            if best_route_for_cluster['info']:
                route_info = best_route_for_cluster['info']
                final_routes[best_vehicle['id']] = {
                    'route': route_info['route'],
                    'load': cluster_demand,
                    'total_time_seconds': route_info['duration'],
                    'schedule': route_info['schedule'],
                    **route_info['metrics']
                }
                used_vehicles.add(best_vehicle['id'])
                unassigned_customers_final -= set(cluster_customer_ids)
                print(f"  -> Rota (Vizinho Mais Próximo) encontrada com duração de {route_info['duration']/60:.0f} min.")
            else:
                 print(f"  -> AVISO: Nenhuma rota viável encontrada para este cluster. Clientes serão reavaliados se possível.")
                 clusters_to_process.append(cluster) # Devolve o cluster para a fila, pode ser que outro veículo o pegue
        
        else:
            # Nenhum veículo único tem capacidade suficiente, vamos dividir o cluster.
            print(f"INFO: Cluster {cluster_customer_ids} com demanda {cluster_demand} é grande demais. Tentando dividir...")
            
            if not available_vehicles:
                print(f"  -> AVISO: Não há veículos disponíveis para atender o cluster {cluster_customer_ids}. Clientes abandonados.")
                continue # Pula para o próximo cluster na fila

            # Encontra a capacidade do maior veículo disponível para basear a divisão
            largest_vehicle_capacity = max(v['capacity'] for v in available_vehicles)
            
            new_cluster_1 = []
            new_cluster_1_demand = 0
            # Ordena clientes pela demanda para tentar agrupar os menores primeiro
            customers_to_split = sorted(cluster, key=lambda c: c['demand'])

            # Cria o primeiro novo cluster com base na capacidade do maior veículo
            for customer in list(customers_to_split):
                if new_cluster_1_demand + customer['demand'] <= largest_vehicle_capacity:
                    new_cluster_1.append(customer)
                    new_cluster_1_demand += customer['demand']
                    customers_to_split.remove(customer)

            if new_cluster_1:
                print(f"  -> Criado novo cluster {[c['id'] for c in new_cluster_1]} com demanda {new_cluster_1_demand}")
                clusters_to_process.append(new_cluster_1)
            
            if customers_to_split: # O que sobrar forma outro cluster
                remaining_demand = sum(c['demand'] for c in customers_to_split)
                print(f"  -> Criado cluster restante {[c['id'] for c in customers_to_split]} com demanda {remaining_demand}")
                clusters_to_process.append(customers_to_split)

            # Reordena a fila para continuar processando os de maior demanda primeiro
            clusters_to_process.sort(key=lambda c: sum(cust['demand'] for cust in c), reverse=True)

    summary = "VRP concluído.\n"
    # A lógica de `unassigned_customers_final` já deve funcionar corretamente
    assigned_customers = {c_id for route_data in final_routes.values() for c_id in route_data['route']}
    unassigned_customers_final = set(c['id'] for c in customers) - assigned_customers
    
    if unassigned_customers_final:
        summary += f"Clientes não atendidos: {list(unassigned_customers_final)}"
    return final_routes, summary, distance_matrix