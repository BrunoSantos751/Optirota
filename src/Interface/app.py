import tkinter as tk
from tkinter import messagebox, scrolledtext
from io import StringIO
import sys
from src.OSM.consultaOSM import get_osm_data, print_crossings
from src.Grafo.build import build_graph
from src.Grafo.visualizar import plot_graph_with_names

def capture_print_crossings(G, nodes, vertices, ways, node_id_to_index, index_to_node_id, limit=20):
    """
    Captura a saída da função print_crossings adaptada para RustworkX
    """
    buffer = StringIO()
    sys_stdout = sys.stdout
    sys.stdout = buffer
    try:
        print_crossings(G, nodes, vertices, ways, node_id_to_index, index_to_node_id, limit)
    finally:
        sys.stdout = sys_stdout
    return buffer.getvalue()

def run_app():
    root = tk.Tk()
    root.title("OptiRota - Interface OSM")
    
    # Responsividade
    root.geometry("800x400")
    root.columnconfigure(0, weight=1)
    root.rowconfigure(0, weight=1)
    
    # Frame principal
    frame = tk.Frame(root, padx=10, pady=10)
    frame.grid(sticky="nsew")
    frame.columnconfigure(1, weight=1)
    
    # Inputs
    tk.Label(frame, text="Sul (lat min):").grid(row=0, column=0, sticky="w")
    south_entry = tk.Entry(frame)
    south_entry.grid(row=0, column=1, sticky="ew")
    south_entry.insert(0, "-9.659998")
    
    tk.Label(frame, text="Oeste (lon min):").grid(row=1, column=0, sticky="w")
    west_entry = tk.Entry(frame)
    west_entry.grid(row=1, column=1, sticky="ew")
    west_entry.insert(0, "-35.708648")
    
    tk.Label(frame, text="Norte (lat max):").grid(row=2, column=0, sticky="w")
    north_entry = tk.Entry(frame)
    north_entry.grid(row=2, column=1, sticky="ew")
    north_entry.insert(0, "-9.657515")
    
    tk.Label(frame, text="Leste (lon max):").grid(row=3, column=0, sticky="w")
    east_entry = tk.Entry(frame)
    east_entry.grid(row=3, column=1, sticky="ew")
    east_entry.insert(0, "-35.704620")
    
    # Saída de resultados
    output_text = tk.Text(frame, wrap="word")
    output_text.grid(row=6, column=0, columnspan=2, sticky="nsew", pady=10)
    frame.rowconfigure(6, weight=1)
    
    # Variáveis para armazenar dados carregados (adaptado para RustworkX)
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
        
        # build_graph agora retorna também os mapeamentos
        G, nodes, vertices, ways, node_id_to_index, index_to_node_id = build_graph(data)
        
        # Atualizar dados carregados
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
            
            # Informações do grafo adaptadas para RustworkX
            result = f"Total de vértices (cruzamentos reais): {len(vertices)}\n"
            result += f"Total de arestas: {G.num_edges()}\n"  # RustworkX usa num_edges() ao invés de number_of_edges()
            result += f"Total de nós no grafo: {G.num_nodes()}\n\n"
            
            # Capturar saída da função print_crossings adaptada
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
            # Verificar se já temos dados carregados
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
            
            # Chamar função de visualização (precisará ser adaptada também)
            plot_graph_with_names(
                G, nodes, ways, 
                node_id_to_index, index_to_node_id
            )
            
        except Exception as e:
            output_text.delete("1.0", tk.END)
            output_text.insert(tk.END, f"Erro ao gerar grafo: {str(e)}")

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
    button_frame.grid(row=4, column=0, columnspan=2, pady=10, sticky="ew")
    button_frame.columnconfigure(0, weight=1)
    button_frame.columnconfigure(1, weight=1)

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


    # Botão adicional para limpar cache
    tk.Button(
        button_frame, 
        text="Limpar Cache", 
        command=clear_cache
    ).grid(row=1, column=0, columnspan=2, pady=5, sticky="ew")
    
    # Barra de status
    status_frame = tk.Frame(frame)
    status_frame.grid(row=7, column=0, columnspan=2, sticky="ew")
    
    status_label = tk.Label(status_frame, text="Pronto - Digite as coordenadas e clique em 'Mostrar Conexões'", relief=tk.SUNKEN, anchor=tk.W)
    status_label.pack(fill=tk.X)
    
    root.mainloop()

# Função auxiliar para compatibilidade
def get_graph_info_rustworkx(G):
    """
    Função auxiliar para obter informações do grafo RustworkX
    de forma compatível com o código existente
    """
    return {
        'num_nodes': G.num_nodes(),
        'num_edges': G.num_edges(),
        'node_indices': list(G.node_indices()),
        'edge_indices': list(G.edge_indices())
    }

if __name__ == "__main__":
    run_app()