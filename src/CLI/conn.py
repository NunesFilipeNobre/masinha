# CLI/conn.py

def mostrar_conexoes(cli):
    print("\n--- Conexões Ativas ---")
    
    conexoes_ativas = cli.estado.tabela.conexoes
    
    if not conexoes_ativas:
        print("Nenhuma conexão TCP aberta no momento.")
    else:
        for peer_id, sock in conexoes_ativas.items():
            try:
                # O getpeername() extrai o IP e a porta reais da ponta do socket
                ip_remoto, porta_remota = sock.getpeername()
                
                # Puxa a direção que salvamos na tabela de conhecidos
                info_peer = cli.estado.tabela.conhecidos.get(peer_id, {})
                direcao = info_peer.get('direcao', 'desconhecida')
                
                # Ajusta a setinha visual dependendo de quem iniciou a conexão
                seta = "<-" if direcao == "inbound" else "->"
                
                print(f"[{peer_id}] {seta} TCP {direcao.upper()} com {ip_remoto}:{porta_remota}")
            except Exception:
                print(f"[{peer_id}] Conectado (Dados do socket indisponíveis)")
                
    print("--------------------------------------\n")