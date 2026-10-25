from pathlib import Path
import subprocess,os,time,json,hashlib,struct
ROOT=Path(__file__).resolve().parent
GAME=ROOT/'Menino_Cactus_Jogavel'
env={**os.environ,'SDL_VIDEODRIVER':'dummy','SDL_AUDIODRIVER':'dummy'}
def code_sections(b):
    pe=struct.unpack_from('<I',b,60)[0];n=struct.unpack_from('<H',b,pe+6)[0];size=struct.unpack_from('<H',b,pe+20)[0];out={}
    for i in range(n):
        off=pe+24+size+i*40;name,vs,va,rs,rp=struct.unpack_from('<8sIIII',b,off)
        if name.rstrip(b'\0')!=b'.rsrc':out[name]=b[rp:rp+rs] if rs else b''
    return out
# Starting the normal intro loads both TITLE image tables, including all three
# story pages and the palette that SDLPoP recolors at run time.
proc=subprocess.Popen([str(GAME/'prince.exe'),'mod','MeninoCactus','mute'],cwd=GAME,env=env,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
started=time.monotonic()
try:
    while time.monotonic()-started<45:
        if proc.poll() is not None:
            out,err=proc.communicate()
            raise RuntimeError(f'Intro exited early ({proc.returncode}): {out!r} {err!r}')
        time.sleep(.5)
    baseline=(ROOT/'preview/sdlpop/SDLPoP-1.23/prince.exe').read_bytes()
    old=b'Prince of Persia (SDLPoP) v1.23';new=b'Jogo Menino Cactus'
    branded=baseline.replace(old,new+b'\0'*(len(old)-len(new)))
    result={'normal_intro_alive_after_seconds':round(time.monotonic()-started),
            'mode':'SDL dummy video/audio; no interaction with the user desktop',
            'gameplay_code_unchanged_except_window_title':code_sections((GAME/'prince.exe').read_bytes()) in (code_sections(baseline),code_sections(branded)),
            'scope':'Intro runtime smoke test and image format/layout verification; not a full playthrough.'}
    assert result['gameplay_code_unchanged_except_window_title']
    (ROOT/'verificacao/abertura_runtime.json').write_text(json.dumps(result,indent=2))
    print(json.dumps(result))
finally:
    if proc.poll() is None:proc.terminate()
    proc.communicate(timeout=10)
