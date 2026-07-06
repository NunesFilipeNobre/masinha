import socket
import json
from datetime import datetime

# Configurações do servidor Rendezvous pyp2p.mfcaetano.cc
with open("config.json", "r") as f:
    config = json.load(f)

HOST = config["host"]
PORT = config["rdv_port"]

def _log_rdv(mensagem, silencioso):
    """Função interna para padronizar os logs com Timestamp"""
    if not silencioso:
        agora = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        print(f"\n[{agora}] [Rendezvous] {mensagem}")
        # Repinta o cursor do terminal caso o log apareça em segundo plano
        print("p2p> ", end="", flush=True) 

def registrar(meu_nome, meu_namespace, minha_porta, meu_ttl, silencioso=False):
    dados_registro = {
        "type": "REGISTER",
        "namespace": meu_namespace,
        "name": meu_nome,
        "port": minha_porta,
        "ttl": meu_ttl
    }
    
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(5.0) 
        try:
            _log_rdv(f"Conectando a {HOST}:{PORT} (REGISTER)...", silencioso)
            s.connect((HOST, PORT))
            
            mensagem_json = json.dumps(dados_registro) + "\n"
            s.sendall(mensagem_json.encode('utf-8'))
            
            resposta = s.recv(1024)
            _log_rdv(f"Sucesso! Resposta: {resposta.decode('utf-8').strip()}", silencioso)
            return True
        except Exception as e:
            _log_rdv(f"Falha ao tentar registrar: {e}", silencioso)
            return False

def descobrir(meu_namespace="UnB", silencioso=False):
    dados_descobrir = {
        "type": "DISCOVER"
    }
    
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(5.0) 
        try:
            _log_rdv(f"Conectando a {HOST}:{PORT} (DISCOVER)...", silencioso)
            s.connect((HOST, PORT))
            
            mensagem_json = json.dumps(dados_descobrir) + "\n"
            s.sendall(mensagem_json.encode('utf-8'))
            
            resposta = s.recv(32768)
            
            try:
                texto_resposta = resposta.decode('utf-8')
                json_formatado = json.loads(texto_resposta)
                _log_rdv("Sucesso! Lista de peers baixada.", silencioso)
                return json_formatado 
            except json.JSONDecodeError:
                _log_rdv(f"Erro de formatação do JSON recebido: {texto_resposta}", silencioso)
                return []
        except Exception as e:
            _log_rdv(f"Falha ao tentar descobrir os nós: {e}", silencioso)
            return []

def desregistrar(meu_nome, meu_namespace):
    dados_saida = {
        "type": "UNREGISTER",
        "namespace": meu_namespace,
        "name": meu_nome
    }
    
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(3.0) 
        try:
            _log_rdv("Avisando o servidor sobre o encerramento (UNREGISTER)...", silencioso=False)
            s.connect((HOST, PORT))
            mensagem_json = json.dumps(dados_saida) + "\n"
            s.sendall(mensagem_json.encode('utf-8'))
            _log_rdv("Sucesso! Estamos fora do Rendezvous.", silencioso=False)
        except Exception as e:
            _log_rdv(f"Falha ao desregistrar: {e}", silencioso=False)