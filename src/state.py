# state.py

class NodeState:
    def __init__(self):
        # Aqui você guarda quem você é
        self.meu_nome = "alice"
        self.meu_namespace = "UnB"
        self.minha_porta = 4000
        
        # Aqui é onde vamos salvar a lista que vem do servidor
        self.peers_conhecidos = []

    def atualizar_peers(self, lista_peers):
        """Recebe uma nova lista de peers e salva na memória"""
        self.peers_conhecidos = lista_peers
        print(f"[STATE] Memória atualizada! Agora conheço {len(self.peers_conhecidos)} peers.")

    def obter_peers(self):
        """Retorna a lista salva para quem pedir"""
        return self.peers_conhecidos