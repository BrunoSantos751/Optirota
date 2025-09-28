import tkinter as tk
from tkinter import messagebox, scrolledtext, ttk, simpledialog
from io import StringIO
import sys
import json
from src.OSM.consultaOSM import get_osm_data
from src.Grafo.build import build_graph
from src.Grafo.visualizar import plot_graph_with_names, plot_path_only, plot_vrp_routes
from src.Algoritimos.dijkstra import dijkstra
from src.Algoritimos.astar_euclidean import astar
from src.Algoritimos.vrp_solver import solve_vrp_heuristic

def capture_print_crossings(G, nodes, vertices, ways, node_id_to_index, index_to_node_id, limit=20):
    """Captura a saída da função print_crossings para exibir na interface."""
    buffer = StringIO()
    sys_stdout = sys.stdout
    sys.stdout = buffer
    try:
        from src.OSM.consultaOSM import print_crossings
        print_crossings(G, nodes, vertices, ways, node_id_to_index, index_to_node_id, limit)
    finally:
        sys.stdout = sys_stdout
    return buffer.getvalue()

class OptiRotaApp:
    """Classe principal da aplicação com interface gráfica."""
    def __init__(self, root):
        self.root = root
        self.root.title("OptiRota - Otimizador de Rotas")
        self.root.geometry("950x800")
        self.loaded_graph = { "G": None, "nodes": None, "vertices": None, "ways": None, "node_id_to_index": None, "index_to_node_id": None }
        self._create_widgets()

    def _seconds_to_time_str(self, seconds):
        """Converte segundos para uma string no formato HH:MM."""
        if not isinstance(seconds, (int, float)): return ""
        seconds = int(seconds)
        h = seconds // 3600
        m = (seconds % 3600) // 60
        return f"{h:02d}:{m:02d}"

    def _time_str_to_seconds(self, time_str):
        """Converte uma string HH:MM para segundos."""
        try:
            h, m = map(int, time_str.split(':'))
            return h * 3600 + m * 60
        except (ValueError, IndexError):
            raise ValueError(f"Formato de hora inválido: '{time_str}'. Use HH:MM.")

    def _create_widgets(self):
        """Cria todos os elementos da interface gráfica."""
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(expand=True, fill='both', padx=10, pady=10)
        
        self.tab1 = ttk.Frame(self.notebook)
        self.notebook.add(self.tab1, text='Grafo & Rota Simples')
        self._create_tab1_widgets(self.tab1)
        
        self.tab2 = ttk.Frame(self.notebook)
        self.notebook.add(self.tab2, text='Otimizador de Frota (VRP)')
        self._create_tab2_widgets(self.tab2)
        
    def _create_tab1_widgets(self, parent_frame):
        """Cria os widgets para a primeira aba (Grafo e Rota Simples)."""
        control_frame = ttk.LabelFrame(parent_frame, text="Configurações do Grafo e Busca", padding=(10, 10))
        control_frame.pack(fill='x', padx=5, pady=5)
        control_frame.columnconfigure(1, weight=1)
        
        ttk.Label(control_frame, text="Sul (lat min):").grid(row=0, column=0, sticky="w")
        self.south_entry = ttk.Entry(control_frame); self.south_entry.grid(row=0, column=1, sticky="ew", padx=5); self.south_entry.insert(0, "-9.67107")
        ttk.Label(control_frame, text="Oeste (lon min):").grid(row=1, column=0, sticky="w")
        self.west_entry = ttk.Entry(control_frame); self.west_entry.grid(row=1, column=1, sticky="ew", padx=5); self.west_entry.insert(0, "-35.73166")
        ttk.Label(control_frame, text="Norte (lat max):").grid(row=2, column=0, sticky="w")
        self.north_entry = ttk.Entry(control_frame); self.north_entry.grid(row=2, column=1, sticky="ew", padx=5); self.north_entry.insert(0, "-9.63134")
        ttk.Label(control_frame, text="Leste (lon max):").grid(row=3, column=0, sticky="w")
        self.east_entry = ttk.Entry(control_frame); self.east_entry.grid(row=3, column=1, sticky="ew", padx=5); self.east_entry.insert(0, "-35.66720")
        
        ttk.Label(control_frame, text="Nó de Origem:").grid(row=4, column=0, sticky="w", pady=(10, 0))
        self.start_id_entry = ttk.Entry(control_frame); self.start_id_entry.grid(row=4, column=1, sticky="ew", padx=5, pady=(10, 0)); self.start_id_entry.insert(0, "432674688")
        ttk.Label(control_frame, text="Nó de Destino:").grid(row=5, column=0, sticky="w")
        self.end_id_entry = ttk.Entry(control_frame); self.end_id_entry.grid(row=5, column=1, sticky="ew", padx=5); self.end_id_entry.insert(0, "7044690950")
        
        button_frame = ttk.Frame(parent_frame); button_frame.pack(fill='x', padx=5, pady=5); button_frame.columnconfigure((0,1,2,3), weight=1)
        ttk.Button(button_frame, text="Carregar Dados / Mostrar Conexões", command=self.show_connections).grid(row=0, column=0, columnspan=2, padx=5, pady=5, sticky='ew')
        ttk.Button(button_frame, text="Limpar Cache", command=self.clear_cache).grid(row=0, column=2, columnspan=2, padx=5, pady=5, sticky='ew')
        ttk.Button(button_frame, text="Visualizar Grafo Completo", command=self.show_graph).grid(row=1, column=0, columnspan=2, padx=5, pady=5, sticky='ew')
        ttk.Button(button_frame, text="Calcular Rota com Dijkstra", command=lambda: self._run_pathfinding_algorithm(dijkstra, "Dijkstra")).grid(row=1, column=2, padx=5, pady=5, sticky='ew')
        ttk.Button(button_frame, text="Calcular Rota com A*", command=lambda: self._run_pathfinding_algorithm(astar, "A*")).grid(row=1, column=3, padx=5, pady=5, sticky='ew')
        
        output_frame = ttk.LabelFrame(parent_frame, text="Resultados e Informações", padding=(10, 10)); output_frame.pack(expand=True, fill='both', padx=5, pady=5)
        self.output_text = scrolledtext.ScrolledText(output_frame, wrap="word", height=10); self.output_text.pack(expand=True, fill='both')

    def _create_tab2_widgets(self, parent_frame):
        """Cria os widgets para a segunda aba (Otimizador de Frota)."""
        vrp_frame = ttk.LabelFrame(parent_frame, text="Dados do Problema de Roteamento de Veículos (VRP)", padding=(10, 10)); vrp_frame.pack(fill='both', expand=True, padx=5, pady=5); vrp_frame.columnconfigure(0, weight=1)
        
        config_frame = ttk.Frame(vrp_frame); config_frame.grid(row=0, column=0, sticky="ew", pady=5)
        config_frame.columnconfigure(1, weight=1)
        ttk.Label(config_frame, text="ID do Depósito:").grid(row=0, column=0, sticky="w", padx=5)
        self.depot_id_entry = ttk.Entry(config_frame); self.depot_id_entry.grid(row=0, column=1, sticky="ew")
        self.depot_id_entry.insert(0, "1964909054")
        ttk.Label(config_frame, text="Raio de Serviço (km):").grid(row=1, column=0, sticky="w", padx=5, pady=(5,0))
        self.radius_entry = ttk.Entry(config_frame); self.radius_entry.grid(row=1, column=1, sticky="ew", pady=(5,0))
        self.radius_entry.insert(0, "3.0")
        
        vehicles_frame = ttk.LabelFrame(vrp_frame, text="Frota de Veículos", padding=10); vehicles_frame.grid(row=1, column=0, sticky="ew", pady=5)
        self.vehicles_tree = ttk.Treeview(vehicles_frame, columns=("ID", "Capacidade", "Velocidade"), show="headings", height=4)
        self.vehicles_tree.heading("ID", text="ID"); self.vehicles_tree.heading("Capacidade", text="Capacidade"); self.vehicles_tree.heading("Velocidade", text="Velocidade (km/h)"); self.vehicles_tree.pack(side="top", fill="x", expand=True)
        btn_frame_v = ttk.Frame(vehicles_frame); btn_frame_v.pack(fill="x", pady=5)
        ttk.Button(btn_frame_v, text="Adicionar Veículo", command=self.add_vehicle).pack(side="left", padx=5)
        ttk.Button(btn_frame_v, text="Remover Veículo", command=self.remove_vehicle).pack(side="left", padx=5)
        
        customers_frame = ttk.LabelFrame(vrp_frame, text="Clientes", padding=10); customers_frame.grid(row=2, column=0, sticky="nsew", pady=5); vrp_frame.rowconfigure(2, weight=1)
        self.customers_tree = ttk.Treeview(customers_frame, columns=("ID", "Demanda", "Janela Início", "Janela Fim", "Tempo Serviço"), show="headings", height=6)
        self.customers_tree.heading("ID", text="ID Nó"); self.customers_tree.heading("Demanda", text="Demanda")
        self.customers_tree.heading("Janela Início", text="Início (HH:MM)"); self.customers_tree.heading("Janela Fim", text="Fim (HH:MM)"); self.customers_tree.heading("Tempo Serviço", text="Serviço (s)"); self.customers_tree.pack(side="top", fill="both", expand=True)
        btn_frame_c = ttk.Frame(customers_frame); btn_frame_c.pack(fill="x", pady=5)
        ttk.Button(btn_frame_c, text="Adicionar Cliente", command=self.add_customer).pack(side="left", padx=5)
        ttk.Button(btn_frame_c, text="Remover Cliente", command=self.remove_customer).pack(side="left", padx=5)
        
        solve_button = ttk.Button(vrp_frame, text="Otimizar Rotas (VRP)", command=self.solve_vrp); solve_button.grid(row=3, column=0, pady=10, sticky='ew')
        self.populate_initial_vrp_data()
        
    def show_graph(self):
        """Plota o grafo completo da área selecionada."""
        if self.check_data_loaded():
            depot_id = int(self.depot_id_entry.get()) if self.depot_id_entry.get().isdigit() else None
            radius = float(self.radius_entry.get()) if self.radius_entry.get() and self.radius_entry.get().replace('.','',1).isdigit() else None
            plot_graph_with_names(self.loaded_graph["G"], self.loaded_graph["nodes"], self.loaded_graph["ways"], self.loaded_graph["node_id_to_index"], self.loaded_graph["index_to_node_id"], depot_id=depot_id, service_radius_km=radius)

    def solve_vrp(self):
        if not self.check_data_loaded(): 
            return
        try:
            depot_id = int(self.depot_id_entry.get())
            radius = float(self.radius_entry.get()) if self.radius_entry.get() and self.radius_entry.get().replace('.','',1).isdigit() else None

            vehicles = [
                {'id': v[0], 'capacity': float(v[1]), 'speed_kmh': int(v[2])} 
                for v in (self.vehicles_tree.item(i, 'values') for i in self.vehicles_tree.get_children())
            ]

            customers = [
                {
                    'id': int(c[0]), 
                    'demand': float(c[1]), 
                    'time_window_start': self._time_str_to_seconds(c[2]), 
                    'time_window_end': self._time_str_to_seconds(c[3]), 
                    'service_time': int(c[4])
                } 
                for c in (self.customers_tree.item(i, 'values') for i in self.customers_tree.get_children())
            ]

            if not vehicles or not customers: 
                raise ValueError("É necessário ter ao menos um veículo e um cliente.")

            self.output_text.delete("1.0", tk.END)
            self.output_text.insert(tk.END, "Resolvendo o VRP... Isso pode demorar.\n\n")
            self.root.update_idletasks()

            # Chama o solver e trata retorno de 2 ou 3 valores
            result = solve_vrp_heuristic(
                self.loaded_graph["G"],
                self.loaded_graph["nodes"],
                self.loaded_graph["node_id_to_index"],
                self.loaded_graph["index_to_node_id"],
                depot_id,
                vehicles,
                customers
            )

            if len(result) == 3:
                routes, summary, distance_matrix = result
            else:
                routes, summary = result
                distance_matrix = None  # fallback caso não exista

            self.output_text.delete("1.0", tk.END)
            result_text = f"{summary}\n\n--- ROTAS GERADAS ---\n"

            if not routes: 
                result_text += "Nenhuma rota viável foi gerada."
            else:
                for v_id, data in routes.items():
                    departure_seconds = data.get('schedule', {}).get(depot_id, {}).get('departure', 0)
                    departure_time_str = self._seconds_to_time_str(departure_seconds)
                    distance_km = data.get('total_distance_meters', 0) / 1000
                    travel_time_str = self._seconds_to_time_str(data.get('total_travel_time_seconds', 0))
                    service_time_str = self._seconds_to_time_str(data.get('total_service_time_seconds', 0))
                    wait_time_str = self._seconds_to_time_str(data.get('total_wait_time_seconds', 0))
                    
                    result_text += f"\nVeículo: {v_id}\n"
                    result_text += f"  - Partida do Depósito: {departure_time_str} (HH:MM)\n"
                    result_text += f"  - Rota: {' -> '.join(map(str, data['route']))}\n"
                    result_text += f"  - Carga: {data['load']}\n"
                    result_text += f"  - Duração Total: {self._seconds_to_time_str(data['total_time_seconds'])} (HH:MM)\n"
                    result_text += f"  - Distância Total: {distance_km:.2f} km\n"
                    result_text += f"  - Tempo em Deslocamento: {travel_time_str} (HH:MM)\n"
                    result_text += f"  - Tempo em Serviço: {service_time_str} (HH:MM)\n"
                    result_text += f"  - Tempo Ocioso (Espera): {wait_time_str} (HH:MM)\n"

            self.output_text.insert(tk.END, result_text)

            if routes and distance_matrix:
                plot_vrp_routes(routes, depot_id, self.loaded_graph["nodes"], self.loaded_graph["ways"], distance_matrix, service_radius_km=radius)
            elif routes:
                plot_vrp_routes(routes, depot_id, self.loaded_graph["nodes"], self.loaded_graph["ways"], {}, service_radius_km=radius)

        except ValueError as ve: 
            messagebox.showerror("Erro de Valor", f"Erro nos dados de entrada: {ve}")
        except Exception as e: 
            messagebox.showerror("Erro Inesperado", f"Ocorreu um erro ao resolver o VRP: {e}")

    def populate_initial_vrp_data(self):
        """Popula a interface com dados de exemplo."""
        for i in self.vehicles_tree.get_children(): self.vehicles_tree.delete(i)
        for i in self.customers_tree.get_children(): self.customers_tree.delete(i)
        initial_vehicles = json.loads('[{"id": "Veiculo_A_Standard", "capacity": 100, "speed_kmh": 40}, {"id": "Veiculo_B_Grande", "capacity": 150, "speed_kmh": 50}]')
        initial_customers = json.loads('[{"id": 2863259711, "demand": 40, "time_window_start": 28800, "time_window_end": 32400, "service_time": 400},{"id": 8981058358, "demand": 50, "time_window_start": 31500, "time_window_end": 35100, "service_time": 600},{"id": 2033249141, "demand": 55, "time_window_start": 34200, "time_window_end": 37800, "service_time": 500},{"id": 3762462936, "demand": 30, "time_window_start": 50400, "time_window_end": 54000, "service_time": 300},{"id": 1964957765, "demand": 40, "time_window_start": 53100, "time_window_end": 56700, "service_time": 550},{"id": 616055065, "demand": 25, "time_window_start": 55800, "time_window_end": 59400, "service_time": 450}]')
        for v in initial_vehicles: self.vehicles_tree.insert("", "end", values=(v['id'], v['capacity'], v['speed_kmh']))
        for c in initial_customers: self.customers_tree.insert("", "end", values=(c['id'], c['demand'], self._seconds_to_time_str(c['time_window_start']), self._seconds_to_time_str(c['time_window_end']), c['service_time']))
    
    def add_vehicle(self):
        d = SimpleDialog(self.root, "Adicionar Veículo", [("ID do Veículo:", str), ("Capacidade:", float), ("Velocidade (km/h):", int)])
        if d.result: self.vehicles_tree.insert("", "end", values=d.result)
    
    def remove_vehicle(self):
        selected = self.vehicles_tree.selection();
        if selected: self.vehicles_tree.delete(selected)
    
    def add_customer(self):
        d = SimpleDialog(self.root, "Adicionar Cliente", [("ID do Nó:", int), ("Demanda:", float), ("Janela de Início (HH:MM):", str), ("Janela de Fim (HH:MM):", str), ("Tempo de Serviço (s):", int)])
        if d.result:
            try:
                self._time_str_to_seconds(d.result[2]); self._time_str_to_seconds(d.result[3])
                self.customers_tree.insert("", "end", values=d.result)
            except ValueError as e: messagebox.showerror("Erro de Formato", str(e))
    
    def remove_customer(self):
        selected = self.customers_tree.selection()
        if selected: self.customers_tree.delete(selected)
    
    def load_data(self):
        self.output_text.delete("1.0", tk.END); self.output_text.insert(tk.END, "Carregando dados do OpenStreetMap...\n"); self.root.update_idletasks()
        try:
            bbox = (float(self.south_entry.get()), float(self.west_entry.get()), float(self.north_entry.get()), float(self.east_entry.get()))
            data = get_osm_data(bbox); self.output_text.insert(tk.END, "Construindo o grafo com RustworkX...\n"); self.root.update_idletasks()
            G, nodes, vertices, ways, node_id_to_index, index_to_node_id = build_graph(data)
            self.loaded_graph.update({"G": G, "nodes": nodes, "vertices": vertices, "ways": ways, "node_id_to_index": node_id_to_index, "index_to_node_id": index_to_node_id})
            self.output_text.insert(tk.END, "Dados carregados e grafo construído com sucesso!\n"); return True
        except Exception as e:
            messagebox.showerror("Erro ao Carregar", f"Ocorreu um erro: {e}"); self.output_text.insert(tk.END, f"Erro ao carregar dados: {e}\n"); return False
    
    def check_data_loaded(self):
        if self.loaded_graph["G"] is None:
            if messagebox.askokcancel("Dados não carregados", "O grafo da cidade ainda não foi carregado. Deseja carregar agora?"): return self.load_data()
            return False
        return True
    
    def show_connections(self):
        if self.load_data():
            result = f"Total de vértices: {len(self.loaded_graph['vertices'])}\nTotal de arestas: {self.loaded_graph['G'].num_edges()}\nTotal de nós: {self.loaded_graph['G'].num_nodes()}\n\n"
            result += capture_print_crossings(limit=1000, **self.loaded_graph); self.output_text.delete("1.0", tk.END); self.output_text.insert(tk.END, result)
    
    def _run_pathfinding_algorithm(self, algorithm_func, name):
        if not self.check_data_loaded(): return
        try:
            start_id, end_id = int(self.start_id_entry.get()), int(self.end_id_entry.get()); path, distance, explored = (None, float('inf'), 0)
            if algorithm_func == astar:
                path, distance, explored = algorithm_func(self.loaded_graph["G"], start_id, end_id, self.loaded_graph["nodes"], self.loaded_graph["node_id_to_index"], self.loaded_graph["index_to_node_id"])
            else:
                path, distance = algorithm_func(self.loaded_graph["G"], start_id, end_id, self.loaded_graph["node_id_to_index"], self.loaded_graph["index_to_node_id"])
            self.output_text.delete("1.0", tk.END)
            if path:
                result = f"Caminho ({name}) de {start_id} para {end_id}:\n{' -> '.join(map(str, path))}\n\nDistância total: {distance:.2f} metros."
                if explored > 0: result += f"\nNós explorados: {explored}"
                self.output_text.insert(tk.END, result); plot_path_only(path, self.loaded_graph["nodes"], self.loaded_graph["ways"])
            else: self.output_text.insert(tk.END, f"Não foi possível encontrar um caminho entre {start_id} e {end_id}.")
        except ValueError: messagebox.showerror("Erro de Entrada", "IDs dos nós devem ser números inteiros.")
        except Exception as e: messagebox.showerror("Erro de Cálculo", f"Ocorreu um erro: {e}")
    
    def clear_cache(self):
        self.loaded_graph.update({k: None for k in self.loaded_graph}); self.output_text.delete("1.0", tk.END); self.output_text.insert(tk.END, "Cache limpo.")

class SimpleDialog(simpledialog.Dialog):
    def __init__(self, parent, title, fields):
        self.fields = fields; self.entries = {}; super().__init__(parent, title)
    def body(self, master):
        for i, (label, type_func) in enumerate(self.fields):
            ttk.Label(master, text=label).grid(row=i, sticky="w"); e = ttk.Entry(master); e.grid(row=i, column=1); self.entries[label] = (e, type_func)
        return self.entries[self.fields[0][0]][0]
    def apply(self):
        self.result = []
        try:
            for label, (entry, type_func) in self.entries.items(): self.result.append(type_func(entry.get()))
        except ValueError: messagebox.showerror("Erro de Tipo", f"Verifique o tipo de dado para '{label}'."); self.result = None

def run_app():
    root = tk.Tk(); app = OptiRotaApp(root); root.mainloop()