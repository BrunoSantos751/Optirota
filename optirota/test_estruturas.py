import timeit 
from Filas.Fila_Simples import FilaSimples
from Filas.Fila_Prioridade import FilaPrioridade
from Filas.Pilha import Pilha

def testar_fila_simples():
    print("\n=== Teste Fila Simples ===")
    fila = FilaSimples()
    fila.inserir("A")
    fila.inserir("B")
    fila.inserir("C")
    print("Fila após inserções:", fila.exibir_fila())
    print("Removido:", fila.remover())
    print("Fila atual:", fila.exibir_fila())
    print("Está vazia?", fila.esta_vazia())

def testar_fila_prioridade():
    print("\n=== Teste Fila de Prioridade ===")
    fila = FilaPrioridade()
    fila.inserir(2, "Tarefa média")
    fila.inserir(1, "Tarefa urgente")
    fila.inserir(3, "Tarefa baixa prioridade")
    print("Tamanho da fila:", fila.tamanho())
    print("Removido (mais urgente):", fila.remover())
    print("Removido (próxima):", fila.remover())

def testar_pilha():
    print("\n=== Teste Pilha ===")
    pilha = Pilha()
    pilha.empilhar("X")
    pilha.empilhar("Y")
    pilha.empilhar("Z")
    print("Pilha atual:", pilha.exibir_pilha())
    print("Desempilhado:", pilha.desempilhar())
    print("Pilha após desempilhar:", pilha.exibir_pilha())
    print("Está vazia?", pilha.esta_vazia())

def meu_codigo():
    for i in range(1000000):
        pass


if __name__ == "__main__":
    testar_fila_simples()
    testar_fila_prioridade()
    testar_pilha()

tempo = timeit.timeit(meu_codigo, number=1)
print(f"Tempo de execução: {tempo:.5f} segundos")
