# p2p_client.py
import time
from rendezvous_connection import registrar, descobrir, desregistrar
from peer_connection import PeerConnectionManager
from CLI.cli import CLI
from message_router import MessageRouter
from keep_alive import KeepAliveManager
from reconnect_manager import ReconnectManager

class P2PClient:
    def __init__(self, estado):
        self.estado = estado
        
        # Cria o roteador primeiro
        self.roteador = MessageRouter(self.estado)
        
        # Passa o roteador para a conexão
        self.conexao_p2p = PeerConnectionManager(self.estado, self.roteador)
        
        self.keep_alive = KeepAliveManager(self.estado)
        self.reconnect_manager = ReconnectManager(self.estado, self.roteador)
        self.terminal = CLI(self.estado, self)

    def iniciar(self):
        """Orquestra o boot do nó P2P"""
        # Sobe o servidor local para ouvir conexões
        self.conexao_p2p.iniciar_servidor()

        # Registra no randezvous e descobre peers
        sucesso_registro = registrar(
            meu_nome=self.estado.meu_nome, 
            meu_namespace=self.estado.meu_namespace, 
            minha_porta=self.estado.minha_porta
        )
        
        if not sucesso_registro:
            print("[Client] Falha ao registrar no Rendezvous. Encerrando.")
            return

        time.sleep(1)

        # Popula a memória inicial
        self.atualizar_rede()

        # Trava o programa no loop da Interface
        self.keep_alive.iniciar()
        self.reconnect_manager.iniciar()
        self.terminal.iniciar()

    def atualizar_rede(self):
        """Encapsula a lógica de descoberta para ser chamada a qualquer momento"""
        lista_de_peers = descobrir(meu_namespace=self.estado.meu_namespace)
        if lista_de_peers:
            self.estado.atualizar_peers(lista_de_peers)
            
    def parar(self):
        """Desliga o sistema graciosamente"""
        print("\n[Client] Iniciando protocolo de encerramento...")
        self.conexao_p2p.rodando = False
        self.keep_alive.rodando = False
        self.reconnect_manager.rodando = False
        
        # Manda o BYE para os amigos e fecha os sockets
        self.conexao_p2p.encerrar_todas_conexoes()
        
        # Avisa o rendezvous que estamos saindo
        desregistrar(self.estado.meu_nome, self.estado.meu_namespace)