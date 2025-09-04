from collections import deque

class FilaSimples:
    def __init__(self):
        self.fila = deque()
    
    def inserir(self, item):
        self.fila.append(item)  # Enfileira um item
    
    def remover(self):
        if self.fila:
            return self.fila.popleft()  # Desenfileira o primeiro item
        else:
            return None
    
    def tamanho(self):
        return len(self.fila)
    
    def exibir_fila(self):
        return list(self.fila)  # Exibe todos os itens na fila
    
    def esta_vazia(self):
        return len(self.fila) == 0
