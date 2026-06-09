#Interface de linha de comando

# cli.py
import sys

class CLI:
    def __init__(self, estado, conexao_p2p):
        self.estado = estado
        self.conexao_p2p = conexao_p2p

    def iniciar(self):
        print("\n" + "="*50)
        print(" Terminal P2P Iniciado! Digite /ajuda para comandos")
        print("="*50)

        # O loop infinito que mantém o programa vivo
        while True:
            try:
                # O input trava a tela esperando você digitar
                comando = input("p2p> ").strip()
                if not comando:
                    continue

                # Roteamento dos comandos
                if comando == "/ajuda":
                    self._mostrar_ajuda()
                elif comando == "/listar":
                    self._listar_peers()
                elif comando.startswith("/msg"):
                    self._enviar_mensagem(comando)
                elif comando == "/sair":
                    print("Encerrando o nó P2P...")
                    self.conexao_p2p.rodando = False
                    sys.exit(0)
                else:
                    print("Comando desconhecido. Digite /ajuda.")
                    
            except KeyboardInterrupt:
                # Trata o Ctrl+C graciosamente
                print("\nEncerrando o nó P2P (Ctrl+C)...")
                self.conexao_p2p.rodando = False
                sys.exit(0)

    def _mostrar_ajuda(self):
        print("\nComandos disponíveis:")
        print("  /listar                   - Mostra os peers conhecidos (da memória)")
        print("  /msg <ip> <porta> <texto> - Envia uma mensagem direta para um peer")
        print("  /sair                     - Fecha o programa de forma segura\n")

    def _listar_peers(self):
        """Consulta a memória (State) e imprime de forma legível"""
        peers = self.estado.obter_peers().get('peers', [])
        if not peers:
            print("Nenhum peer encontrado na memória.")
            return
        
        print("\n--- Peers na Rede ---")
        for p in peers:
            nome = p.get('name', 'Desconhecido')
            ip = p.get('ip')
            porta = p.get('port')
            print(f"[{nome}] IP: {ip} | Porta: {porta}")
        print("---------------------\n")

    def _enviar_mensagem(self, comando):
        """Quebra a string '/msg IP PORTA TEXTO' e repassa para a conexão P2P"""
        # Divide no máximo em 4 partes: ["/msg", "IP", "PORTA", "O resto da mensagem toda"]
        partes = comando.split(" ", 3)
        if len(partes) < 4:
            print("Erro de sintaxe. Uso correto: /msg <ip> <porta> <mensagem>")
            return
        
        _, ip, porta, mensagem = partes
        self.conexao_p2p.enviar_mensagem(ip, porta, mensagem)