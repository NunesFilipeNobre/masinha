# main.py

#INTEGRANTES DO GRUPO 3:
#Filipe Nobre Nunes	242023523
#Guilherme Silva Cavalcante	 242001508
#Rafael Mileo Moreira Krauss Guimarães 242024763
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