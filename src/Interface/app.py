import tkinter as tk
from tkinter import messagebox, scrolledtext
from io import StringIO
import sys
from src.OSM.consultaOSM import get_osm_data
from src.Grafo.build import build_graph
from src.Grafo.visualizar import plot_graph_with_names, plot_path_only
from src.Algoritimos.dijkstra import dijkstra

def capture_print_crossings(G, nodes, vertices, ways, node_id_to_index, index_to_node_id, limit=20):
    """
    Captura a saída da função print_crossings adaptada para RustworkX
    """
    buffer = StringIO()
    sys_stdout = sys.stdout
    sys.stdout = buffer
    try:
        from src.OSM.consultaOSM import print_crossings
        print_crossings(G, nodes, vertices, ways, node_id_to_index, index_to_node_id, limit)
    finally:
        sys.stdout = sys_stdout
    return buffer.getvalue()

def run_app():
    root = tk.Tk()
    root.title("OptiRota - Interface OSM")
    
    # Responsividade
    root.geometry("800x600")
    root.columnconfigure(0, weight=1)
    root.rowconfigure(0, weight=1)
    
    # Frame principal
    frame = tk.Frame(root, padx=10, pady=10)
    frame.grid(sticky="nsew")
    frame.columnconfigure(1, weight=1)
    
    # Inputs da Bounding Box
    tk.Label(frame, text="Sul (lat min):").grid(row=0, column=0, sticky="w")
    south_entry = tk.Entry(frame)
    south_entry.grid(row=0, column=1, sticky="ew")
    south_entry.insert(0, "-9.67107")
    
    tk.Label(frame, text="Oeste (lon min):").grid(row=1, column=0, sticky="w")
    west_entry = tk.Entry(frame)
    west_entry.grid(row=1, column=1, sticky="ew")
    west_entry.insert(0, "-35.73166")
    
    tk.Label(frame, text="Norte (lat max):").grid(row=2, column=0, sticky="w")
    north_entry = tk.Entry(frame)
    north_entry.grid(row=2, column=1, sticky="ew")
    north_entry.insert(0, "-9.63134")
    
    tk.Label(frame, text="Leste (lon max):").grid(row=3, column=0, sticky="w")
    east_entry = tk.Entry(frame)
    east_entry.grid(row=3, column=1, sticky="ew")
    east_entry.insert(0, "-35.66720")

    # Inputs para o Dijkstra
    tk.Label(frame, text="Nó de Origem (ID):").grid(row=4, column=0, sticky="w", pady=(10, 0))
    start_id_entry = tk.Entry(frame)
    start_id_entry.grid(row=4, column=1, sticky="ew", pady=(10, 0))
    start_id_entry.insert(0, "432674688") # Exemplo
    
    tk.Label(frame, text="Nó de Destino (ID):").grid(row=5, column=0, sticky="w")
    end_id_entry = tk.Entry(frame)
    end_id_entry.grid(row=5, column=1, sticky="ew")
    end_id_entry.insert(0, "7044690950") # Exemplo
    
    # Saída de resultados
    output_text = scrolledtext.ScrolledText(frame, wrap="word")
    output_text.grid(row=8, column=0, columnspan=2, sticky="nsew", pady=10)
    frame.rowconfigure(8, weight=1)
    
    # Variáveis para armazenar dados carregados
    loaded_graph = {
        "G": None, 
        "nodes": None, 
        "vertices": None, 
        "ways": None,
        "node_id_to_index": None,
        "index_to_node_id": None
    }
    
    def load_data():
        """Carrega dados OSM e constrói o grafo usando RustworkX"""
        bbox = (
            float(south_entry.get()),
            float(west_entry.get()),
            float(north_entry.get()),
            float(east_entry.get())
        )
        
        data = get_osm_data(bbox)
        
        G, nodes, vertices, ways, node_id_to_index, index_to_node_id = build_graph(data)
        
        loaded_graph.update({
            "G": G, 
            "nodes": nodes, 
            "vertices": vertices, 
            "ways": ways,
            "node_id_to_index": node_id_to_index,
            "index_to_node_id": index_to_node_id
        })
        
        return G, nodes, vertices, ways, node_id_to_index, index_to_node_id
    
    def show_connections():
        """Mostra as conexões do grafo RustworkX"""
        try:
            G, nodes, vertices, ways, node_id_to_index, index_to_node_id = load_data()
            
            result = f"Total de vértices (cruzamentos reais): {len(vertices)}\n"
            result += f"Total de arestas: {G.num_edges()}\n"
            result += f"Total de nós no grafo: {G.num_nodes()}\n\n"
            
            result += capture_print_crossings(
                G, nodes, vertices, ways, 
                node_id_to_index, index_to_node_id, 
                limit=20
            )
            
            output_text.delete("1.0", tk.END)
            output_text.insert(tk.END, result)
            
        except ValueError as ve:
            output_text.delete("1.0", tk.END)
            output_text.insert(tk.END, f"Erro nos valores de entrada: {str(ve)}")
        except Exception as e:
            output_text.delete("1.0", tk.END)
            output_text.insert(tk.END, f"Erro ao carregar dados: {str(e)}")
    
    def show_graph():
        """Exibe o grafo visualmente"""
        try:
            if loaded_graph["G"] is None:
                G, nodes, vertices, ways, node_id_to_index, index_to_node_id = load_data()
            else:
                G, nodes, vertices, ways = (
                    loaded_graph["G"],
                    loaded_graph["nodes"],
                    loaded_graph["vertices"],
                    loaded_graph["ways"],
                )
                node_id_to_index = loaded_graph["node_id_to_index"]
                index_to_node_id = loaded_graph["index_to_node_id"]
            
            plot_graph_with_names(G, nodes, ways, node_id_to_index, index_to_node_id)
            
        except Exception as e:
            output_text.delete("1.0", tk.END)
            output_text.insert(tk.END, f"Erro ao gerar grafo: {str(e)}")
    
    def get_graph_statistics():
        """Função adicional para mostrar estatísticas detalhadas do grafo"""
        try:
            if loaded_graph["G"] is None:
                output_text.delete("1.0", tk.END)
                output_text.insert(tk.END, "Carregue os dados primeiro usando 'Mostrar Conexões'")
                return
            
            G = loaded_graph["G"]
            vertices = loaded_graph["vertices"]
            
            stats = f"=== ESTATÍSTICAS DO GRAFO ===\n"
            stats += f"Nós: {G.num_nodes()}\n"
            stats += f"Arestas: {G.num_edges()}\n"
            stats += f"Vértices (cruzamentos): {len(vertices)}\n"
            
            try:
                components = len(list(G.connected_components())) if hasattr(G, 'connected_components') else "N/A"
                stats += f"Componentes conectados: {components}\n"
            except:
                stats += f"Componentes conectados: Não disponível para grafos direcionados\n"
            
            if G.num_nodes() > 0:
                total_degree = sum(len(G.out_edges(node_idx)) + len(G.in_edges(node_idx)) for node_idx in G.node_indices())
                avg_degree = total_degree / (2 * G.num_nodes())
                stats += f"Grau médio: {avg_degree:.2f}\n"
            
            output_text.delete("1.0", tk.END)
            output_text.insert(tk.END, stats)
            
        except Exception as e:
            output_text.delete("1.0", tk.END)
            output_text.insert(tk.END, f"Erro ao calcular estatísticas: {str(e)}")

    # ... (código anterior)

    def find_shortest_path():
        """Função para encontrar o menor caminho usando Dijkstra e plotá-lo"""
        try:
            if loaded_graph["G"] is None:
                output_text.delete("1.0", tk.END)
                output_text.insert(tk.END, "Carregue os dados primeiro usando 'Mostrar Conexões'")
                return
            
            start_id = int(start_id_entry.get())
            end_id = int(end_id_entry.get())
            
            path, distance = dijkstra(
                loaded_graph["G"],
                start_id,
                end_id,
                loaded_graph["node_id_to_index"],
                loaded_graph["index_to_node_id"]
            )
            
            output_text.delete("1.0", tk.END)
            if path:
                result = f"Caminho encontrado de {start_id} para {end_id}:\n"
                result += " -> ".join(map(str, path))
                result += f"\n\nDistância total: {distance:.2f} metros."
                output_text.insert(tk.END, result)
                plot_path_only(path, loaded_graph["nodes"], loaded_graph["ways"])
            
            else:
                output_text.insert(tk.END, f"Não foi possível encontrar um caminho entre {start_id} e {end_id}.")
                
        except ValueError:
            output_text.delete("1.0", tk.END)
            output_text.insert(tk.END, "Erro: Certifique-se de que os IDs dos nós são números inteiros válidos.")
        except Exception as e:
            output_text.delete("1.0", tk.END)
            output_text.insert(tk.END, f"Erro ao calcular o caminho: {str(e)}")
    
    def clear_cache():
        """Limpa o cache de dados carregados"""
        loaded_graph.update({
            "G": None, 
            "nodes": None, 
            "vertices": None, 
            "ways": None,
            "node_id_to_index": None,
            "index_to_node_id": None
        })
        output_text.delete("1.0", tk.END)
        output_text.insert(tk.END, "Cache limpo. Próxima operação recarregará os dados.")
    
    # Layout dos botões em grid
    button_frame = tk.Frame(frame)
    button_frame.grid(row=6, column=0, columnspan=2, pady=10, sticky="ew")
    button_frame.columnconfigure(0, weight=1)
    button_frame.columnconfigure(1, weight=1)
    button_frame.columnconfigure(2, weight=1)
    
    # Botões principais
    tk.Button(
        button_frame, 
        text="Mostrar Conexões", 
        command=show_connections
    ).grid(row=0, column=0, padx=5, sticky="ew")
    
    tk.Button(
        button_frame, 
        text="Mostrar Grafo", 
        command=show_graph
    ).grid(row=0, column=1, padx=5, sticky="ew")
    
    tk.Button(
        button_frame, 
        text="Estatísticas", 
        command=get_graph_statistics
    ).grid(row=0, column=2, padx=5, sticky="ew")
    

    tk.Button(
        button_frame,
        text="Calcular Menor Caminho",
        command=find_shortest_path
    ).grid(row=1, column=0, columnspan=2, padx=5, pady=(10, 0), sticky="ew")
    

    tk.Button(
        button_frame, 
        text="Limpar Cache", 
        command=clear_cache
    ).grid(row=1, column=2, padx=5, pady=(10, 0), sticky="ew")
    

    status_frame = tk.Frame(frame)
    status_frame.grid(row=7, column=0, columnspan=2, sticky="ew")
    
    status_label = tk.Label(status_frame, text="Pronto - Digite as coordenadas e clique em 'Mostrar Conexões'", relief=tk.SUNKEN, anchor=tk.W)
    status_label.pack(fill=tk.X)
    
    root.mainloop()

# Função auxiliar para compatibilidade
def get_graph_info_rustworkx(G):
    return {
        'num_nodes': G.num_nodes(),
        'num_edges': G.num_edges(),
        'node_indices': list(G.node_indices()),
        'edge_indices': list(G.edge_indices())
    }

if __name__ == "__main__":
    run_app()