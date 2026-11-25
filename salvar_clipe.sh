#!/bin/zsh
# Uso: ./salvar_clipe.sh 07   → pega o MP4 1080p mais novo do Flow nos Downloads,
# recorta o quadrado central (a pintura) e mede se continua alinhado com quadros/q07.jpg
set -e
cd "${0:A:h}"
q=$1
f=$(find ~/Downloads -maxdepth 1 -name '*_1080p.mp4' -mmin -10 -print0 | xargs -0 ls -t | head -1)
[[ -z "$f" ]] && { echo "nenhum vídeo recente"; exit 1; }
mv "$f" animacao/q${q}_veo_1080p.mp4
ffmpeg -loglevel error -y -i animacao/q${q}_veo_1080p.mp4 -vf "crop=1080:1080:420:0" \
  -c:v libx264 -crf 16 -pix_fmt yuv420p -an animacao/q$q.mp4
echo "q$q.mp4 pronto ($f)"
for t in 0 4 7.5; do
  echo -n "  t=$t vs pintura: "
  ffmpeg -ss $t -i animacao/q$q.mp4 -i quadros/q$q.jpg -filter_complex \
    "[0]scale=1024:1024[a];[1]scale=1024:1024[b];[a][b]psnr" -frames:v 1 -f null - 2>&1 | grep -o 'average:[0-9.]*'
done
