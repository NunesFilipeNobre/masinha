# peer_connection.py
import socket
import threading
import json
import uuid

class PeerConnectionManager:
    def __init__(self, estado, roteador):
        self.estado = estado
        self.roteador = roteador
        self.porta_local = int(estado.minha_porta)
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
                        self.roteador.processar_mensagem(pacote, socket_cliente)
                                
            except Exception as e:
                print(f"[SERVER] Erro na conversa com {ip_peer}: {e}")
                
        print(f"\n[SERVER] Conexão encerrada com {ip_peer}")
        print("p2p> ", end="", flush=True)

    def _escutar_conexao_persistente(self, socket_peer, endereco):
        """Ouve mensagens em uma conexão que já passou pelo Handshake"""
        ip_peer, porta_peer = endereco
        try:
            while self.rodando:
                dados = socket_peer.recv(4096)
                if not dados:
                    break # Conexão caiu
                
                linhas = dados.decode('utf-8').strip().split('\n')
                for linha in linhas:
                    if not linha: continue
                    pacote = json.loads(linha)
                    
                    self.roteador.processar_mensagem(pacote, socket_peer)
        except Exception as e:
            print(f"\n[CLIENT] Conexão persistente interrompida com {ip_peer}: {e}")
            print("p2p> ", end="", flush=True)

    def enviar_mensagem(self, peer_id_destino, texto_mensagem):
        # 1. Verifica se já temos uma conexão aberta e saudável
        sock = self.estado.tabela.obter_conexao(peer_id_destino)
        
        # Se NÃO temos a conexão, criamos uma nova DO ZERO
        if not sock:
            info_peer = self.estado.tabela.obter_info(peer_id_destino)
            if not info_peer:
                print(f"[CLIENT] Peer {peer_id_destino} não encontrado na Tabela.")
                return False
                
            ip_destino = info_peer['ip']
            porta_destino = int(info_peer['port'])
            
           
            
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(5.0)
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
                    # DEU CERTO! Salva a conexão
                    self.estado.tabela.salvar_conexao(peer_id_destino, sock)
                    print(f"[CLIENT] Conexão persistente criada com {peer_id_destino}!")
                    
                    # Cria a thread pra escutar sem pedir HELLO de novo
                    threading.Thread(
                        target=self._escutar_conexao_persistente, 
                        args=(sock, (ip_destino, porta_destino)), 
                        daemon=True
                    ).start()
                else:
                    return False
            except Exception as e:
                print(f"[CLIENT] Erro ao conectar com {peer_id_destino}: {e}")
                return False

        # 2. Agora o cano está garantido e aberto! Mandamos o SEND.
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
            print(f"[CLIENT] O cano morreu inesperadamente: {e}")
            self.estado.tabela.conhecidos[peer_id_destino]['status'] = "STALE"
            return False