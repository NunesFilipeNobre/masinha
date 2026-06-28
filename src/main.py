# main.py
from state import NodeState
from p2p_client import P2PClient

def main():
    print("--- Inicializando Aplicação P2P ---")
    
    #Cria a memória base
    estado = NodeState()
    
   
    cliente = P2PClient(estado)
    
    
    cliente.iniciar()

if __name__ == "__main__":
    main()