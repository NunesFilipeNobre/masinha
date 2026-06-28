
#peer_connection/server.py
import socket
import threading
import json

class PeerServer:
    def __init__(self, estado, roteador):
        self.estado = estado
        self.roteador = roteador
        self.porta_local = int(estado.minha_porta)
        self.rodando = True

    def iniciar(self):
        thread_servidor = threading.Thread(target=self._executar_servidor, daemon=True)
        thread_servidor.start()
        print(f"[SERVER] Servidor TCP P2P iniciado na porta {self.porta_local}")
    #function _executar_servidor cria um socket TCP, vincula-o à porta local e entra em um loop para aceitar conexões de entrada. Para cada conexão aceita, ele cria uma nova thread que chama a função _lidar_com_cliente para gerenciar a comunicação com o peer conectado.
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
            socket_cliente.settimeout(None)
            try:
                #  Fase de Handshake (HELLO)
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
                    self.estado.tabela.salvar_conexao(peer_remetente, socket_cliente)
                else:
                    return

                # Fase de Chat (Encaminha tudo para o Roteador)
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