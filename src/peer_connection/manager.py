
#peer_connection/manager.py
import json
import uuid
from .server import PeerServer
from .client import PeerClient
from .broadcast import PeerBroadcaster

with open("config.json", "r") as f:
    config = json.load(f)
    
# Classe que gerencia as conexões P2P, incluindo envio de mensagens, broadcast e encerramento de conexões.
class PeerConnectionManager:
    def __init__(self, estado, roteador):
        self.estado = estado
        self.roteador = roteador
        
        # Instancia os sub-módulos
        self.server = PeerServer(estado, roteador)
        self.client = PeerClient(estado, roteador)
        self.broadcaster = PeerBroadcaster(estado)
        
        self.rodando = True

    def iniciar_servidor(self):
        # Repassa para o módulo de servidor
        self.server.iniciar()

    def enviar_mensagem(self, destino, texto_mensagem):
        # Repassa para o módulo de cliente
        return self.client.enviar_mensagem(destino, texto_mensagem)

    def enviar_pub(self, destino, texto_mensagem):
        # Repassa para o módulo de broadcast
        self.broadcaster.enviar_pub(destino, texto_mensagem)

    def encerrar_todas_conexoes(self):
        """Envia BYE para todos os peers ativos antes de fechar o programa"""
        # Desliga as flags de laço infinito dos submódulos
        self.rodando = False
        self.server.rodando = False
        self.client.rodando = False
        
        conexoes_ativas = list(self.estado.tabela.conexoes.items())
        
        for peer_id, sock in conexoes_ativas:
            try:
                msg_id = str(uuid.uuid4())
                pacote_bye = {
                    "type": "BYE",
                    "msg_id": msg_id,
                    "src": self.estado.peer_id,
                    "dst": peer_id,
                    "reason": "Encerrando nó P2P",
                    "ttl": config.get("fixed_msg_ttl",1)
                }
                sock.sendall((json.dumps(pacote_bye) + "\n").encode('utf-8'))
                print(f"[SHUTDOWN] BYE enviado para {peer_id}")
            except Exception:
                pass
            
            # Fecha o socket localmente para liberar a porta do sistema operacional
            try:
                sock.close()
            except:
                pass
                
        self.estado.tabela.conexoes.clear()