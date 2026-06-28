# CLI/reconnect.py
# Função para forçar a reconexão imediata com todos os peers que estão com status DISCONNECTED ou STALE quando o usuário digita /reconnect
def forcar_reconexao(cli):
    print("\n[CLI] Varrendo tabela para forçar reconexão imediata...")
    
    # Percorre todos os peers conhecidos na tabela de peers do estado do CLI, e para cada peer que está com status DISCONNECTED ou STALE, ele altera o status para STALE e limpa o relógio de backoff associado a esse peer no motor de reconexão.
    for peer_id, info in cli.estado.tabela.conhecidos.items():
        if info.get('status') in ['STALE', 'DISCONNECTED']:
            info['status'] = 'STALE'
            
            
            motor = cli.cliente_p2p.reconnect_manager
            if peer_id in motor.backoff_tracking:
                del motor.backoff_tracking[peer_id]
                
    print("[CLI] Motor acionado! Os contatos inativos serão testados no próximo segundo.\n")