import heapq

class FilaPrioridade:
    def __init__(self):
        self.fila = []
    
    def inserir(self, prioridade, item):
     
        heapq.heappush(self.fila, (prioridade, item))
    
    def remover(self):
      
        if self.fila:
            return heapq.heappop(self.fila)[1]
        else:
            return None
    
    def tamanho(self):
        return len(self.fila)


