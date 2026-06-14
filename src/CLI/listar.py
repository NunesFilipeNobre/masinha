# CLI/listar.py
def listar_peers(cli):
    print("[CLI] Buscando atualizações no servidor Rendezvous...")
    cli.cliente_p2p.atualizar_rede()

    peers = cli.estado.tabela.conhecidos

    if not peers:
        print("Nenhum peer encontrado na rede.")
        return

    print("\n--- Tabela de Peers ---")
    for pid, info in peers.items():
        ip = info.get("ip")
        porta = info.get("port")
        status = info.get("status")
        print(f"[{pid}] IP: {ip}:{porta} | Status: {status}")
    print("-----------------------\n")