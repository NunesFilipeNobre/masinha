# state.py

class NodeState:
    def __init__(self):
        self.meu_nome = "alice"      # Lembre de mudar para "bob" no pc do seu amigo
        self.meu_namespace = "UnB"
        self.minha_porta = 4002      # A porta que você configurou
        
        self.peers_conhecidos = []

    @property
    def peer_id(self):
        """Gera automaticamente a identidade completa exigida pelo protocolo"""
        return f"{self.meu_nome}@{self.meu_namespace}"

    def atualizar_peers(self, lista_peers):
        self.peers_conhecidos = lista_peers
        print(f"[STATE] Memória atualizada! Agora conheço {len(self.peers_conhecidos)} peers.")

    def obter_peers(self):
        return self.peers_conhecidos