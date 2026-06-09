# cli.py
import sys

class CLI:
    def __init__(self, estado, cliente_p2p):
        self.estado = estado
        self.cliente_p2p = cliente_p2p # Guarda a referência correta do orquestrador

    def iniciar(self):
        print("\n" + "="*50)
        print(" Terminal P2P Iniciado! Digite /ajuda para comandos")
        print("="*50)

        while True:
            try:
                comando = input("p2p> ").strip()
                if not comando:
                    continue

                if comando == "/ajuda":
                    self._mostrar_ajuda()
                elif comando == "/listar":
                    self._listar_peers() 
                elif comando.startswith("/msg"):
                    self._enviar_mensagem(comando)
                elif comando == "/sair":
                    print("Encerrando o nó P2P...")
                    self.cliente_p2p.parar() # Chama a função de parada segura do orquestrador
                    sys.exit(0)
                else:
                    print("Comando desconhecido. Digite /ajuda.")
                    
            except KeyboardInterrupt:
                print("\nEncerrando o nó P2P (Ctrl+C)...")
                self.cliente_p2p.parar() # Chama a parada segura também no Ctrl+C
                sys.exit(0)

    def _mostrar_ajuda(self):
        print("\nComandos disponíveis:")
        print("  /listar                   - Consulta o servidor e mostra os peers online")
        print("  /msg <ip> <porta> <texto> - Envia uma mensagem direta para um peer")
        print("  /sair                     - Fecha o programa de forma segura\n")

    def _listar_peers(self):
        print("[CLI] Buscando atualizações no servidor Rendezvous...")
        self.cliente_p2p.atualizar_rede()
        
        # Agora lemos da PeerTable!
        peers = self.estado.tabela.conhecidos
        
        if not peers:
            print("Nenhum peer encontrado na rede.")
            return
        
        print("\n--- Tabela de Peers ---")
        for pid, info in peers.items():
            ip = info.get('ip')
            porta = info.get('port')
            status = info.get('status')
            print(f"[{pid}] IP: {ip}:{porta} | Status: {status}")
        print("-----------------------\n")

    def _enviar_mensagem(self, comando):
        # Agora o comando é: /msg bob@UnB Oi tudo bem?
        # Dividimos em 3 partes: ["/msg", "bob@UnB", "Oi tudo bem?"]
        partes = comando.split(" ", 2)
        if len(partes) < 3:
            print("Erro de sintaxe. Uso correto: /msg <peer_id> <mensagem>")
            return
        
        _, peer_id, mensagem = partes
        self.cliente_p2p.conexao_p2p.enviar_mensagem(peer_id, mensagem)