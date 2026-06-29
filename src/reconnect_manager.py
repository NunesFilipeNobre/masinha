# reconnect_manager.py
import threading
import time
import socket
import json

class ReconnectManager:
    def __init__(self, estado, roteador):
        self.estado = estado
        self.roteador = roteador
        self.rodando = True
        
        # Puxa o limite do config. Se não tiver, o padrão é 5.
        self.max_attempts = self.estado.config.get("max_reconnect_attempts", 5)
        
        # Dicionário para gerenciar a matemática do tempo:
        # peer_id -> {'tentativas': int, 'proxima': timestamp}
        self.backoff_tracking = {} 

    def iniciar(self):
        threading.Thread(target=self._rotina_reconexao, daemon=True).start()
        print(f"[RECONNECT] Motor de reconexão ativado (Max: {self.max_attempts} tentativas).")

    def _rotina_reconexao(self):
        while self.rodando:
            time.sleep(2) # Vare a tabela a cada 2 segundos
            agora = time.time()
            
            # Procura quem está morto (STALE)
            for peer_id, info in list(self.estado.tabela.conhecidos.items()):
                if info.get('status') in ['STALE', 'NEW']:
                    
                    # Se é a primeira vez que o vemos cair, inicia o cronômetro
                    if peer_id not in self.backoff_tracking:
                        self.backoff_tracking[peer_id] = {'tentativas': 0, 'proxima': agora}
                        
                    tracker = self.backoff_tracking[peer_id]
                    
                    # Chegou a hora de tentar de novo?
                    if agora >= tracker['proxima']:
                        tracker['tentativas'] += 1
                        
                        # Se passou do limite, desistimos de vez
                        if tracker['tentativas'] > self.max_attempts:
                            print(f"\n[RECONNECT] Limite atingido! {peer_id} marcado como DISCONNECTED.")
                            print("p2p> ", end="", flush=True)
                            info['status'] = 'DISCONNECTED'
                            del self.backoff_tracking[peer_id]
                            continue
                            
                        print(f"\n[RECONNECT] Tentativa {tracker['tentativas']}/{self.max_attempts} de reconectar com {peer_id}...")
                        print("p2p> ", end="", flush=True)
                        
                        sucesso = self._fazer_handshake(peer_id, info['ip'], info['port'])
                        
                        if sucesso:
                            print(f"\n[RECONNECT] Sucesso! Voltamos a falar com {peer_id}.")
                            print("p2p> ", end="", flush=True)
                            info['status'] = 'CONNECTED'
                            del self.backoff_tracking[peer_id]
                        else:
                            
                            tempo_espera = 2 ** tracker['tentativas']
                            tracker['proxima'] = agora + tempo_espera
                            print(f"[RECONNECT] Falhou. Próxima tentativa em {tempo_espera}s.")
                            print("p2p> ", end="", flush=True)

    def _fazer_handshake(self, peer_id, ip, porta):
        """Refaz o processo de HELLO isoladamente para reviver o TCP"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(3.0)
            sock.connect((ip, int(porta)))
            
            pacote_hello = {
               "type": "HELLO",
               "peer_id": self.estado.peer_id,
               "version": "1.0",
               "features": ["ack", "metrics"],
               "ttl": 1
            }
            sock.sendall((json.dumps(pacote_hello) + "\n").encode('utf-8'))
            
            # Já usando o limite de 32 KiB exigido pelo professor!
            resposta = sock.recv(32768) 
            
            if json.loads(resposta.decode('utf-8').strip()).get("type") == "HELLO_OK":
                sock.settimeout(None)
                self.estado.tabela.salvar_conexao(peer_id, sock)
                
                # Coloca a thread para escutar o cano revivido
                threading.Thread(
                    target=self._escutar_conexao, 
                    args=(sock, peer_id), 
                    daemon=True
                ).start()
                return True
            return False
        except Exception:
            return False

    def _escutar_conexao(self, socket_peer, peer_id):
        """Fica ouvindo o peer reconectado"""
        try:
            while self.rodando:
                dados = socket_peer.recv(32768)
                if not dados:
                    break
                
                linhas = dados.decode('utf-8').strip().split('\n')
                for linha in linhas:
                    if not linha: continue
                    self.roteador.processar_mensagem(json.loads(linha), socket_peer)
        except Exception:
            pass
        finally:
            # Se cair de novo no futuro, marca como STALE para reviver novamente
            if peer_id in self.estado.tabela.conhecidos:
                self.estado.tabela.conhecidos[peer_id]['status'] = 'STALE'