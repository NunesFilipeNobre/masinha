# CLI/ajuda.py
def mostrar_ajuda():
    print("\nComandos disponíveis:")
    print("  /listar                   - Consulta o servidor e mostra os peers online")
    print("  /msg <nome@UnB> <texto>   - Envia uma mensagem direta para um peer")
    print("  /quit                     - Fecha o programa de forma segura\n")
    print("  /conn                   - Mostra as conexões TCP persistentes abertas")
    print("Comandos de Broadcast:")
    print("  /pub * <texto>            - Envia uma mensagem para todos os peers conectados")
    print("  /pub #namespace <texto>   - Envia uma mensagem para todos os peers de um namespace específico\n")
    print(" /rtt - Mostra o rtt\n")
    print("  /log <INFO|DEBUG>       - Altera a quantidade de logs na tela")