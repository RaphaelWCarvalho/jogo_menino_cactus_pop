from pathlib import Path
import sys, subprocess, math, json
from PIL import Image, ImageDraw, ImageFont, ImageOps
ROOT=Path(__file__).resolve().parent
GAME=ROOT/'sdlpop/SDLPoP-1.23'
OUT=ROOT/'resultado'; OUT.mkdir(exist_ok=True)
MOD=GAME/'mods/MeninoCactus/data/KID'; MOD.mkdir(parents=True,exist_ok=True)
GREEN=(33,128,65); DARK=(17,87,48); GOLD=(235,199,57)

def adapt(n):
    src=Image.open(GAME/f'data/KID/res{n}.png').convert('RGBA')
    im=src.copy(); w,h=im.size
    # Preserve the source silhouette and pixel grid; recolor the existing costume.
    for y in range(h):
      for x in range(w):
        r,g,b,a=src.getpixel((x,y))
        if not a: continue
        if r>235 and g>230:
          c=GREEN if x%4 else (46,151,74)
        elif y<7:
          if r==184 and g==144: c=(103,65,38)
          elif y in (3,4) and r>170: c=(29,143,73)
          else: c=(r,g,b)
        elif y>h-6: c=GOLD if r>170 else (154,122,25)
        elif y>h*.43 and r>170 and r>g+20: c=GOLD
        else: c=GREEN if r>180 else DARK
        im.putpixel((x,y),(*c,a))
    # Tiny profile chest insignia, only on upright torso frames.
    if n<=418:
      candidates=[x for x in range(w) if src.getpixel((x,11))[0]>235]
      if candidates:
        x=min(candidates)
        for dx,dy in [(0,0),(1,0),(0,1),(0,2),(1,2)]:
          if x+dx<w and im.getpixel((x+dx,11+dy))[3]: im.putpixel((x+dx,11+dy),(*GOLD,255))
    return im

sprites={n:adapt(n) for n in range(401,450)}
for n,im in sprites.items():
    # Indexed palette with explicit transparent index, matching the game's asset convention.
    rgb=Image.new('RGB',im.size,'black');rgb.paste(im,mask=im.getchannel('A'))
    indexed=rgb.quantize(colors=255)
    palette=indexed.getpalette(); data=list(indexed.getdata());alpha=list(im.getchannel('A').getdata())
    indexed.putpalette([0,0,0]+palette[:765]); indexed.putdata([v+1 if a else 0 for v,a in zip(data,alpha)])
    indexed.save(MOD/f'res{n}.png',transparency=0)

fontdir=Path('C:/Windows/Fonts')
def font(size,bold=False): return ImageFont.truetype(str(fontdir/('arialbd.ttf' if bold else 'arial.ttf')),size)
def label(d,xy,s,size=20,fill='#dde7e5',bold=False):d.text(xy,s,font=font(size,bold),fill=fill)

bg=Image.open(GAME/'screenshots/screenshot_003.png').convert('RGB')
# Remove the original actor from the doorway's uniform black interior.
ImageDraw.Draw(bg).rectangle((218,75,240,120),fill='black')
# Reconstruct the floor directly beneath that actor from the adjacent floor texture.
bg.paste(bg.crop((194,114,216,126)),(218,114))

def scene(t):
    im=bg.copy()
    # All poses below are original animation frames; translation is a visual mock-up.
    if t<1.5: n=415; x=50;lift=0;action='PARADO'
    elif t<5.5:
        q=t-1.5;n=407+int(q*12)%8;x=50+q*36;lift=0;action='CORRENDO'
    elif t<7.1:
        q=(t-5.5)/1.6;n=434+min(15,int(q*16));x=194+q*77;lift=math.sin(q*math.pi)*32;action='PULANDO'
    elif t<8.1:n=415;x=271;lift=0;action='PARADO'
    else:
        q=t-8.1;n=407+int(q*12)%8;x=271-q*45;lift=0;action='CORRENDO'
    sp=sprites[n]
    if t<8.1:sp=ImageOps.mirror(sp)
    im.paste(sp,(round(x-sp.width/2),round(120-sp.height-lift)),sp)
    return im,action,n

def frame(t):
    canvas=Image.new('RGB',(960,720),'#111b20'); d=ImageDraw.Draw(canvas)
    label(d,(28,15),'MENINO CACTUS',27,'#b1ec8e',True)
    label(d,(680,22),'PRÉVIA VISUAL · SEM CAPA',16,'#f0d16b',True)
    if t<11.5:
      im,action,n=scene(t)
      canvas.paste(im.resize((960,600),Image.Resampling.NEAREST),(0,64))
      d=ImageDraw.Draw(canvas);d.rounded_rectangle((25,80,185,111),5,fill='#172720')
      label(d,(39,86),action,17,'#c2eda5',True)
      # Bottom HUD obscures the original level text only outside game image.
      d.rectangle((0,634,960,720),fill='#111b20')
      label(d,(28,648),'Simulação montada com cenário e poses do SDLPoP.',19)
      label(d,(28,679),'Teste de aparência e movimento; não é uma captura de gameplay.',17,'#a4b1b4')
    else:
      label(d,(45,101),'MESMAS POSES. NOVA IDENTIDADE.',30,'#ffffff',True)
      for x,original,title in [(210,True,'PRÍNCIPE ORIGINAL'),(650,False,'MENINO CACTUS')]:
        n=407+int(t*12)%8
        sp=Image.open(GAME/f'data/KID/res{n}.png').convert('RGBA') if original else sprites[n]
        sp=ImageOps.mirror(sp);sp=sp.resize((sp.width*7,sp.height*7),Image.Resampling.NEAREST)
        canvas.paste(sp,(x-sp.width//2,480-sp.height),sp)
        label(d,(x-125,510),title,22,'#d1e8c9',True)
      label(d,(45,590),'Verde, máscara, cabelo e detalhes amarelos.',24)
      label(d,(45,632),'Proporções e animações do príncipe preservadas.',22,'#a4b1b4')
      label(d,(45,680),'PROTÓTIPO VISUAL · AINDA NÃO É UM MOD COMPLETO',16,'#f0d16b',True)
    return canvas

if __name__=='__main__':
    sys.path.insert(0,str(ROOT/'tools'));import imageio_ffmpeg
    ff=imageio_ffmpeg.get_ffmpeg_exe()
    dest=OUT/'Menino_Cactus_Previa.mp4'
    cmd=[ff,'-y','-f','rawvideo','-vcodec','rawvideo','-pix_fmt','rgb24','-s','960x720','-r','24','-i','-','-an','-c:v','libx264','-crf','18','-pix_fmt','yuv420p','-movflags','+faststart',str(dest)]
    proc=subprocess.Popen(cmd,stdin=subprocess.PIPE,stderr=subprocess.PIPE)
    for i in range(15*24):proc.stdin.write(frame(i/24).tobytes())
    proc.stdin.close();err=proc.stderr.read();rc=proc.wait()
    if rc:raise RuntimeError(err.decode(errors='replace'))
    frame(3.2).save(OUT/'Menino_Cactus_Previa.png')
    contact=Image.new('RGB',(960,720))
    for i,t in enumerate([0,3.2,5.9,6.4,8.7,12]):contact.paste(frame(t).resize((320,360)),(i%3*320,i//3*360))
    contact.save(OUT/'verificacao.jpg')
    (OUT/'LEIA-ME.txt').write_text('Prévia visual de 15 segundos. Sem capa.\nCenários e poses: SDLPoP 1.23 (https://github.com/NagyD/SDLPoP).\nAs imagens foram compostas fora do jogo; deslocamento e salto são uma simulação.\nEsta prévia não comprova colisões, controles ou uma modificação completa.\nVisual inspirado nas referências fornecidas: máscara, cabelo, verde e amarelo.\n',encoding='utf-8')
    print(dest)
