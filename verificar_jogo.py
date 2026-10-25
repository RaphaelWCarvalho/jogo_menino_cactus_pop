from pathlib import Path
import subprocess, os, json, hashlib
from PIL import Image, ImageChops
ROOT=Path(__file__).resolve().parent
BASE=ROOT/'preview/sdlpop/SDLPoP-1.23'
GAME=ROOT/'Menino_Cactus_Jogavel'
QA=ROOT/'verificacao'
env={**os.environ,'SDL_VIDEODRIVER':'dummy','SDL_AUDIODRIVER':'dummy'}
results=[]
for name in ['Grab bug (PR288).p1r','Original level 2 falling into wall.p1r','Original level 5 shadow into wall.p1r']:
    src=BASE/'doc/replays-testcases'/name
    raw=src.read_bytes();assert raw[:3]==b'P1R' and raw[15]==0
    modname=b'MeninoCactus'
    custom=QA/('MC_'+name);custom.write_bytes(raw[:15]+bytes([len(modname)])+modname+raw[16:])
    logs=[]
    for folder,replay in [(BASE,src),(GAME,custom)]:
        p=subprocess.run([str(folder/'prince.exe'),'validate',str(replay),'mute'],cwd=folder,env=env,capture_output=True,timeout=30)
        output=p.stdout.decode(errors='replace')+p.stderr.decode(errors='replace')
        # SDL's Windows entry point may redirect its output to files.
        if 'Replay ended' not in output and (folder/'stdout.txt').exists():output+=(folder/'stdout.txt').read_text(errors='replace')
        logs.append(output)
        (QA/((('MC_' if folder==GAME else 'Original_')+src.stem)+'.log')).write_text(output)
        assert p.returncode==0,(name,p.returncode,output)
        assert 'Replay ended' in output,(name,output)
        assert 'Play duration matches replay length' in output,(name,output)
    summary=[s[s.index('Replay ended'):].strip() for s in logs]
    assert summary[0]==summary[1],summary
    results.append({'replay':name,'original_and_mc_identical':True,'result':summary[1]})

for folder in [BASE,GAME]:
    before=set((folder/'screenshots').glob('*.png'))
    p=subprocess.run([str(folder/'prince.exe'),'megahit','4','--screenshot','mute'],cwd=folder,env=env,capture_output=True,timeout=20)
    # SDLPoP 1.23 deliberately calls quit(1) after an automatic screenshot.
    new=set((folder/'screenshots').glob('*.png'))-before
    assert p.returncode==1 and len(new)==1,(p.returncode,p.stderr)
    shot=new.pop()
    Image.open(shot).save(QA/('MC_no_jogo.png' if folder==GAME else 'Original_no_jogo.png'))
a=Image.open(QA/'Original_no_jogo.png').convert('RGB');b=Image.open(QA/'MC_no_jogo.png').convert('RGB')
box=ImageChops.difference(a,b).getbbox();assert box is not None
# The only changed pixels should be in the prince's costume at the start of level 4.
assert box[0]>=216 and box[2]<=244 and box[1]>=70 and box[3]<=124,box
results.append({'static_visual_difference_bbox':box,'scenery_unchanged':True})
b.resize((960,600),Image.Resampling.NEAREST).save(GAME/'Menino_Cactus_no_jogo.png')
(QA/'testes.json').write_text(json.dumps(results,indent=2))
print(json.dumps(results,indent=2))
