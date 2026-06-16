# peer_connection/client.py
import socket
import threading
import json
import uuid

class PeerClient:
    def __init__(self, estado, roteador):
        self.estado = estado
        self.roteador = roteador
        self.rodando = True

    def conectar_silencioso(self, peer_id_destino):
        """Apenas abre a conexão TCP persistente e faz o Handshake"""
        sock = self.estado.tabela.obter_conexao(peer_id_destino)
        if sock: return True # Já está conectado
            
        info_peer = self.estado.tabela.obter_info(peer_id_destino)
        if not info_peer: return False
                
        ip_destino = info_peer['ip']
        porta_destino = int(info_peer['port'])

        # --- HACK BLINDADO PARA TESTE LOCAL ---
        ip_destino = '127.0.0.1' 
        # --------------------------------------
        
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(5.0)
            sock.connect((ip_destino, porta_destino))
            
            pacote_hello = {
               "type": "HELLO",
               "peer_id": self.estado.peer_id,
               "version": "1.0",
               "features": ["ack", "metrics"],
               "ttl": 1
            }
            sock.sendall((json.dumps(pacote_hello) + "\n").encode('utf-8'))
            
            resposta = sock.recv(4096)
            if json.loads(resposta.decode('utf-8').strip()).get("type") == "HELLO_OK":
                sock.settimeout(None)
                self.estado.tabela.salvar_conexao(peer_id_destino, sock)
                
                threading.Thread(
                    target=self._escutar_conexao_persistente, 
                    args=(sock, (ip_destino, porta_destino)), 
                    daemon=True
                ).start()
                return True
            return False
        except Exception as e:
            print(f"[DEBUG] Falha de socket com {peer_id_destino}: {e}")
            if peer_id_destino in self.estado.tabela.conhecidos:
                self.estado.tabela.conhecidos[peer_id_destino]['status'] = 'STALE'
            return False

    def enviar_mensagem(self, peer_id_destino, texto_mensagem):
        # 1. Tenta garantir que o cano está aberto usando a função nova
        if not self.conectar_silencioso(peer_id_destino):
            print(f"[CLIENT] Falha ao conectar com {peer_id_destino}.")
            return False

        # 2. Com o cano garantido, apenas atiramos o SEND
        sock = self.estado.tabela.obter_conexao(peer_id_destino)
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
        ip_peer, porta_peer = endereco
        try:
            while self.rodando:
                dados = socket_peer.recv(4096)
                if not dados: break 
                
                linhas = dados.decode('utf-8').strip().split('\n')
                for linha in linhas:
                    if not linha: continue
                    self.roteador.processar_mensagem(json.loads(linha), socket_peer)
        except Exception as e:
            # Não precisamos mais do print assustador aqui, a reconexão vai cuidar disso
            pass