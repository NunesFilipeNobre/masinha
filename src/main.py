# main.py
from state import NodeState
from p2p_client import P2PClient

def main():
    print("--- Inicializando Aplicação P2P ---")
    
    # 1. Cria a memória base
    estado = NodeState()
    
    # 2. Cria o cérebro da aplicação
    cliente = P2PClient(estado)
    
    # 3. Dá a partida
    cliente.iniciar()

if __name__ == "__main__":
    main()