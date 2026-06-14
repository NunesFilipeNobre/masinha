#peer_connection/broadcast.py

import json
import uuid

class PeerBroadcaster:
    def __init__(self, estado):
        self.estado = estado

    def enviar_pub(self, destino, texto_mensagem):
        """Dispara um pacote PUB para os canos TCP que já estão abertos"""
        msg_id = str(uuid.uuid4())
        pacote_pub = {
            "type": "PUB",
            "msg_id": msg_id,
            "src": self.estado.peer_id,
            "dst": destino,
            "payload": texto_mensagem,
            "require_ack": False,  # PUB nunca pede ACK de acordo com a especificação
            "ttl": 1
        }
        json_pub = (json.dumps(pacote_pub) + "\n").encode('utf-8')
        enviados = 0

        # Vasculha todos os peers conhecidos na tabela
        for peer_id, info in list(self.estado.tabela.conhecidos.items()):
            
            # Lógica de Namespace-cast do professor (ex: se destino for #UnB)
            if destino.startswith("#"):
                ns_alvo = destino[1:] # Tira a hashtag para sobrar só 'UnB'
                # Se o peer_id (ex: bob@CIC) não termina com '@UnB', pula ele
                if not peer_id.endswith(f"@{ns_alvo}"):
                    continue

            # Tenta pegar a conexão. O PUB só vai para quem já tem cano aberto!
            sock = self.estado.tabela.obter_conexao(peer_id)
            if sock:
                try:
                    sock.sendall(json_pub)
                    enviados += 1
                except Exception as e:
                    print(f"\n[PUB] Erro ao enviar para {peer_id}: {e}")
                    self.estado.tabela.conhecidos[peer_id]['status'] = 'STALE'
                    
        print(f"[CLIENT] Broadcast disparado para {enviados} peer(s) ativo(s).")