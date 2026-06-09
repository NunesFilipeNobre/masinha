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

    def enviar_mensagem(self, peer_id_destino, texto_mensagem):
        # 1. Verifica se já temos uma conexão aberta com essa pessoa
        sock = self.estado.tabela.obter_conexao(peer_id_destino)
        
        # Se NÃO temos a conexão, criamos ela e fazemos o Handshake
        if not sock:
            info_peer = self.estado.tabela.obter_info(peer_id_destino)
            if not info_peer:
                print(f"[CLIENT] Peer {peer_id_destino} não encontrado na Tabela.")
                return False
                
            ip_destino = info_peer['ip']
            porta_destino = int(info_peer['port'])
            
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.connect((ip_destino, porta_destino))
                
                # Handshake HELLO
                pacote_hello = {
                   "type": "HELLO",
                   "peer_id": self.estado.peer_id,
                   "version": "1.0",
                   "features": ["ack", "metrics"],
                   "ttl": 1
                }
                sock.sendall((json.dumps(pacote_hello) + "\n").encode('utf-8'))
                
                # Espera HELLO_OK
                resposta = sock.recv(4096)
                if json.loads(resposta.decode('utf-8').strip()).get("type") == "HELLO_OK":
                    # DEU CERTO! Salva a conexão para nunca mais fechar
                    self.estado.tabela.salvar_conexao(peer_id_destino, sock)
                    print(f"[CLIENT] Conexão persistente criada com {peer_id_destino}!")
                    
                    # Cria uma thread para ficar lendo o que ele responder depois 
                    # (já que a conexão não vai fechar, alguém precisa escutar ela)
                    threading.Thread(
                        target=self._lidar_com_cliente, 
                        args=(sock, (ip_destino, porta_destino)), 
                        daemon=True
                    ).start()
                else:
                    return False
            except Exception as e:
                print(f"[CLIENT] Erro ao conectar com {peer_id_destino}: {e}")
                return False

        # 2. Agora que temos o "cano" aberto garantido, só disparamos a mensagem SEND
        try:
            msg_id = str(uuid.uuid4())
            pacote_send = {
                "type": "SEND",
                "msg_id": msg_id,
                "src": self.estado.peer_id,
                "dst": peer_id_destino,
                "payload": texto_mensagem,
                "require_ack": True,
                "ttl": 1
            }
            sock.sendall((json.dumps(pacote_send) + "\n").encode('utf-8'))
            return True
        except Exception as e:
            print(f"[CLIENT] Erro ao enviar mensagem no socket aberto: {e}")
            self.estado.tabela.conhecidos[peer_id_destino]['status'] = "STALE"
            return False