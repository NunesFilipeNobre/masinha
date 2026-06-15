# CLI/conn.py
def mostrar_conexoes(cli):
    print("\n--- Conexões Ativas (Persistentes) ---")
    
    conexoes_ativas = cli.estado.tabela.conexoes
    
    if not conexoes_ativas:
        print("Nenhuma conexão TCP aberta no momento.")
    else:
        for peer_id, sock in conexoes_ativas.items():
            try:
                # O getpeername() extrai o IP e a porta reais da ponta do socket
                ip_remoto, porta_remota = sock.getpeername()
                print(f"[{peer_id}] Conectado via TCP -> {ip_remoto}:{porta_remota}")
            except Exception:
                print(f"[{peer_id}] Conectado (Dados do socket indisponíveis)")
                
    print("--------------------------------------\n")