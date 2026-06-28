#Fica enviando PING e recebendo PONG pra manter a conexão viva

# keep_alive.py
import threading
import time
import json
import uuid
from datetime import datetime, timezone

class KeepAliveManager:
    def __init__(self, estado):
        self.estado = estado
        self.rodando = True
        #self.intervalo_segundos = 30
        self.intervalo_segundos = self.estado.config.get("keep_alive_interval", 30)

    def iniciar(self):
        t = threading.Thread(target=self._rotina_ping, daemon=True)
        t.start()
        print(f"[KEEP-ALIVE] Monitoramento iniciado (PING a cada {self.intervalo_segundos}s).")

    def _rotina_ping(self):
        while self.rodando:
            time.sleep(self.intervalo_segundos)
            
            # Fazemos uma cópia da lista para evitar erros se alguém desconectar no meio do loop
            conexoes_ativas = list(self.estado.tabela.conexoes.items())
            
            for peer_id, sock in conexoes_ativas:
                try:
                    msg_id_unico = str(uuid.uuid4())
                    pacote_ping = {
                        "type": "PING",
                        "msg_id": msg_id_unico,
                        "timestamp": datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ'),
                        "ttl": 1
                    }
                    self.estado.tabela.ping_tracking[msg_id_unico] = (peer_id, time.time())
                    sock.sendall((json.dumps(pacote_ping) + "\n").encode('utf-8'))
                    # Debug sutil só pra gente ver que enviou
                    print(f"\n[KEEP-ALIVE] PING enviado para {peer_id}")
                    print("p2p> ", end="", flush=True)
                except Exception as e:
                    print(f"\n[KEEP-ALIVE] Falha ao pingar {peer_id}: {e}")
                    self.estado.tabela.conhecidos[peer_id]['status'] = 'STALE'
                    print("p2p> ", end="", flush=True)