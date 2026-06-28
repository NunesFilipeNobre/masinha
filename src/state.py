# state.py

import json

from peer_table import PeerTable

class NodeState:
    def __init__(self):
        # Aqui você guarda quem você é
        self.meu_nome = "sonze"
        self.meu_namespace = "UnB"
        self.minha_porta = 4005
        
        # A Tabela assume o controle!
        self.tabela = PeerTable(self.peer_id)

    # NOVO: Dicionário para rastrear os 5 segundos do SEND
        self.tabela.ack_tracking = {} 

        # NOVO: Carregar arquivo de configuração
        try:
            with open("config.json", "r") as f:
                self.config = json.load(f)
        except FileNotFoundError:
            self.config = {"keep_alive_interval": 30, "log_level": "INFO"}
            
        self.log_level = self.config.get("log_level", "INFO")
    @property
    def peer_id(self):
        return f"{self.meu_nome}@{self.meu_namespace}"

    def atualizar_peers(self, lista_peers):
        self.tabela.registrar_da_rede(lista_peers)
        total = len(self.tabela.conhecidos)
        print(f"[STATE] Tabela atualizada! Conheço {total} peers externos.")