
#peer_connection/client.py
import socket
import threading
import json
import uuid

class PeerClient:
    def __init__(self, estado, roteador):
        self.estado = estado
        self.roteador = roteador
        self.rodando = True

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

            #teste ne 
            #ip_destino = '127.0.0.1' 
            print(f"[DEBUG] Atirando localmente em: {ip_destino}:{porta_destino}")
            ######
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
                    sock.settimeout(None)

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