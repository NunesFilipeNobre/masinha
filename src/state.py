# state.py

from peer_table import PeerTable

class NodeState:
    def __init__(self):
        # Aqui você guarda quem você é
        self.meu_nome = "malario"
        self.meu_namespace = "UnB"
        self.minha_porta = 4005
        
        # A Tabela assume o controle!
        self.tabela = PeerTable(self.peer_id)

    @property
    def peer_id(self):
        return f"{self.meu_nome}@{self.meu_namespace}"

    def atualizar_peers(self, lista_peers):
        self.tabela.registrar_da_rede(lista_peers)
        total = len(self.tabela.conhecidos)
        print(f"[STATE] Tabela atualizada! Conheço {total} peers externos.")