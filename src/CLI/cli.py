# CLI/cli.py
from .iniciar import iniciar

class CLI:
    def __init__(self, estado, cliente_p2p):
        self.estado = estado
        self.cliente_p2p = cliente_p2p

    def iniciar(self):
        return iniciar(self)