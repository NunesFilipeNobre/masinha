# main.py
from rendezvous_connection import registrar, descobrir
from state import NodeState
from peer_connection import PeerConnectionManager
from cli import CLI # <-- Adicione a importação do CLI
import time

def main():
    print("--- Iniciando Nó P2P ---")
    estado = NodeState()

    conexao_p2p = PeerConnectionManager(porta_local=estado.minha_porta)
    conexao_p2p.iniciar_servidor()

    registrar(meu_nome=estado.meu_nome, meu_namespace=estado.meu_namespace, minha_porta=estado.minha_porta)
    time.sleep(1) 

    lista_de_peers = descobrir(meu_namespace=estado.meu_namespace)
    if lista_de_peers:
        estado.atualizar_peers(lista_de_peers)

    # --- INICIAR A INTERFACE ---
    # Isso vai prender o programa no loop do terminal, impedindo que ele feche!
    terminal = CLI(estado, conexao_p2p)
    terminal.iniciar()

if __name__ == "__main__":
    main()