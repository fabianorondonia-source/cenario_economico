"""
Helper HTTP compartilhado por todos os módulos de services/.

Existe por causa de um problema clássico do Python no macOS: quando o
Python vem do instalador oficial (python.org) — ou às vezes até via
Homebrew — o certificado raiz usado para validar HTTPS não está instalado
no keychain do próprio Python, e toda chamada https:// falha com
"CERTIFICATE_VERIFY_FAILED: unable to get local issuer certificate",
mesmo com a internet funcionando normalmente para tudo mais (navegador,
curl, git). Isso derruba silenciosamente todo fetch de indicador.

Usamos o pacote `certifi` (via pip, já em requirements.txt) para montar um
contexto SSL com uma lista de certificados confiável e independente do
sistema — resolve o problema sem precisar rodar o
"Install Certificates.command" manualmente.
"""

import ssl
import urllib.request

try:
    import certifi
    _SSL_CONTEXT = ssl.create_default_context(cafile=certifi.where())
except ImportError:
    _SSL_CONTEXT = None

TIMEOUT_PADRAO = 10


def abrir_url(url, timeout=TIMEOUT_PADRAO):
    """Retorna o objeto de resposta (bytes ainda não lidos) de uma URL,
    usando o contexto SSL do certifi quando disponível. Deixa a exceção
    subir para quem chamou decidir como logar/tratar."""
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (Netway EID)"})
    return urllib.request.urlopen(req, timeout=timeout, context=_SSL_CONTEXT)


def descrever_erro(e):
    """Mensagem de erro mais legível — sinaliza explicitamente quando é o
    problema clássico de certificado do macOS, pra facilitar diagnóstico."""
    texto = str(e)
    if "CERTIFICATE_VERIFY_FAILED" in texto or "certificate verify failed" in texto:
        return (f"{type(e).__name__}: {texto} — "
                "isso costuma ser certificado SSL do Python no macOS, não falta de internet. "
                "Solução: 'pip install --upgrade certifi' dentro do .venv do projeto.")
    return f"{type(e).__name__}: {texto}"
