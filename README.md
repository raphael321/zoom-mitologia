# Do Olimpo ao Hades — zoom infinito

Um zoom infinito (no estilo dos *zoomquilts*) por 12 pinturas surreais e psicodélicas de mitologia grega:
do trono de Zeus, passando pelo carro do Sol, Atenas, o mar de Poseidon e o rio Estige, até o salão de Hades,
onde o Olimpo reaparece num poço de visões e o ciclo recomeça.

As pinturas foram geradas com IA (Google Flow — Nano Banana para as imagens, Veo para as animações),
cada uma pintada em volta da anterior para que o miolo de um quadro seja exatamente o quadro seguinte.

**Vídeos prontos (1080×1920, 48 s, loop perfeito):** veja a [Release](../../releases/latest) —
versão estática e versão com 4 quadros animados.

## Rodar o player

```bash
python3 -m http.server 8765
```

Abra http://localhost:8765 (o WebGL não carrega as imagens direto do arquivo, por isso o servidor).

- **Roda do mouse / ↑ ↓** — velocidade (dá para ir para trás)
- **No celular:** toque na tela mostra/esconde a barra; arrastar para baixo acelera, para cima desacelera e volta
- **1–5** — efeitos: Original, Cores, Redemoinho, Ácido, Brilho
- **A** / botão **Animação** — liga e desliga os clipes animados (Zeus, Poseidon, Estige e Hades); começa ligado
- **F** — tela cheia
- `?versao=estatica` — abre com a animação desligada

## Como funciona

Cada quadro N+1 é o centro de N reduzido a 50%. O player desenha 4–5 camadas encaixadas,
cada uma 2× menor que a anterior, com as bordas esfumadas, e escala tudo de 1× a 2×;
ao chegar em 2× troca para o quadro seguinte e volta a 1× — sem salto visível.
Os efeitos são um shader WebGL por cima da composição.

| Quadro | Cena | Animado |
|---|---|---|
| q00 | Zeus segurando o banquete como visão, águia, galáxia | ✓ |
| q01 | Banquete dos deuses, Hera com pavões, Afrodite na concha | |
| q02 | Carro do Sol de Apolo, Eos, constelações vivas | |
| q03 | Encostas do Olimpo, Musas, Apolo com a lira, Pégaso | |
| q04 | Acrópole, Atena com o escudo da Medusa, coruja | |
| q05 | Campos de Deméter, Perséfone, girassóis | |
| q06 | Vinhedo de Dioniso nas falésias | |
| q07 | Poseidon no carro de hipocampos, mar em tempestade | ✓ |
| q08 | Palácio submarino de Poseidon | |
| q09 | Caverna de Tênaro, Hermes guiando as almas | |
| q10 | Rio Estige, Caronte, rostos de pedra que abrem os olhos | ✓ |
| q11 | Hades e Perséfone, Cérbero, o Olimpo num poço de visões | ✓ |

## Fazer o seu

Requer `ffmpeg` e Python 3 com Pillow e NumPy.

1. Gere o primeiro quadro (1:1).
2. `./preparar_base.sh quadros/q00.jpg bases/b11.png` — põe o quadro a 50% no centro de uma tela cinza,
   com as bordas esfumadas.
3. Mande a base para um modelo de edição de imagem com um prompt de *outpainting*:
   > Keep the central picture in the same position and size and keep its content. Its edges fade softly into flat gray:
   > repaint that soft fading border AND all the gray area, so that the central picture continues seamlessly into the
   > new scene with no visible seam, no square, no frame. The new surrounding scene: …
4. Salve como o quadro de fora e repita, andando de dentro para fora. `salvar.sh` mede o alinhamento do centro (PSNR ≈ 20 dB = ok)
   e já prepara a próxima base.
5. Para fechar o loop (ou consertar uma costura), `./base_anel.sh fora.jpg dentro.jpg base.png` mantém a borda externa,
   coloca o quadro de dentro no centro e deixa só o anel do meio para repintar.
6. Animação: quadro 16:9 com a pintura no centro, gerador de vídeo com início = fim e câmera travada;
   `salvar_clipe.sh` recorta o quadrado de volta.
7. `python3 render.py saida.mp4 [--animada] [--w 1080 --h 1920 --seg 4]` renderiza o vídeo.

Inspirado nos zoomquilts de Nikolaus Baumgarten e colaboradores (zoomquilt.org, organiccity.org).
O código e as imagens aqui são originais.
