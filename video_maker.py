import asyncio
import edge_tts
import requests
from moviepy import *
from pathlib import Path
from PIL import Image, ImageDraw
from io import BytesIO

# ─────────────────────────────────────────────────────────────────
# CONFIGURAÇÕES
# ─────────────────────────────────────────────────────────────────

# Voz da narração — pt-BR feminina, soa natural
VOZ = "pt-BR-FranciscaNeural"

# Pasta onde os vídeos serão salvos
PASTA_VIDEOS = Path("videos")
PASTA_VIDEOS.mkdir(exist_ok=True)

# ─────────────────────────────────────────────────────────────────
# PASSO 1 — GERAR NARRAÇÃO
# ─────────────────────────────────────────────────────────────────
async def gerar_narracao(texto, arquivo_saida):
    print(f"🎙️ Gerando narração...")
    tts = edge_tts.Communicate(texto, VOZ)
    await tts.save(arquivo_saida)

# ─────────────────────────────────────────────────────────────────
# PASSO 2 — BAIXAR IMAGEM DO PRODUTO
# Quando a API da Shopee estiver conectada, essa função
# vai baixar a imagem real do produto automaticamente
# ─────────────────────────────────────────────────────────────────
def baixar_imagem(url, arquivo_saida):
    print(f"🖼️ Baixando imagem do produto...")
    resposta = requests.get(url, timeout=10)
    img = Image.open(BytesIO(resposta.content)).convert("RGB")
    img.save(arquivo_saida, "JPEG")

# ─────────────────────────────────────────────────────────────────
# PASSO 3 — MONTAR O VÍDEO
# Formato vertical (1080x1920) — ideal pra TikTok, Reels e Shorts
# ─────────────────────────────────────────────────────────────────
def montar_video(imagem_path, audio_path, nome_produto, link_curto, saida_path):
    print(f"🎬 Montando vídeo...")

    # Carrega o áudio pra saber a duração do vídeo
    audio    = AudioFileClip(audio_path)
    duracao  = audio.duration

    # Cria o fundo preto no formato vertical
    fundo = ColorClip(size=(1080, 1920), color=(13, 15, 20), duration=duracao)

    # Carrega a imagem do produto e centraliza
    imagem = (ImageClip(imagem_path)
              .resized(width=900)
              .with_position("center")
              .with_duration(duracao))

    # Texto com o nome do produto
    texto_nome = (TextClip(
                    text=nome_produto,
                    font_size=48,
                    color="white",
                    font="Arial",
                    size=(1000, None),
                    method="caption"
                  )
                  .with_position(("center", 1400))
                  .with_duration(duracao))

    # Texto com o link curto
    texto_link = (TextClip(
                    text=f"🔗 {link_curto}",
                    font_size=38,
                    color="#00e5a0",
                    font="Arial",
                    size=(1000, None),
                    method="caption"
                  )
                  .with_position(("center", 1550))
                  .with_duration(duracao))

    # Junta tudo
    video_final = CompositeVideoClip([fundo, imagem, texto_nome, texto_link])
    video_final = video_final.with_audio(audio)

    # Salva o vídeo
    video_final.write_videofile(
        saida_path,
        fps=24,
        codec="libx264",
        audio_codec="aac",
        logger=None
    )

# ─────────────────────────────────────────────────────────────────
# FUNÇÃO PRINCIPAL
# ─────────────────────────────────────────────────────────────────
async def criar_video_produto(produto, link_curto):
    nome     = produto["offerName"]
    comissao = float(produto["commissionRate"]) * 100

    print(f"\n📦 Criando vídeo para: {nome}")

    roteiro = f"""
    Olha esse achado incrível na Shopee!
    {nome}.
    Com até {comissao:.0f} por cento de desconto!
    Corre que é por tempo limitado.
    Acesse o link na descrição e garanta o seu agora!
    """

    audio_path  = str(PASTA_VIDEOS / "temp_audio.mp3")
    imagem_path = str(PASTA_VIDEOS / "temp_imagem.jpg")
    video_path  = str(PASTA_VIDEOS / f"{link_curto.replace('/', '')}.mp4")

    await gerar_narracao(roteiro, audio_path)

    # Se tiver URL de imagem, baixa. Senão usa a imagem de teste
    if produto.get("imageUrl"):
        baixar_imagem(produto["imageUrl"], imagem_path)

    montar_video(imagem_path, audio_path, nome, link_curto, video_path)

    print(f"✅ Vídeo salvo em: {video_path}")
    return video_path

# ─────────────────────────────────────────────────────────────────
# TESTE — cria imagem localmente pra testar sem precisar
# de internet ou credenciais da Shopee
# ─────────────────────────────────────────────────────────────────
async def main():
    # Cria imagem de teste colorida localmente
    print("🖼️ Criando imagem de teste...")
    img  = Image.new("RGB", (800, 800), color=(30, 80, 200))
    draw = ImageDraw.Draw(img)
    draw.text((200, 380), "PRODUTO TESTE", fill="white")
    img.save(str(PASTA_VIDEOS / "temp_imagem.jpg"), "JPEG")

    produto_teste = {
        "offerName"     : "Fone Bluetooth JBL Tune 520BT",
        "imageUrl"      : "",
        "commissionRate": "0.08"
    }

    await criar_video_produto(produto_teste, "fone-jbl")

if __name__ == "__main__":
    asyncio.run(main())