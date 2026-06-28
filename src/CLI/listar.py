# CLI/listar.py
# Essa função é chamada quando o usuário digita /listar ou /peers, e ela consulta o servidor para atualizar a lista de peers conhecidos e exibe essa lista no terminal.
def listar_peers(cli):
    print("[CLI] Buscando atualizações no servidor Rendezvous...")

    # a função atualizar_rede() é responsável por consultar o servidor e atualizar a tabela de peers conhecidos no estado do CLI e ela está no módulo cliente_p2p
    cli.cliente_p2p.atualizar_rede()

    peers = cli.estado.tabela.conhecidos

    if not peers:
        print("Nenhum peer encontrado na rede.")
        return

    print("\n--- Tabela de Peers ---")
    # exibe cada peer conhecido com seu ID, IP, porta e status, o .items() é usado para iterar sobre o dicionário de peers, onde cada chave é o ID do peer e o valor é outro dicionário com informações sobre esse peer.
    for pid, info in peers.items():
        ip = info.get("ip")
        porta = info.get("port")
        status = info.get("status")
        print(f"[{pid}] IP: {ip}:{porta} | Status: {status}")
    print("-----------------------\n")