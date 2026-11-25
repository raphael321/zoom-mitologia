#!/bin/zsh
# Uso: ./base_anel.sh quadros/q08.jpg quadros/q09.jpg bases/b08_anel.png
# Refaz o miolo de um quadro sem mexer na borda externa (que já encaixa no quadro de fora):
# mantém os 112 px de fora do quadro original, põe o quadro de dentro a 50% esfumado
# no centro e deixa cinza o anel entre os dois, para a IA repintar.
ffmpeg -loglevel error -y -i "$1" -i "$2" -f lavfi -i color=c=0x808080:s=1024x1024 -filter_complex "\
[0]scale=1024:1024,format=rgba,geq=r='r(X,Y)':g='g(X,Y)':b='b(X,Y)':a='255*min(1,max(0,(max(abs(X-511.5),abs(Y-511.5))-400)/48))'[outer];\
[1]scale=512:512,format=rgba,geq=r='r(X,Y)':g='g(X,Y)':b='b(X,Y)':a='255*min(1,min(min(X,W-1-X),min(Y,H-1-Y))/48)'[in];\
[2][outer]overlay[t];[t][in]overlay=256:256" -frames:v 1 "$3"
