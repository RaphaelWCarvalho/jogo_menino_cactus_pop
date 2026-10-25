from pathlib import Path
from PIL import Image
import hashlib,json,shutil

ROOT=Path(__file__).resolve().parent
GAME=ROOT/'Menino_Cactus_Jogavel'
old=b'Prince of Persia (SDLPoP) v1.23'
new=b'Jogo Menino Cactus'
padded=new+b'\0'*(len(old)-len(new))
baseline=(ROOT/'preview/sdlpop/SDLPoP-1.23/prince.exe').read_bytes()
assert baseline.count(old)==1
expected=baseline.replace(old,padded)
exe=GAME/'prince.exe'
current=exe.read_bytes()
assert current in (baseline,expected),'Unexpected executable changes; refusing to patch.'
archive=ROOT/'versoes/Menino_Cactus_v2_historia.zip'
if not archive.exists():shutil.copy2(ROOT/'Menino_Cactus_Jogavel.zip',archive)
exe.write_bytes(expected)
# Match the corresponding source to the string-only change in the distributed binary.
source=GAME/'src/config.h'
text=source.read_text()
text=text.replace('#define WINDOW_TITLE "Prince of Persia (SDLPoP) v" SDLPOP_VERSION',
                  '#define WINDOW_TITLE "Jogo Menino Cactus"')
source.write_text(text)
start=baseline.index(old)
differences=[i for i,(a,b) in enumerate(zip(baseline,expected)) if a!=b]
assert len(baseline)==len(expected)
assert all(start<=i<start+len(old) for i in differences)
assert exe.read_bytes()==expected

art=Image.open(ROOT/'arte_mc/abertura_arte_original.png').convert('RGBA')
# Reuse the existing approved illustration as the shortcut's icon.
w,h=art.size
portrait=art.crop((int(w*.68),int(h*.07),int(w*.87),int(h*.37)))
portrait=portrait.resize((256,256),Image.Resampling.LANCZOS)
portrait.save(GAME/'Menino_Cactus.ico',sizes=[(16,16),(24,24),(32,32),(48,48),(64,64),(128,128),(256,256)])
result={'window_title':new.decode(),'only_changed_executable_region':[start,start+len(old)],
        'executable_length_unchanged':True,'changed_bytes':len(differences),
        'sha256':hashlib.sha256(expected).hexdigest()}
(ROOT/'verificacao/titulo_janela.json').write_text(json.dumps(result,indent=2))
print(json.dumps(result))
