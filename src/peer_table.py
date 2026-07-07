#Controle de estado e gerencia reconexão com peers conhecidos na table

# peer_table.py

class PeerTable:
    def __init__(self, meu_peer_id):
        self.meu_peer_id = meu_peer_id
        self.conhecidos = {}  # Dicionário: peer_id -> {ip, port, status}
        self.conexoes = {}    # Dicionário: peer_id -> Objeto de Socket TCP ativo
        self.ping_tracking = {} # Mapeia: msg_id -> (peer_id, timestamp_de_envio)

    def registrar_da_rede(self, dados_rendezvous):
        """Pega a lista do professor e cadastra quem a gente não conhece"""
        
        # 1. Extrai a lista real que está dentro da chave 'peers'
        if isinstance(dados_rendezvous, dict):
            lista_peers = dados_rendezvous.get('peers', [])
        else:
            lista_peers = dados_rendezvous 

       
        for p in lista_peers:
            nome = p.get('name')
            ns = p.get('namespace')
            if not nome or not ns: continue
            
            pid = f"{nome}@{ns}"
            
            # Não adiciona a si mesmo na lista de contatos
            if pid == self.meu_peer_id: 
                continue 
                
            if pid not in self.conhecidos:
                self.conhecidos[pid] = {
                    'ip':p.get('ip'),  
                    'port': p.get('port'), 
                    'status': 'NEW'
                }
            else:
                # Atualiza caso o IP/Porta da pessoa tenha mudado
                self.conhecidos[pid]['ip'] = p.get('ip')
                self.conhecidos[pid]['port'] = p.get('port')

    def salvar_conexao(self, peer_id, socket_conn, direcao="outbound"):
        """Guarda o cano TCP aberto para reuso futuro"""
        self.conexoes[peer_id] = socket_conn
        
        
        #criamos o cadastro dele "na marra" lendo o IP físico do cano TCP.
        if peer_id not in self.conhecidos:
            try:
                ip, porta = socket_conn.getpeername()
            except Exception:
                ip, porta = "Desconhecido", 0
                
            self.conhecidos[peer_id] = {
                'ip': ip,
                'port': porta
            }
            
        
        self.conhecidos[peer_id]['direcao'] = direcao
        self.conhecidos[peer_id]['status'] = 'CONNECTED'

    def obter_conexao(self, peer_id):
        """Devolve o Socket se ele já estiver aberto"""
        return self.conexoes.get(peer_id)

    def obter_info(self, peer_id):
        """Devolve o IP e a Porta de alguém da tabela"""
        return self.conhecidos.get(peer_id)