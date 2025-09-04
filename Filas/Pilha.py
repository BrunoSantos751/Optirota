class Pilha:
    def __init__(self):
        self.pilha = []
    
    def empilhar(self, item):
        self.pilha.append(item)  # Empilha um item
    
    def desempilhar(self):
        if self.pilha:
            return self.pilha.pop()  # Desempilha o último item
        else:
            return None
    
    def tamanho(self):
        return len(self.pilha)
    
    def exibir_pilha(self):
        return list(reversed(self.pilha))  # Exibe a pilha do topo para a base
    
    def esta_vazia(self):
        return len(self.pilha) == 0
