# CLI/iniciar.py
import sys
from .ajuda import mostrar_ajuda
from .listar import listar_peers
from .msg import enviar_mensagem
from .pub import enviar_pub
from .rtt import mostrar_rtt
from .conn import mostrar_conexoes
def iniciar(cli):
    print("\n" + "="*50)
    print(" Terminal P2P Iniciado! Digite /ajuda para comandos")
    print("="*50)

    while True:
        try:
            comando = input("p2p> ").strip()
            if not comando:
                continue

            if comando == "/ajuda":
                mostrar_ajuda()
            elif comando == "/listar" or comando == "/peers":
                listar_peers(cli)
            elif comando.startswith("/msg"):
                enviar_mensagem(cli, comando)
            elif comando.startswith("/pub"):
                enviar_pub(cli, comando)
            elif comando.startswith("/rtt"):
                mostrar_rtt(cli)
            elif comando == "/conn": 
                mostrar_conexoes(cli)
            elif comando == "/quit":
                print("Encerrando o nó P2P...")
                cli.cliente_p2p.parar()
                sys.exit(0)
            else:
                print("Comando desconhecido. Digite /ajuda.")

        except KeyboardInterrupt:
            print("\nEncerrando o nó P2P (Ctrl+C)...")
            cli.cliente_p2p.parar()
            sys.exit(0)