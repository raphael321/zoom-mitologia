#!/bin/zsh
# Uso: ./preparar_base.sh quadros/q00.jpg bases/b11.png
# Põe o quadro de dentro a 50% no centro de uma tela 1024x1024 cinza.
# As bordas dele (48 px) se esfumam no cinza, para a IA pintar a transição
# em vez de deixar uma costura reta. O player esfuma a mesma faixa.
ffmpeg -loglevel error -y -i "$1" -f lavfi -i color=c=0x808080:s=1024x1024 \
  -filter_complex "[0]scale=512:512,format=rgba,geq=r='r(X,Y)':g='g(X,Y)':b='b(X,Y)':a='255*min(1,min(min(X,W-1-X),min(Y,H-1-Y))/48)'[in];[1][in]overlay=256:256" \
  -frames:v 1 "$2"
