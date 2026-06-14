# message_router.py
import json
from datetime import datetime, timezone

class MessageRouter:
    def __init__(self, estado):
        self.estado = estado

    def processar_mensagem(self, pacote, socket_cliente):
        tipo = pacote.get("type")

        if tipo == "SEND":
            self._lidar_com_send(pacote, socket_cliente)
        elif tipo == "ACK":
            self._lidar_com_ack(pacote)
        elif tipo == "PING":
            self._lidar_com_ping(pacote, socket_cliente)
        elif tipo == "PONG":
            self._lidar_com_pong(pacote)
        elif tipo == "PUB": 
            self._lidar_com_pub(pacote)
        elif tipo == "BYE":       
            self._lidar_com_bye(pacote, socket_cliente)
        elif tipo == "BYE_OK":    
            self._lidar_com_bye_ok(pacote)
        else:
            print(f"\n[ROUTER] Pacote '{tipo}' ignorado.")
            print("p2p> ", end="", flush=True)

    def _lidar_com_send(self, pacote, socket_cliente):
        remetente = pacote.get("src", "Desconhecido")
        texto = pacote.get("payload", "")
        
        print(f"\n[MENSAGEM DE {remetente}]: {texto}")
        print("p2p> ", end="", flush=True)
        
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
                print(f"\n[ROUTER] Erro ao enviar ACK: {e}")

    def _lidar_com_ack(self, pacote):
        print(f"\n[CLIENT] Mensagem entregue com sucesso! (ACK recebido)")
        print("p2p> ", end="", flush=True)

    def _lidar_com_ping(self, pacote, socket_cliente):
        """Devolve um PONG imediatamente ao receber um PING"""
        pong = {
            "type": "PONG",
            "msg_id": pacote.get("msg_id"),
            "timestamp": datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ'),
            "ttl": 1
        }
        try:
            socket_cliente.sendall((json.dumps(pong) + "\n").encode('utf-8'))
        except Exception:
            pass

    def _lidar_com_pong(self, pacote):
        """Avisa que o peer está vivo (Opcional: implementar cálculo de latência aqui depois)"""
        print(f"\n[KEEP-ALIVE] PONG recebido! Conexão saudável.")
        print("p2p> ", end="", flush=True)
    
    def _lidar_com_pub(self, pacote):
        """Lê um broadcast e imprime na tela sem exigir ACK"""
        remetente = pacote.get("src", "Desconhecido")
        destino = pacote.get("dst", "*")
        texto = pacote.get("payload", "")
        
        # Formata bonitinho para o usuário saber que foi um grito público
        print(f"\n[BROADCAST de {remetente} -> {destino}]: {texto}")
        print("p2p> ", end="", flush=True)
    def _lidar_com_bye(self, pacote, socket_cliente):
        """Alguém está saindo. Devolvemos um BYE_OK e fechamos a conexão."""
        remetente = pacote.get("src", "Desconhecido")
        print(f"\n[SESSÃO] {remetente} encerrou a conexão graciosamente.")
        print("p2p> ", end="", flush=True)
        
        # O documento exige enviar um BYE_OK de volta antes de fechar a porta
        bye_ok = {
            "type": "BYE_OK",
            "msg_id": pacote.get("msg_id"),
            "src": self.estado.peer_id,
            "dst": remetente,
            "ttl": 1
        }
        try:
            socket_cliente.sendall((json.dumps(bye_ok) + "\n").encode('utf-8'))
        except Exception:
            pass
            
        # 1. Limpa o status na tabela de peers
        if remetente in self.estado.tabela.conhecidos:
            self.estado.tabela.conhecidos[remetente]['status'] = 'DISCONNECTED'
            
        # 2. ARRANCAMOS O CANO DA LISTA DE ATIVOS (Para o PING parar)
        if remetente in self.estado.tabela.conexoes:
            del self.estado.tabela.conexoes[remetente]
            
        # 3. Mandamos o Windows fechar a porta localmente
        try:
            socket_cliente.close()
        except:
            pass

    def _lidar_com_bye_ok(self, pacote):
        """Confirmação de que o amigo aceitou o nosso tchau."""
        remetente = pacote.get("src", "Desconhecido")
        print(f"\n[SESSÃO] {remetente} confirmou o encerramento (BYE_OK).")
        print("p2p> ", end="", flush=True)