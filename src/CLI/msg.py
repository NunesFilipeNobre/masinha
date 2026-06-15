# CLI/msg.py
def enviar_mensagem(cli, comando):
    partes = comando.split(" ", 2)
    if len(partes) < 3:
        print("Erro de sintaxe. Uso correto: /msg <peer_id> <mensagem>")
        return

    _, peer_id, mensagem = partes
    cli.cliente_p2p.conexao_p2p.enviar_mensagem(peer_id, mensagem)