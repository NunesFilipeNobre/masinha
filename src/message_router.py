# message_router.py
import json
from datetime import datetime, timezone

class MessageRouter:
    def __init__(self, estado):
        self.estado = estado

    def processar_mensagem(self, pacote, socket_cliente):
        """Lê o dicionário JSON e distribui para a função correta"""
        tipo = pacote.get("type")

        if tipo == "SEND":
            self._lidar_com_send(pacote, socket_cliente)
        elif tipo == "ACK":
            self._lidar_com_ack(pacote)
        else:
            print(f"\n[ROUTER] Pacote '{tipo}' recebido, mas ainda não implementado no roteador.")
            print("p2p> ", end="", flush=True)

    def _lidar_com_send(self, pacote, socket_cliente):
        """Exibe a mensagem na tela e devolve um ACK se solicitado"""
        remetente = pacote.get("src", "Desconhecido")
        texto = pacote.get("payload", "")
        
        print(f"\n[MENSAGEM DE {remetente}]: {texto}")
        print("p2p> ", end="", flush=True) # Arruma o cursor do CLI na tela
        
        if pacote.get("require_ack"):
            ack = {
                "type": "ACK",
                "msg_id": pacote.get("msg_id"),
                "timestamp": datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ'),
                "ttl": 1
            }
            try:
                socket_cliente.sendall((json.dumps(ack) + "\n").encode('utf-8'))
            except Exception as e:
                print(f"\n[ROUTER] Erro ao enviar ACK de volta: {e}")

    def _lidar_com_ack(self, pacote):
        """Avisa que a mensagem que você enviou foi lida"""
        print(f"\n[CLIENT] Mensagem entregue com sucesso! (ACK recebido)")
        print("p2p> ", end="", flush=True)