"""Renderiza o zoom infinito em vídeo (mesma matemática do index.html).

Uso: python3 render.py [saida.mp4] [--w 1080 --h 1920 --fps 30 --seg 4]
  --seg = segundos por quadro; o vídeo tem len(quadros) * seg e fecha o loop exato.
"""
import argparse, glob, json, subprocess
import numpy as np
from PIL import Image

ap = argparse.ArgumentParser()
ap.add_argument('saida', nargs='?', default='video/zoom-vertical.mp4')
ap.add_argument('--w', type=int, default=1080)
ap.add_argument('--h', type=int, default=1920)
ap.add_argument('--fps', type=int, default=30)
ap.add_argument('--seg', type=float, default=4.0)
ap.add_argument('--feather', type=float, default=0.06)
ap.add_argument('--animada', action='store_true',
                help='troca os quadros de "animados" (config do index.html) pelos vídeos em loop')
a = ap.parse_args()

SIZE = 1024
def mask():
    def ramp(n):
        x = np.arange(n) + 0.5
        return np.clip(np.minimum(x, n - x) / (a.feather * n), 0, 1)
    return Image.fromarray((np.outer(ramp(SIZE), ramp(SIZE)) * 255).astype(np.uint8))
MASK = mask()

def feathered(im):
    """RGBA com as bordas esfumadas (igual ao player)."""
    out = im.convert('RGB').resize((SIZE, SIZE), Image.BICUBIC).convert('RGBA')
    out.putalpha(MASK)
    return out

class Clip:
    """Vídeo em loop lido frame a frame do ffmpeg, na mesma taxa do vídeo de saída."""
    def __init__(self, path):
        self.p = subprocess.Popen(['ffmpeg', '-loglevel', 'error', '-stream_loop', '-1', '-i', path,
                                   '-vf', f'fps={a.fps},scale={SIZE}:{SIZE}', '-f', 'rawvideo',
                                   '-pix_fmt', 'rgb24', '-'], stdout=subprocess.PIPE)
        self.cur = None
    def advance(self):
        buf = self.p.stdout.read(SIZE * SIZE * 3)
        self.cur = feathered(Image.frombuffer('RGB', (SIZE, SIZE), buf))

animados = {}
if a.animada:
    cfg = open('index.html', encoding='utf-8').read()
    cfg = json.loads(cfg.split('id="zoom-config" type="application/json">')[1].split('</script>')[0])
    animados = {int(k): v for k, v in cfg['animados'].items()}

paths = sorted(glob.glob('quadros/q*.jpg'))
frames = [Clip(animados[i]) if i in animados else feathered(Image.open(p)) for i, p in enumerate(paths)]
clips = [f for f in frames if isinstance(f, Clip)]
n, W, H = len(frames), a.w, a.h
total = int(round(n * a.seg * a.fps))
base = max(W / SIZE, H / SIZE)   # "cover"

ff = subprocess.Popen(['ffmpeg', '-loglevel', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24',
                       '-s', f'{W}x{H}', '-r', str(a.fps), '-i', '-',
                       '-c:v', 'libx264', '-preset', 'slow', '-crf', '17', '-pix_fmt', 'yuv420p',
                       '-movflags', '+faststart', a.saida], stdin=subprocess.PIPE)

for i in range(total):
    T = i / total * n                      # vai de 0 a n: o último frame emenda no primeiro
    zoom = 2 ** (T % 1)
    canvas = Image.new('RGBA', (W, H), (0, 0, 0, 255))
    for c in clips:
        c.advance()
    for b in range(-1, 5):
        img = frames[(int(T) + b) % n]
        if isinstance(img, Clip):
            img = img.cur
        s = base * zoom / 2 ** b
        w, h = img.width * s, img.height * s
        if w < 2:
            break
        x0, y0 = (W - w) / 2, (H - h) / 2
        # só a parte visível: recorta na fonte e redimensiona direto para a tela
        vx0, vy0 = max(0, x0), max(0, y0)
        vx1, vy1 = min(W, x0 + w), min(H, y0 + h)
        if vx1 <= vx0 or vy1 <= vy0:
            continue
        # arredonda para dentro (a borda já é transparente) para a caixa nunca sair da imagem
        ix0, iy0 = int(np.ceil(vx0)), int(np.ceil(vy0))
        ix1, iy1 = int(np.floor(vx1)), int(np.floor(vy1))
        if ix1 <= ix0 or iy1 <= iy0:
            continue
        box = (max(0, (ix0 - x0) / s), max(0, (iy0 - y0) / s),
               min(img.width, (ix1 - x0) / s), min(img.height, (iy1 - y0) / s))
        part = img.resize((ix1 - ix0, iy1 - iy0), Image.BICUBIC, box=box)
        canvas.alpha_composite(part, (ix0, iy0))
    ff.stdin.write(canvas.convert('RGB').tobytes())
    if i % (a.fps * 4) == 0:
        print(f'{i}/{total}', flush=True)

ff.stdin.close()
ff.wait()
for c in clips:
    c.p.kill()
print('pronto:', a.saida)
