import heapq

class FilaPrioridade:
    def __init__(self):
        self.fila = []
    
    def inserir(self, prioridade, item):
        # Insere um item na fila de prioridade com sua prioridade
        heapq.heappush(self.fila, (prioridade, item))
    
    def remover(self):
        # Remove o item com a menor prioridade (o primeiro na fila)
        if self.fila:
            return heapq.heappop(self.fila)[1]
        else:
            return None
    
    def tamanho(self):
        return len(self.fila)

