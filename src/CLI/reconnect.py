# CLI/reconnect.py
def forcar_reconexao(cli):
    print("\n[CLI] Varrendo tabela para forçar reconexão imediata...")
    
    # Força todo mundo que tá DISCONNECTED ou STALE para tentar AGORA
    for peer_id, info in cli.estado.tabela.conhecidos.items():
        if info.get('status') in ['STALE', 'DISCONNECTED']:
            info['status'] = 'STALE'
            
            # Limpa o relógio de backoff (Zera as tentativas e o tempo de espera)
            motor = cli.cliente_p2p.reconnect_manager
            if peer_id in motor.backoff_tracking:
                del motor.backoff_tracking[peer_id]
                
    print("[CLI] Motor acionado! Os contatos inativos serão testados no próximo segundo.\n")