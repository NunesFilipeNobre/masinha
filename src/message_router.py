# message_router.py
import json
from datetime import datetime, timezone

with open("config.json", "r") as f:
    config = json.load(f)
    
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
        agora = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        print(f"\n[{agora}] [Router] MENSAGEM DE {remetente}: {texto}")
        print("p2p> ", end="", flush=True)
        print(f"\n[MENSAGEM DE {remetente}]: {texto}")
        print("p2p> ", end="", flush=True)
        
        if pacote.get("require_ack"):
            ack = {
                "type": "ACK",
                "msg_id": pacote.get("msg_id"),
                "timestamp": datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ'),
                "ttl": config.get("fixed_msg_ttl",1)
            }
            try:
                socket_cliente.sendall((json.dumps(ack) + "\n").encode('utf-8'))
            except Exception as e:
                print(f"\n[ROUTER] Erro ao enviar ACK: {e}")

    def _lidar_com_ack(self, pacote):
        msg_id = pacote.get("msg_id")
        
        # NOVO: O ACK chegou a tempo! Apagamos da tabela do vigia
        if msg_id in self.estado.tabela.ack_tracking:
            del self.estado.tabela.ack_tracking[msg_id]
            
        agora = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        if self.estado.log_level == "DEBUG":
            print(f"\n[{agora}] [Router] Mensagem entregue com sucesso! (ACK recebido)")
            print("p2p> ", end="", flush=True)

    def _lidar_com_ping(self, pacote, socket_cliente):
        """Devolve um PONG imediatamente ao receber um PING"""
        pong = {
            "type": "PONG",
            "msg_id": pacote.get("msg_id"),
            "timestamp": datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ'),
            "ttl": config.get("fixed_msg_ttl",1)
        }
        try:
            socket_cliente.sendall((json.dumps(pong) + "\n").encode('utf-8'))
        except Exception:
            pass

    def _lidar_com_pong(self, pacote):
        """Avisa que o peer está vivo e calcula a latência (RTT)"""
        import time
        msg_id = pacote.get("msg_id")
        
        # Verifica se nós enviamos esse PING
        if msg_id in self.estado.tabela.ping_tracking:
            peer_id, tempo_envio = self.estado.tabela.ping_tracking.pop(msg_id)
            rtt_ms = (time.time() - tempo_envio) * 1000 # Converte pra milissegundos
            
            # Puxa o cadastro do peer para guardar o histórico
            info_peer = self.estado.tabela.conhecidos.get(peer_id)
            if info_peer:
                # Usa .setdefault para criar a lista 'rtts' se não existir
                lista_rtts = info_peer.setdefault('rtts', [])
                lista_rtts.append(rtt_ms)
                info_peer['rtts'] = lista_rtts[-5:] # Mantém só os últimos 5 para a média
            
            print(f"\n[KEEP-ALIVE] PONG de {peer_id} | RTT: {rtt_ms:.2f} ms")
        else:
            print(f"\n[KEEP-ALIVE] PONG recebido, mas origem desconhecida.")
            
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
            "ttl": config.get("fixed_msg_ttl",1)
        }
        try:
            socket_cliente.sendall((json.dumps(bye_ok) + "\n").encode('utf-8'))
        except Exception:
            pass
            
        # 1. Limpa o status na tabela de peers
        if remetente in self.estado.tabela.conhecidos:
            self.estado.tabela.conhecidos[remetente]['status'] = 'DISCONNECTED'
            
        # 2. ARRANCAMOS O CANO DA LISTA DE ATIVOS 
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