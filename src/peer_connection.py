#Controla as conexões TCP e mensagens entre os peers

# peer_connection.py
import socket
import threading

class PeerConnectionManager:
    def __init__(self, porta_local=4000):
        self.porta_local = porta_local
        self.rodando = True

    def iniciar_servidor(self):
        """Dispara o servidor TCP em uma Thread separada para não travar o programa"""
        thread_servidor = threading.Thread(target=self._executar_servidor, daemon=True)
        thread_servidor.start()
        print(f"[SERVER] Servidor P2P iniciado em segundo plano na porta {self.porta_local}")

    def _executar_servidor(self):
        """O loop real do servidor que roda em segundo plano"""
        # Cria o socket de escuta (INADDR_ANY permite conexões de qualquer IP)
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as servidor:
            # Reutiliza a porta caso ela tenha sido fechada recentemente
            servidor.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            
            try:
                servidor.bind(('0.0.0.0', self.porta_local))
                servidor.listen()
                
                while self.rodando:
                    # O programa fica parado aqui até alguém conectar
                    socket_cliente, endereco = servidor.accept()
                    
                    # Quando alguém conecta, criamos UMA NOVA thread só para cuidar dessa conversa
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
        """Cuida das mensagens recebidas de um peer específico"""
        ip_peer, porta_peer = endereco
        print(f"\n[SERVER] Nova conexão recebida de {ip_peer}:{porta_peer}")
        
        with socket_cliente:
            try:
                while self.rodando:
                    dados = socket_cliente.recv(1024)
                    if not dados:
                        break # O peer fechou a conexão
                        
                    mensagem = dados.decode('utf-8').strip()
                    print(f"\n[MENSAGEM RECEBIDA de {ip_peer}]: {mensagem}")
                    
                    # Resposta de cortesia (opcional no protocolo de vocês)
                    socket_cliente.sendall("Mensagem recebida com sucesso!\n".encode('utf-8'))
                    
            except Exception as e:
                print(f"[SERVER] Erro na conversa com {ip_peer}: {e}")
        print(f"[SERVER] Conexão encerrada com {ip_peer}")

    def enviar_mensagem(self, ip_destino, porta_destino, mensagem):
        """Tenta abrir uma conexão rápida e enviar uma mensagem para um peer"""
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(3.0)
                print(f"[CLIENT] Tentando conectar em {ip_destino}:{porta_destino}...")
                s.connect((ip_destino, int(porta_destino)))
                
                print(f"[CLIENT] Enviando mensagem...")
                s.sendall((mensagem + "\n").encode('utf-8'))
                
                # Lê a resposta do colega
                resposta = s.recv(1024)
                print(f"[CLIENT] Resposta do peer: {resposta.decode('utf-8').strip()}")
                return True
        except Exception as e:
            print(f"[CLIENT] Não foi possível enviar mensagem para {ip_destino}:{porta_destino}. Erro: {e}")
            return False