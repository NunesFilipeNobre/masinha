import socket
import json

# Configurações do servidor Rendezvous
HOST = 'pyp2p.mfcaetano.cc'  # Usando o Hostname que você passou nos comentários
PORT = 8080                  # Porta de conexão

def registrar(meu_nome="alicia", meu_namespace="UnB", minha_porta=4000):
    """
    Conecta ao Rendezvous e registra este nó.
    Retorna True se o registro foi bem-sucedido, e False caso contrário.
    """
    dados_registro = {
        "type": "REGISTER",
        "namespace": meu_namespace,
        "name": meu_nome,
        "port": minha_porta,
        "ttl": 3600
    }
    
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(5.0) 
        try:
            print(f"[REGISTER] Conectando a {HOST}:{PORT}...")
            s.connect((HOST, PORT))
            
            mensagem_json = json.dumps(dados_registro) + "\n"
            s.sendall(mensagem_json.encode('utf-8'))
            
            resposta = s.recv(1024)
            print("[REGISTER] Sucesso! Resposta do Servidor:")
            print(" -> " + resposta.decode('utf-8').strip())
            
            return True
            
        except Exception as e:
            print(f"[REGISTER] Falha ao tentar registrar: {e}")
            return False

def descobrir(meu_namespace="UnB"):

    # Voltamos ao JSON original que você tinha criado!
    dados_descobrir = {
        "type": "DISCOVER"
    }
    
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(5.0) 
        try:
            print(f"[DISCOVER] Conectando a {HOST}:{PORT}...")
            s.connect((HOST, PORT))
            
            mensagem_json = json.dumps(dados_descobrir) + "\n"
            s.sendall(mensagem_json.encode('utf-8'))
            
            resposta = s.recv(4096)
            
            try:
                texto_resposta = resposta.decode('utf-8')
                json_formatado = json.loads(texto_resposta)
                print("[DISCOVER] Sucesso! Lista baixada.")
                return json_formatado 
            except json.JSONDecodeError:
                print("[DISCOVER] Erro de formatação do JSON.")
                # Vamos imprimir o que veio cru pra não perder a info!
                print(texto_resposta)
                return []
                
        except Exception as e:
            print(f"[DISCOVER] Falha ao tentar descobrir os nós: {e}")
            return []