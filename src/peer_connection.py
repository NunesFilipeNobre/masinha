# peer_connection.py
import socket
import threading
import json
import uuid

class PeerConnectionManager:
    def __init__(self, estado, roteador):
        self.estado = estado
        self.roteador = roteador # <-- Recebemos o roteador injetado aqui
        self.porta_local = estado.minha_porta
        self.rodando = True

    def iniciar_servidor(self):
        thread_servidor = threading.Thread(target=self._executar_servidor, daemon=True)
        thread_servidor.start()
        print(f"[SERVER] Servidor TCP P2P iniciado na porta {self.porta_local}")

    def _executar_servidor(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as servidor:
            servidor.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            try:
                servidor.bind(('0.0.0.0', self.porta_local))
                servidor.listen()
                
                while self.rodando:
                    socket_cliente, endereco = servidor.accept()
                    thread_conversa = threading.Thread(
                        target=self._lidar_com_cliente, 
                        args=(socket_cliente, endereco), 
                        daemon=True
                    )
                    thread_conversa.start()
            except Exception as e:
                if self.rodando:
                    print(f"[SERVER] Erro crítico no servidor local: {e}")

    def _lidar_com_cliente(self, socket_cliente, endereco):
        ip_peer, porta_peer = endereco
        print(f"\n[SERVER] Nova conexão de {ip_peer}")
        print("p2p> ", end="", flush=True)
        
        with socket_cliente:
            try:
                # 1. Fase de Handshake (HELLO)
                dados_iniciais = socket_cliente.recv(4096)
                if not dados_iniciais: return
                msg_hello = json.loads(dados_iniciais.decode('utf-8').strip())
                
                if msg_hello.get("type") == "HELLO":
                    peer_remetente = msg_hello.get("peer_id", "Desconhecido")
                    
                    resposta_ok = {
                       "type": "HELLO_OK",
                       "peer_id": self.estado.peer_id,
                       "version": "1.0",
                       "features": ["ack", "metrics"],
                       "ttl": 1
                    }
                    socket_cliente.sendall((json.dumps(resposta_ok) + "\n").encode('utf-8'))
                else:
                    return

                # 2. Fase de Chat (Encaminha tudo para o Roteador)
                while self.rodando:
                    dados_chat = socket_cliente.recv(4096)
                    if not dados_chat:
                        break 
                        
                    linhas = dados_chat.decode('utf-8').strip().split('\n')
                    for linha in linhas:
                        if not linha: continue
                        pacote = json.loads(linha)
                        
                        # O Socket não sabe mais o que é SEND ou ACK. O roteador decide.
                        self.roteador.processar_mensagem(pacote, socket_cliente)
                                
            except Exception as e:
                print(f"[SERVER] Erro na conversa com {ip_peer}: {e}")
                
        print(f"\n[SERVER] Conexão encerrada com {ip_peer}")
        print("p2p> ", end="", flush=True)

    def enviar_mensagem(self, ip_destino, porta_destino, texto_mensagem):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(5.0)
            s.connect((ip_destino, int(porta_destino)))
            
            # 1. Handshake HELLO
            pacote_hello = {
               "type": "HELLO",
               "peer_id": self.estado.peer_id,
               "version": "1.0",
               "features": ["ack", "metrics"],
               "ttl": 1
            }
            s.sendall((json.dumps(pacote_hello) + "\n").encode('utf-8'))
            
            # 2. HELLO_OK
            resposta_bruta = s.recv(4096)
            resposta_json = json.loads(resposta_bruta.decode('utf-8').strip())
            
            if resposta_json.get("type") == "HELLO_OK":
                peer_destino = resposta_json.get("peer_id")
                
                # 3. Manda a mensagem SEND
                msg_id = str(uuid.uuid4())
                pacote_send = {
                    "type": "SEND",
                    "msg_id": msg_id,
                    "src": self.estado.peer_id,
                    "dst": peer_destino,
                    "payload": texto_mensagem,
                    "require_ack": True,
                    "ttl": 1
                }
                s.sendall((json.dumps(pacote_send) + "\n").encode('utf-8'))
                
                # 4. Recebe o ACK e joga para o Roteador ler e validar
                resposta_ack_bruta = s.recv(4096)
                if resposta_ack_bruta:
                    msg_ack = json.loads(resposta_ack_bruta.decode('utf-8').strip())
                    self.roteador.processar_mensagem(msg_ack, s)
                
            s.close()
            return True
            
        except Exception as e:
            print(f"[CLIENT] Erro ao enviar mensagem para {ip_destino}:{porta_destino} -> {e}")
            return False