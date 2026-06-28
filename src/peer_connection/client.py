# peer_connection/client.py
import socket
import threading
import json
import uuid
import time

class PeerClient:
    def __init__(self, estado, roteador):
        self.estado = estado
        self.roteador = roteador
        self.rodando = True
        # Inicia a thread que vigia os 5 segundos do ACK
        threading.Thread(target=self._vigiar_timeouts, daemon=True).start()
    
    def _vigiar_timeouts(self):
        """Fica varrendo a memória para ver se alguma mensagem atrasou > 5s"""
        from datetime import datetime
        while self.rodando:
            time.sleep(1)
            agora = time.time()
            
            for msg_id, info in list(self.estado.tabela.ack_tracking.items()):
                if agora - info['timestamp'] > 5.0:
                    ts = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    print(f"\n[{ts}] [Router] TIMEOUT: Sem ACK de {info['dst']} após 5 segundos.")
                    print("p2p> ", end="", flush=True)
                    # Apaga para não avisar duas vezes
                    del self.estado.tabela.ack_tracking[msg_id]

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
            
            # --- O CRONÔMETRO DE 5 SEGUNDOS ENTRA AQUI ---
            # Anotamos a hora exata antes do pacote sair para a rede
            self.estado.tabela.ack_tracking[msg_id] = {
                "timestamp": time.time(),
                "dst": peer_id_destino
            }
            # ----------------------------------------------
            
            sock.sendall((json.dumps(pacote_send) + "\n").encode('utf-8'))
            return True
        except Exception as e:
            print(f"[CLIENT] O cano morreu inesperadamente: {e}")
            self.estado.tabela.conhecidos[peer_id_destino]['status'] = "STALE"
            
            # Se o socket quebrou na hora de enviar, a gente remove a contagem do timeout
            if msg_id in self.estado.tabela.ack_tracking:
                del self.estado.tabela.ack_tracking[msg_id]
                
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
            # Silenciado para não sujar o log quando a conexão cai de propósito
            pass