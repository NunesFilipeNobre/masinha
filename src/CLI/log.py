def alterar_log(cli, comando):
    partes = comando.split(" ")
    if len(partes) < 2:
        print("Uso correto: /log <DEBUG|INFO>")
        return
        
    novo_nivel = partes[1].upper()
    if novo_nivel in ["DEBUG", "INFO"]:
        cli.estado.log_level = novo_nivel
        print(f"[CLI] Nível de log alterado para {novo_nivel}")
    else:
        print("[CLI] Níveis suportados: DEBUG, INFO")