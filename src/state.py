# state.py

from peer_table import PeerTable

class NodeState:
    def __init__(self):
<<<<<<< HEAD
        # Aqui você guarda quem você é
        self.meu_nome = "malario"
        self.meu_namespace = "UnB"
        self.minha_porta = 4005
=======
        self.meu_nome = "Apple1"      # Troque para "bob" no outro PC
        self.meu_namespace = "UnB"
        self.minha_porta = 4008      
>>>>>>> 492a482a1f639e4c4222d955bcfe057e101a99c1
        
        # A Tabela assume o controle!
        self.tabela = PeerTable(self.peer_id)

    @property
    def peer_id(self):
        return f"{self.meu_nome}@{self.meu_namespace}"

    def atualizar_peers(self, lista_peers):
        self.tabela.registrar_da_rede(lista_peers)
        total = len(self.tabela.conhecidos)
        print(f"[STATE] Tabela atualizada! Conheço {total} peers externos.")