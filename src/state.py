import json
import sys
from peer_table import PeerTable

class NodeState:
    def __init__(self):
        #Carrega os dados de forma dinâmica
        try:
            with open("config.json", "r") as f:
                self.config = json.load(f)
        except FileNotFoundError:
            print("[ERRO FATAL] Arquivo config.json não encontrado. Crie o arquivo na raiz do projeto.")
            sys.exit(1)

        self.meu_nome = self.config.get("name", "anonimo")
        self.meu_namespace = self.config.get("namespace", "UnB")
        self.minha_porta = self.config.get("port", 4005)
        self.meu_ttl = self.config.get("ttl", 3600)
        
        self.log_level = self.config.get("log_level", "INFO")

        self._validar_formatos()
        self.tabela = PeerTable(self.peer_id)
        self.tabela.ack_tracking = {} 

    def _validar_formatos(self):
        """Garante que os dados respeitam os tipos e limites da especificação"""
        erros = []
        
        if not isinstance(self.meu_namespace, str) or len(self.meu_namespace) > 64:
            erros.append("O campo 'namespace' deve ser uma string com até 64 caracteres.")
            
        if not isinstance(self.meu_nome, str) or len(self.meu_nome) > 64:
            erros.append("O campo 'name' deve ser uma string com até 64 caracteres.")
            
        if type(self.minha_porta) is not int or not (1 <= self.minha_porta <= 65535):
            erros.append("O campo 'port' deve ser um número inteiro entre 1 e 65535.")
            
        if type(self.meu_ttl) is not int or not (1 <= self.meu_ttl <= 86400):
            erros.append("O campo 'ttl' deve ser um número inteiro entre 1 e 86400.")

        if erros:
            print("\n[FALHA DE VALIDAÇÃO] Encontramos erros no seu config.json:")
            for erro in erros:
                print(f" -> {erro}")
            print("Por favor, corrija o arquivo e reinicie o nó P2P.")
            sys.exit(1)

    @property
    def peer_id(self):
        return f"{self.meu_nome}@{self.meu_namespace}"

    def atualizar_peers(self, lista_peers):
        self.tabela.registrar_da_rede(lista_peers)
        total = len(self.tabela.conhecidos)
        
        if self.log_level == "DEBUG":
            print(f"[STATE] Tabela atualizada! Conheço {total} peers externos.")