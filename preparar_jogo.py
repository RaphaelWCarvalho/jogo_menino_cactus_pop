"""Build a portable costume-only SDLPoP mod from the unmodified local distribution."""
from pathlib import Path
from collections import deque
import shutil, hashlib, json, re
from PIL import Image, ImageDraw, ImageFont

ROOT=Path(__file__).resolve().parent
SOURCE=ROOT/'preview/sdlpop/SDLPoP-1.23'
DEST=ROOT/'Menino_Cactus_Jogavel'
MOD=DEST/'mods/MeninoCactus/data/KID'
QA=ROOT/'verificacao';QA.mkdir(exist_ok=True)
GREEN=(33,128,65);DARK=(17,87,48);GOLD=(235,199,57)

def components(points):
    left=set(points);groups=[]
    while left:
        p=left.pop();q=[p];group={p}
        for x,y in q:
            for n in ((x-1,y),(x+1,y),(x,y-1),(x,y+1)):
                if n in left:left.remove(n);group.add(n);q.append(n)
        groups.append(group)
    return groups

def adapt(src,n):
    w,h=src.size
    hair=components((x,y) for y in range(h) for x in range(w) if src.getpixel((x,y)) in (1,4))
    eyes=[(x,y) for y in range(h) for x in range(w) if src.getpixel((x,y))==2]
    if hair:
        if eyes:
            ex,ey=eyes[0]
            head=min(hair,key=lambda c:min(abs(x-ex)+abs(y-ey) for x,y in c))
        else:head=max(hair,key=len)
        hx=sum(x for x,y in head)/len(head);hy=sum(y for x,y in head)/len(head)
    else:hx,hy=w/2,2
    if not eyes:ex,ey=hx,hy+3
    else:ex,ey=eyes[0]
    wrist=[(x,y) for c in hair if c!=head for x,y in c if src.getpixel((x,y))==1] if hair else []
    im=src.convert('RGBA')
    for y in range(h):
      for x in range(w):
        idx=src.getpixel((x,y));r,g,b,a=im.getpixel((x,y))
        if not a:continue
        face=abs(x-ex)<=5 and ey-3<=y<=ey+4
        glove=any(abs(x-wx)+abs(y-wy)<=4 for wx,wy in wrist)
        if idx==15:c=GREEN if x%4 else (46,151,74)
        elif idx==7:c=DARK
        elif idx in (13,14):c=GOLD if idx==13 else (154,122,25)
        elif idx in (1,4):c=(103,65,38) if (x,y) in head else GOLD
        elif idx==2:c=(54,38,28)
        elif idx in (5,6):
            if face:
                c=(29,143,73) if ey<=y<=ey+1 else (r,g,b)
            elif glove:c=GOLD
            else:c=GREEN if idx==6 else DARK
        else:c=(r,g,b)
        im.putpixel((x,y),(*c,a))
    # Keep the small chest mark from the approved concept on the upright poses.
    if n<=418 and h>14:
        xs=[x for x in range(w) if src.getpixel((x,11))==15]
        if xs:
            x=min(xs)
            for dx,dy in ((0,0),(1,0),(0,1),(0,2),(1,2)):
                if x+dx<w and src.getpixel((x+dx,11+dy)) in (7,15):im.putpixel((x+dx,11+dy),(*GOLD,255))
    return im

def save_indexed(im,p):
    # A deterministic palette; no quantization, no antialiasing, zero reserved for transparency.
    colors=sorted({(r,g,b) for r,g,b,a in im.get_flattened_data() if a})
    assert len(colors)<=255
    ids={c:i+1 for i,c in enumerate(colors)}
    out=Image.new('P',im.size)
    pal=[0,0,0]+[v for c in colors for v in c];out.putpalette(pal+[0]*(768-len(pal)))
    out.putdata([ids[(r,g,b)] if a else 0 for r,g,b,a in im.get_flattened_data()])
    out.save(p,transparency=0)

DEST.mkdir(exist_ok=True)
for name in ('prince.exe','SDL2.dll','SDL2_image.dll','COPYING','README.md'):
    shutil.copy2(SOURCE/name,DEST/name)
shutil.copytree(SOURCE/'data',DEST/'data',dirs_exist_ok=True)
# Include corresponding source and notices with the redistributed GPL engine.
shutil.copytree(SOURCE/'src',DEST/'src',dirs_exist_ok=True)
shutil.copytree(SOURCE/'doc',DEST/'doc',dirs_exist_ok=True)
MOD.mkdir(parents=True,exist_ok=True)
records=[]
for p in sorted((SOURCE/'data/KID').glob('*.png')):
    n=int(p.stem[3:])
    if n in (531,532,533,617,618,619):continue # Mouse and blood effects are not costume frames.
    src=Image.open(p);im=adapt(src,n);save_indexed(im,MOD/p.name)
    actual=Image.open(MOD/p.name).convert('RGBA');orig=src.convert('RGBA')
    assert actual.size==orig.size
    assert actual.getchannel('A').tobytes()==orig.getchannel('A').tobytes(),p.name
    assert actual.tobytes()==im.tobytes(),p.name
    records.append({'file':p.name,'size':im.size,'silhouette_unchanged':True})

ini=(SOURCE/'SDLPoP.ini').read_text()
ini=ini.replace('levelset = original','levelset = MeninoCactus')
ini=ini.replace('enable_info_screen = true;','enable_info_screen = false')
ini=ini.replace('pop_window_width = default','pop_window_width = 960')
ini=ini.replace('pop_window_height = default','pop_window_height = 600')
(DEST/'SDLPoP.ini').write_text(ini,encoding='utf-8')
(DEST/'mods/MeninoCactus/mod.ini').write_text('; Costume visual. Sem alteracoes de fisica, niveis ou animacoes.\n',encoding='ascii')
(DEST/'JOGAR.cmd').write_text('@echo off\r\ncd /d "%~dp0"\r\nstart "" "%~dp0prince.exe" mod MeninoCactus\r\n',encoding='ascii')
(DEST/'COMO JOGAR.txt').write_text('''MENINO CACTUS - PRIMEIRA VERSÃO JOGÁVEL

Para começar, dê dois cliques em JOGAR.cmd (ou em prince.exe).
Na apresentação do jogo, pressione qualquer tecla para começar.

CONTROLES
Setas esquerda/direita: virar e correr.
Seta para cima: pular ou subir. Durante a corrida: salto para a frente.
Seta para baixo: agachar ou descer.
Shift + setas: passos cuidadosos.
Segure Shift durante uma queda para se agarrar à borda.
Shift: pegar objetos; atacar quando estiver com a espada.
Seta para cima com a espada: defender.
F6: salvar rapidamente. F9: carregar.
Ctrl+A: recomeçar a fase. Esc: pausar e abrir opções.
Alt+Enter: alternar tela cheia. Ctrl+Q: sair.

SOBRE ESTA VERSÃO
Adaptação visual sem capa: máscara, cabelo, uniforme verde e detalhes amarelos.
O motor, as fases, os controles e os tempos de animação são os do SDLPoP 1.23.
Os quadros mantêm o tamanho e a silhueta originais. Não há novos poderes.
Esta é uma primeira versão visual: alguns detalhes do traje podem ser refinados.

O jogo original continua com suas cenas de perigo, combate e morte.
Referências do personagem fornecidas pelo usuário.
Motor: SDLPoP, por Dávid Nagy e colaboradores, GPL v3 ou posterior.
Projeto: https://github.com/NagyD/SDLPoP
Licença em COPYING; código correspondente em src; instruções em README.md.
''',encoding='utf-8-sig')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
for name in ('prince.exe','SDL2.dll','SDL2_image.dll'):
    assert sha(SOURCE/name)==sha(DEST/name)
for p in (SOURCE/'data').rglob('*'):
    if p.is_file():assert sha(p)==sha(DEST/p.relative_to(SOURCE))
(QA/'assets.json').write_text(json.dumps({'costume_frames':len(records),'engine_sha256':sha(DEST/'prince.exe'),'base_data_identical':True,'frames':records},indent=2))
sheet=Image.new('RGB',(960,((len(records)+15)//16)*80),'#1c272e');d=ImageDraw.Draw(sheet)
for i,r in enumerate(records):
    im=Image.open(MOD/r['file']).convert('RGBA');im.thumbnail((56,56),Image.Resampling.NEAREST)
    x=i%16*60;y=i//16*80;sheet.paste(im,(x,y),im);d.text((x,y+58),r['file'][3:-4],fill='white')
sheet.save(QA/'animacoes.png')
print(f'Criados {len(records)} quadros. Motor e cenarios identicos. Destino: {DEST}')
