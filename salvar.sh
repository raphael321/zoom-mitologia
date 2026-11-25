#!/bin/zsh
# Uso: ./salvar.sh 10   → pega o JPG mais novo dos Downloads (últimos 2 min),
# salva como quadros/q10.jpg, mede o alinhamento do centro com o q11 e prepara bases/b09.png
set -e
cd "${0:A:h}"
n=$(printf %02d $1); inner=$(printf %02d $(( ($1 + 1) % 12 ))); prev=$(printf %02d $(( $1 - 1 )))
# só arquivos com o padrão de nome do Flow: Titulo_8hex.jpg
f=$(find -E ~/Downloads -maxdepth 1 -regex '.*/[A-Za-z0-9_…]+_[0-9a-f]{8}\.jpg' -mmin -2 -print0 | xargs -0 ls -t | head -1)
[[ -z "$f" ]] && { echo "nenhum download recente"; exit 1; }
mv "$f" quadros/q$n.jpg
psnr=$(ffmpeg -i quadros/q$n.jpg -i quadros/q$inner.jpg -filter_complex \
  "[0]crop=512:512:256:256[a];[1]scale=512:512[b];[a][b]psnr" -f null - 2>&1 | grep -o 'average:[0-9.]*')
echo "q$n salvo ($f) — centro vs q$inner: $psnr dB"
(( $1 > 1 )) && ./preparar_base.sh quadros/q$n.jpg bases/b$prev.png && echo "base b$prev pronta"
