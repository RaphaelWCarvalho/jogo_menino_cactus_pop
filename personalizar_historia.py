"""Install title/story images only. No executable or gameplay changes."""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import json,hashlib,zipfile

ROOT=Path(__file__).resolve().parent
GAME=ROOT/'Menino_Cactus_Jogavel'
OUT=GAME/'mods/MeninoCactus/data/TITLE';OUT.mkdir(parents=True,exist_ok=True)
ART=ROOT/'arte_mc';QA=ROOT/'verificacao'
FONT=Path('C:/Windows/Fonts')

STORIES={
42:('A fonte do oásis',[
'Muito além da cidade, um',
'antigo palácio guarda a fonte',
'que dá vida a um oásis.',
'',
'Jaffar tomou o palácio e',
'prendeu sua guardiã. Agora,',
'as sombras cercam seus muros.']),
43:('Uma hora para salvar a guardiã',[
'A guardiã tem apenas uma hora.',
'',
'O Menino Cactus entrou no',
'palácio para salvá-la. Mas uma',
'armadilha o lançou nas',
'masmorras.',
'',
'É hora de encontrar a saída!']),
44:('A coragem floresce',[
'Jaffar foi vencido. A guardiã',
'está livre e a luz voltou',
'ao oásis.',
'',
'O Menino Cactus provou que a',
'coragem floresce até nos',
'lugares mais sombrios.',
'',
'Uma nova aventura o espera!'])}

def f(size,bold=False):return ImageFont.truetype(str(FONT/('consolab.ttf' if bold else 'consola.ttf')),size)
def pixel_text(canvas,xy,text,font,color,stroke=0,stroke_fill=None):
    # Draw text on a binary mask so the native-resolution image has hard pixel edges.
    mask=Image.new('1',canvas.size);d=ImageDraw.Draw(mask)
    if stroke:
        d.text(xy,text,font=font,fill=1,stroke_width=stroke)
        canvas.paste(stroke_fill,(0,0,*canvas.size),mask)
        mask=Image.new('1',canvas.size);d=ImageDraw.Draw(mask)
    d.text(xy,text,font=font,fill=1);canvas.paste(color,(0,0,*canvas.size),mask)

def centered(im,text,y,font,color,stroke=0,stroke_fill=None):
    w=ImageDraw.Draw(im).textlength(text,font=font)
    pixel_text(im,((im.width-w)//2,y),text,font,color,stroke,stroke_fill)

def indexed(im,path,transparent=False):
    # Reserve index zero for transparency without allowing quantization to use it as ink.
    rgba=im.convert('RGBA');rgb=im.convert('RGB')
    q=rgb.quantize(colors=254,method=Image.Quantize.MEDIANCUT,dither=Image.Dither.NONE)
    pal=q.getpalette();data=list(q.get_flattened_data())
    out=Image.new('P',im.size);out.putpalette([0,0,0]+pal[:762]+[0,0,0])
    alpha=list(rgba.getchannel('A').get_flattened_data())
    out.putdata([v+1 if a else 0 for v,a in zip(data,alpha)])
    opts={'transparency':0} if transparent else {}
    out.save(path,**opts)

before={str(p.relative_to(GAME)):hashlib.sha256(p.read_bytes()).hexdigest()
        for folder in [GAME/'data',GAME/'mods/MeninoCactus/data/KID'] for p in folder.rglob('*') if p.is_file()}
before['prince.exe']=hashlib.sha256((GAME/'prince.exe').read_bytes()).hexdigest()

main=Image.open(ART/'abertura_arte_original.png').convert('RGB').resize((320,200),Image.Resampling.LANCZOS)
# A native title overlay begins at y=107; transparent space protects the hero's legs.
title=Image.new('RGBA',(272,65),(0,0,0,0))
centered(title,'MENINO CACTUS',22,f(24,True),'#f6cf55',1,'#09372e')
centered(title,'O PALÁCIO DAS SOMBRAS',51,f(9,True),'#b2e7b0')
main.paste(title,(24,107),title)
centered(main,'PRESSIONE UMA TECLA PARA JOGAR',172,f(9,True),'#e1d9b2')
footer=main.crop((48,184,272,195))
centered(footer,'Base: © 1990 Jordan Mechner',0,f(9),'#b3baa2')
main.paste(footer,(48,184))
indexed(main,OUT/'res51.png')
indexed(title,OUT/'res54.png',True)
# Replace legacy credit flashes with matching background crops. All original
# authors remain credited in the original credits card and accompanying notices.
indexed(main.crop((96,106,224,153)),OUT/'res52.png')
indexed(main.crop((96,122,218,152)),OUT/'res53.png')
indexed(footer,OUT/'res55.png')

# Native indexed story border. Index 14 must exist because SDLPoP updates it;
# our background uses another index, so its intended forest green stays stable.
frame=Image.new('RGB',(320,200),'#031b18');d=ImageDraw.Draw(frame)
d.rectangle((2,2,317,197),outline='#d8ad45',width=2)
d.rectangle((7,7,312,192),outline='#2d744b',width=1)
d.line((18,18,301,18),fill='#b58d35');d.line((18,181,301,181),fill='#b58d35')
for x,y in [(7,7),(307,7),(7,187),(307,187)]:
    d.rectangle((x,y,x+5,y+5),fill='#d8ad45')
centered(frame,'MENINO CACTUS',183,f(9,True),'#a3bf91')
indexed(frame,OUT/'res41.png')

for n,(heading,lines) in STORIES.items():
    size=Image.open(GAME/f'data/TITLE/res{n}.png').size
    im=Image.new('RGBA',size,(0,0,0,0));font=f(12)
    widths=[ImageDraw.Draw(im).textlength(line,font=font) for line in lines]
    assert max(widths)<size[0]-8,(n,max(widths),size)
    assert len(lines)*14<=size[1],(n,size)
    y=(size[1]-len(lines)*14)//2
    for line in lines:
        pixel_text(im,(4,y),line,font,'white');y+=14
    indexed(im,OUT/f'res{n}.png',True)
    preview=frame.copy();preview.paste(im,(24,25),im)
    preview.resize((960,600),Image.Resampling.NEAREST).save(ART/f'historia_{n}.png')

main.resize((960,600),Image.Resampling.NEAREST).save(ART/'Tela_Inicial_MC.png')
for p,h in before.items():assert hashlib.sha256((GAME/p).read_bytes()).hexdigest()==h,p
for p in OUT.glob('*.png'):
    orig=Image.open(GAME/'data/TITLE'/p.name);actual=Image.open(p)
    assert actual.size==orig.size,(p.name,actual.size,orig.size)
    assert actual.mode=='P'

(ART/'narrativa.txt').write_text('MENINO CACTUS — O PALÁCIO DAS SOMBRAS\n\n'+'\n\n'.join(heading+'\n'+'\n'.join(lines) for heading,lines in STORIES.values())+'\n',encoding='utf-8-sig')
(ART/'LEIA-ME.txt').write_text('Arte original criada com a ferramenta integrada de geração de imagens, usando o desenho fornecido como referência.\nTítulo e textos rasterizados para os recursos nativos do SDLPoP.\nAbertura, segunda página e encerramento personalizados; cenas animadas permanecem as originais.\nA versão anterior está preservada em ../versoes/Menino_Cactus_v1_aprovado.zip.\n',encoding='utf-8-sig')
(QA/'historia_assets.json').write_text(json.dumps({'title_resources':[p.name for p in OUT.glob('*.png')],'engine_gameplay_and_base_assets_unchanged':True,'previous_version':'versoes/Menino_Cactus_v1_aprovado.zip'},indent=2))
p=GAME/'COMO JOGAR.txt';text=p.read_text(encoding='utf-8-sig')
text=text.replace('MENINO CACTUS - PRIMEIRA VERSÃO JOGÁVEL','MENINO CACTUS - O PALÁCIO DAS SOMBRAS')
if 'Abertura e encerramento' not in text:text+='\nAbertura e encerramento em português com narrativa própria do MC.\nAs cenas animadas da história são as originais do Prince of Persia.\n'
p.write_text(text,encoding='utf-8-sig')
print('Instalados título, arte de abertura e três páginas da história. Motor, fases e sprites preservados.')
