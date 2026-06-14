# CLI/rtt.py
def mostrar_rtt(cli):
    print("\n--- Latência Média (RTT) ---")
    peers = cli.estado.tabela.conhecidos
    
    nenhum_conectado = True
    for pid, info in peers.items():
        if info.get('status') == 'CONNECTED':
            nenhum_conectado = False
            rtts = info.get('rtts', [])
            if rtts:
                media = sum(rtts) / len(rtts)
                print(f"[{pid}] RTT Médio: {media:.2f} ms")
            else:
                print(f"[{pid}] RTT Médio: Aguardando PONG...")
                
    if nenhum_conectado:
        print("Nenhum peer conectado no momento.")
    print("----------------------------\n")