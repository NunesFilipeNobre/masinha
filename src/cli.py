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
        """Busca a lista atualizada no Rendezvous através do cliente, salva no State e imprime"""
        print("[CLI] Buscando atualizações no servidor Rendezvous...")
        
        # O cliente faz o trabalho de buscar e salvar no estado
        self.cliente_p2p.atualizar_rede()
        
        # Pega os dados novos que acabaram de ser salvos
        dicionario_estado = self.estado.obter_peers()
        peers = dicionario_estado.get('peers', [])
        
        if not peers:
            print("Nenhum peer encontrado na rede.")
            return
        
        print("\n--- Peers Online Agora ---")
        for p in peers:
            nome = p.get('name', 'Desconhecido')
            ip = p.get('ip')
            porta = p.get('port')
            print(f"[{nome}] IP: {ip} | Porta: {porta}")
        print("--------------------------\n")

    def _enviar_mensagem(self, comando):
        partes = comando.split(" ", 3)
        if len(partes) < 4:
            print("Erro de sintaxe. Uso correto: /msg <ip> <porta> <mensagem>")
            return
        
        _, ip, porta, mensagem = partes
        
        # Passa a mensagem completa para o gerenciador de conexões que está dentro do cliente
        self.cliente_p2p.conexao_p2p.enviar_mensagem(ip, porta, mensagem)