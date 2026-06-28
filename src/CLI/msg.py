# CLI/msg.py
# Função para enviar uma mensagem direta para um peer quando o usuário digita /msg <peer_id> <mensagem>
def enviar_mensagem(cli, comando):
    partes = comando.split(" ", 2)
    if len(partes) < 3:
        print("Erro de sintaxe. Uso correto: /msg <peer_id> <mensagem>")
        return

    _, peer_id, mensagem = partes
    # Envia a mensagem para o peer especificado usando a função de envio de mensagens do cliente P2P que esta no módulo cliente_p2p
    cli.cliente_p2p.conexao_p2p.enviar_mensagem(peer_id, mensagem)