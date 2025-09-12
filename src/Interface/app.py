import tkinter as tk
from tkinter import messagebox, scrolledtext
from io import StringIO
import sys

from src.OSM.consultaOSM import get_osm_data, print_crossings
from src.Grafo.build import build_graph
from src.Grafo.visualizar import plot_graph_with_names

def capture_print_crossings(G, nodes, vertices, ways, limit=20):
    buffer = StringIO()
    sys_stdout = sys.stdout
    sys.stdout = buffer
    try:
        print_crossings(G, nodes, vertices, ways, limit)
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

    # Variáveis para armazenar dados carregados
    loaded_graph = {"G": None, "nodes": None, "vertices": None, "ways": None}

    def load_data():
        """Carrega dados OSM e constrói o grafo"""
        bbox = (
            float(south_entry.get()),
            float(west_entry.get()),
            float(north_entry.get()),
            float(east_entry.get())
        )
        data = get_osm_data(bbox)
        G, nodes, vertices, ways = build_graph(data)
        loaded_graph.update({"G": G, "nodes": nodes, "vertices": vertices, "ways": ways})
        return G, nodes, vertices, ways

    def show_connections():
        try:
            G, nodes, vertices, ways = load_data()
            result = f"Total de vértices (cruzamentos reais): {len(vertices)}\n"
            result += f"Total de arestas: {G.number_of_edges()}\n\n"
            result += capture_print_crossings(G, nodes, vertices, ways, limit=20)

            output_text.delete("1.0", tk.END)
            output_text.insert(tk.END, result)

        except Exception as e:
            output_text.delete("1.0", tk.END)
            output_text.insert(tk.END, "Entrada inválida")

    def show_graph():
        try:
            if loaded_graph["G"] is None:
                G, nodes, vertices, ways = load_data()
            else:
                G, nodes, vertices, ways = (
                    loaded_graph["G"],
                    loaded_graph["nodes"],
                    loaded_graph["vertices"],
                    loaded_graph["ways"],
                )
            plot_graph_with_names(G, nodes, ways)

        except Exception as e:
            output_text.delete("1.0", tk.END)
            output_text.insert(tk.END, "Erro ao gerar grafo")

    # Botões separados
    tk.Button(frame, text="Mostrar Conexões", command=show_connections).grid(row=4, column=0, pady=10, sticky="ew")
    tk.Button(frame, text="Mostrar Grafo", command=show_graph).grid(row=4, column=1, pady=10, sticky="ew")

    root.mainloop()
