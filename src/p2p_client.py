import time
import threading
from rendezvous_connection import registrar, descobrir, desregistrar
from peer_connection.manager import PeerConnectionManager
from CLI.cli import CLI
from message_router import MessageRouter
from keep_alive import KeepAliveManager
from reconnect_manager import ReconnectManager

import json

with open("config.json", "r") as f:
    config = json.load(f)

class P2PClient:
    def __init__(self, estado):
        self.estado = estado
        self.roteador = MessageRouter(self.estado)
        self.conexao_p2p = PeerConnectionManager(self.estado, self.roteador)
        self.keep_alive = KeepAliveManager(self.estado)
        self.reconnect_manager = ReconnectManager(self.estado, self.roteador)
        self.terminal = CLI(self.estado, self)

    def iniciar(self):
        """Orquestra o boot do nó P2P"""
        self.conexao_p2p.iniciar_servidor()

        sucesso_registro = registrar(
            meu_nome=self.estado.meu_nome, 
            meu_namespace=self.estado.meu_namespace, 
            minha_porta=self.estado.minha_porta,
            meu_ttl=self.estado.meu_ttl
        )
        
        if not sucesso_registro:
            print("[Client] Falha ao registrar no Rendezvous. Encerrando.")
            return

        time.sleep(1)
        self.atualizar_rede()

        
        # Inicia o renovo do TTL e puxa peers novos automaticamente
        threading.Thread(target=self._rotina_rendezvous, daemon=True).start()

        self.keep_alive.iniciar()
        self.reconnect_manager.iniciar()
        self.terminal.iniciar()

    def _rotina_rendezvous(self):
        """Robô de segundo plano para manter o nó sempre atualizado e vivo no professor"""
        tempo_ultimo_registro = time.time()
        intervalo_discover = config["discover_interval"]  
        metade_ttl = self.estado.meu_ttl / 2  # Renova o registro na metade da vida útil

        while self.conexao_p2p.rodando:
            time.sleep(intervalo_discover)
            
            # silencioso se o sistema n estiver em DEBUG
            modo_silencioso = (self.estado.log_level != "DEBUG")
            
            # DISCOVER Recorrente
            lista_de_peers = descobrir(meu_namespace=self.estado.meu_namespace, silencioso=modo_silencioso)
            if lista_de_peers:
                self.estado.atualizar_peers(lista_de_peers)

            # REGISTER Recorrente 
            agora = time.time()
            if agora - tempo_ultimo_registro >= metade_ttl:
                registrar(
                    meu_nome=self.estado.meu_nome,
                    meu_namespace=self.estado.meu_namespace,
                    minha_porta=self.estado.minha_porta,
                    meu_ttl=self.estado.meu_ttl,
                    silencioso=modo_silencioso 
                )
                tempo_ultimo_registro = agora

    def atualizar_rede(self):
        """Versão manual chamada pelo /listar"""
        lista_de_peers = descobrir(meu_namespace=self.estado.meu_namespace, silencioso=False)
        if lista_de_peers:
            self.estado.atualizar_peers(lista_de_peers)
            
    def parar(self):
        """Desliga o sistema graciosamente"""
        print("\n[Client] Iniciando protocolo de encerramento...")
        self.conexao_p2p.rodando = False
        self.keep_alive.rodando = False
        self.reconnect_manager.rodando = False
        
        self.conexao_p2p.encerrar_todas_conexoes()
        desregistrar(self.estado.meu_nome, self.estado.meu_namespace)