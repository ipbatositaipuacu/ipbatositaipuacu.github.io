"""Descobre o episódio mais recente do podcast da igreja e grava em ultimo-sermao.json.

Lê a página pública do player do Spotify (sem credenciais). Se o Spotify mudar
essa página, o script falha sem tocar no arquivo, e o botão do site continua
apontando para o último sermão conhecido.
"""
import json
import re
import sys
import urllib.request

PODCAST = "3iFh2dstNw8r6Yi8gNq7Oc"
ARQUIVO = "ultimo-sermao.json"

req = urllib.request.Request(
    f"https://open.spotify.com/embed/show/{PODCAST}",
    headers={"User-Agent": "Mozilla/5.0", "Accept-Language": "pt-BR"},
)
pagina = urllib.request.urlopen(req, timeout=30).read().decode("utf-8", "replace")

bloco = re.search(r'<script id="__NEXT_DATA__"[^>]*>(.*?)</script>', pagina, re.S)
if not bloco:
    sys.exit("Não achei os dados do episódio na página do player.")
episodio = json.loads(bloco.group(1))["props"]["pageProps"]["state"]["data"]["entity"]

uri = re.fullmatch(r"spotify:episode:([A-Za-z0-9]{22})", episodio.get("uri", ""))
titulo = (episodio.get("title") or episodio.get("name") or "").strip()
if episodio.get("type") != "episode" or not uri or not titulo:
    sys.exit(f"Resposta inesperada do Spotify: {episodio.get('type')} {episodio.get('uri')}")

data = episodio.get("releaseDate") or {}
novo = {
    "id": uri.group(1),
    "titulo": titulo,
    "data": data.get("isoString") if isinstance(data, dict) else None,
}

try:
    with open(ARQUIVO, encoding="utf-8") as f:
        atual = json.load(f)
except (FileNotFoundError, ValueError):
    atual = None

if novo == atual:
    print("Sem sermão novo:", titulo)
else:
    with open(ARQUIVO, "w", encoding="utf-8") as f:
        json.dump(novo, f, ensure_ascii=False, indent=2)
        f.write("\n")
    print("Sermão atualizado:", titulo)
