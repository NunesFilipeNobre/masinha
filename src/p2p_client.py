# p2p_client.py
import time
from rendezvous_connection import registrar, descobrir
from peer_connection import PeerConnectionManager
from cli import CLI
from message_router import MessageRouter

class P2PClient:
    def __init__(self, estado):
        self.estado = estado
        
        # 1. Cria o roteador primeiro
        self.roteador = MessageRouter(self.estado)
        
        # 2. Passa o roteador para a conexão
        self.conexao_p2p = PeerConnectionManager(self.estado, self.roteador)
        
        self.terminal = CLI(self.estado, self)

    def iniciar(self):
        """Orquestra o boot do nó P2P"""
        # 1. Sobe o servidor local para ouvir conexões
        self.conexao_p2p.iniciar_servidor()

        # 2. Registra no professor
        sucesso_registro = registrar(
            meu_nome=self.estado.meu_nome, 
            meu_namespace=self.estado.meu_namespace, 
            minha_porta=self.estado.minha_porta
        )
        
        if not sucesso_registro:
            print("[Client] Falha ao registrar no Rendezvous. Encerrando.")
            return

        time.sleep(1)

        # 3. Popula a memória inicial
        self.atualizar_rede()

        # 4. Trava o programa no loop da Interface
        self.terminal.iniciar()

    def atualizar_rede(self):
        """Encapsula a lógica de descoberta para ser chamada a qualquer momento"""
        lista_de_peers = descobrir(meu_namespace=self.estado.meu_namespace)
        if lista_de_peers:
            self.estado.atualizar_peers(lista_de_peers)
            
    def parar(self):
        """Desliga o sistema graciosamente"""
        self.conexao_p2p.rodando = False
        # Futuramente: enviar BYE para os peers conectados aqui