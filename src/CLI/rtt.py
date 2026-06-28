# CLI/rtt.py
# Função para mostrar a latência média (RTT) para cada peer conectado quando o usuário digita /rtt
def mostrar_rtt(cli):
    print("\n--- Latência Média (RTT) ---")
    peers = cli.estado.tabela.conhecidos
    
    nenhum_conectado = True
    # Percorre todos os peers conhecidos na tabela de peers do estado do CLI, e para cada peer que está com status CONNECTED, ele calcula a média dos RTTs armazenados e exibe essa média. Se não houver peers conectados, ele informa que nenhum peer está conectado no momento.
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