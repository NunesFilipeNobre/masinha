# reconnect_manager.py
import threading
import time

class ReconnectManager:
    def __init__(self, estado, conexao_p2p):
        self.estado = estado
        self.conexao_p2p = conexao_p2p
        self.rodando = True
        # O número máximo de tentativas exigido pelo professor
        self.max_tentativas = 5 

    def iniciar(self):
        t = threading.Thread(target=self._rotina_reconexao, daemon=True)
        t.start()
        print("[RECONNECT] Motor de reconexão automática em backoff ativado.")

    def _rotina_reconexao(self):
        while self.rodando:
            time.sleep(2) # Verifica a tabela a cada 2 segundos
            agora = time.time()
            
            # Varre os contatos buscando os caídos ('STALE')
            for peer_id, info in list(self.estado.tabela.conhecidos.items()):
                if info.get('status') == 'STALE':
                    tentativas = info.get('tentativas', 0)
                    proxima = info.get('proxima_tentativa', 0)
                    
                    if tentativas < self.max_tentativas:
                        # Se já deu o tempo de espera exponencial, tenta de novo
                        if agora >= proxima:
                            print(f"\n[RECONNECT] Tentando reviver {peer_id} (Tentativa {tentativas + 1}/{self.max_tentativas})...")
                            print("p2p> ", end="", flush=True)
                            
                            # Usa a função limpa que acabamos de criar no client!
                            sucesso = self.conexao_p2p.client.conectar_silencioso(peer_id)
                            
                            if sucesso:
                                print(f"\n[RECONNECT] Sucesso! Conexão com {peer_id} restaurada.")
                                info['status'] = 'CONNECTED'
                                info['tentativas'] = 0 # Zera o contador
                            else:
                                info['tentativas'] = tentativas + 1
                                espera = 2 ** info['tentativas'] # Matemática: 2, 4, 8, 16, 32...
                                info['proxima_tentativa'] = time.time() + espera
                                print(f"\n[RECONNECT] Falha. Nova tentativa em {espera}s.")
                            
                            print("p2p> ", end="", flush=True)
                    else:
                        # Se tentou 5 vezes e falhou, desiste de vez.
                        if tentativas == self.max_tentativas:
                            print(f"\n[RECONNECT] Limite atingido para {peer_id}. Marcando como DISCONNECTED.")
                            info['status'] = 'DISCONNECTED'
                            info['tentativas'] = 6 # Trava para não imprimir mais
                            print("p2p> ", end="", flush=True)