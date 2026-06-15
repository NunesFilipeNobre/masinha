# CLI/pub.py
def enviar_pub(cli, comando):
    partes = comando.split(" ", 2)
    if len(partes) < 3:
        print("Erro de sintaxe. Uso correto: /pub * <msg>  OU  /pub #namespace <msg>")
        return

    _, destino, mensagem = partes
    cli.cliente_p2p.conexao_p2p.enviar_pub(destino, mensagem)