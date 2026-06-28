# CLI/pub.py
# Função para enviar uma mensagem de broadcast para todos os peers conectados ou para um namespace específico quando o usuário digita /pub * <mensagem> ou /pub #namespace <mensagem>
def enviar_pub(cli, comando):
    partes = comando.split(" ", 2)
    if len(partes) < 3:
        print("Erro de sintaxe. Uso correto: /pub * <msg>  OU  /pub #namespace <msg>")
        return

    _, destino, mensagem = partes
    # Envia a mensagem de broadcast para todos os peers conectados ou para um namespace específico usando a função de envio de mensagens do cliente P2P que esta no módulo cliente_p2p
    cli.cliente_p2p.conexao_p2p.enviar_pub(destino, mensagem)