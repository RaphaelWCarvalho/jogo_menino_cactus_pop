"""Use the approved cover portrait for the shortcut, executable and SDL window icons."""
from pathlib import Path
import ctypes,struct,shutil,json,os
from ctypes import wintypes
from PIL import Image,ImageDraw

ROOT=Path(__file__).resolve().parent;GAME=ROOT/'Menino_Cactus_Jogavel'
art=Image.open(ROOT/'arte_mc/abertura_arte_original.png').convert('RGBA')
w,h=art.size
portrait=art.crop((int(w*.69),int(h*.065),int(w*.86),int(h*.065)+int(w*.17)))
portrait=portrait.resize((256,256),Image.Resampling.LANCZOS)
mask=Image.new('L',(256,256));d=ImageDraw.Draw(mask);d.rounded_rectangle((0,0,255,255),radius=42,fill=255)
portrait.putalpha(mask)
d=ImageDraw.Draw(portrait);d.rounded_rectangle((3,3,252,252),radius=39,outline='#edca57',width=5)
portrait.save(ROOT/'arte_mc/Icone_Menino_Cactus.png')
ico=GAME/'Menino_Cactus_rosto.ico'
portrait.save(ico,sizes=[(16,16),(24,24),(32,32),(48,48),(64,64),(128,128),(256,256)])
shutil.copy2(ico,GAME/'Menino_Cactus.ico')
shutil.copy2(ico,GAME/'src/icon.ico')
portrait.resize((64,64),Image.Resampling.LANCZOS).save(GAME/'data/icon.png')

def sections(b):
    pe=struct.unpack_from('<I',b,60)[0];n=struct.unpack_from('<H',b,pe+6)[0];size=struct.unpack_from('<H',b,pe+20)[0];out={}
    for i in range(n):
        off=pe+24+size+i*40;name,vs,va,rs,rp=struct.unpack_from('<8sIIII',b,off)
        out[name.rstrip(b'\0').decode()]=b[rp:rp+rs] if rs else b''
    return out

exe=GAME/'prince.exe';before=exe.read_bytes()
backup=ROOT/'versoes/prince_antes_do_icone.exe'
if not backup.exists():shutil.copy2(exe,backup)
staged=GAME/'prince_icone.tmp.exe';shutil.copy2(exe,staged)
kernel=ctypes.WinDLL('kernel32',use_last_error=True)
kernel.BeginUpdateResourceW.argtypes=[wintypes.LPCWSTR,wintypes.BOOL];kernel.BeginUpdateResourceW.restype=wintypes.HANDLE
kernel.UpdateResourceW.argtypes=[wintypes.HANDLE,ctypes.c_void_p,ctypes.c_void_p,wintypes.WORD,ctypes.c_void_p,wintypes.DWORD];kernel.UpdateResourceW.restype=wintypes.BOOL
kernel.EndUpdateResourceW.argtypes=[wintypes.HANDLE,wintypes.BOOL];kernel.EndUpdateResourceW.restype=wintypes.BOOL
handle=kernel.BeginUpdateResourceW(str(staged),False)
if not handle:raise ctypes.WinError(ctypes.get_last_error())
raw=ico.read_bytes();_,kind,count=struct.unpack_from('<HHH',raw)
group=bytearray(struct.pack('<HHH',0,1,count))
try:
    for i in range(count):
        wi,he,col,res,planes,bits,size,offset=struct.unpack_from('<BBBBHHII',raw,6+i*16)
        data=raw[offset:offset+size];buf=ctypes.create_string_buffer(data)
        if not kernel.UpdateResourceW(handle,ctypes.c_void_p(3),ctypes.c_void_p(i+1),1033,buf,len(data)):raise ctypes.WinError(ctypes.get_last_error())
        group.extend(struct.pack('<BBBBHHIH',wi,he,col,res,planes,bits,size,i+1))
    buf=ctypes.create_string_buffer(bytes(group));name=ctypes.c_wchar_p('A')
    if not kernel.UpdateResourceW(handle,ctypes.c_void_p(14),ctypes.cast(name,ctypes.c_void_p),1033,buf,len(group)):raise ctypes.WinError(ctypes.get_last_error())
except:
    kernel.EndUpdateResourceW(handle,True);raise
if not kernel.EndUpdateResourceW(handle,False):raise ctypes.WinError(ctypes.get_last_error())
after=staged.read_bytes()
sb=sections(before);sa=sections(after)
for name,data in sb.items():
    if name!='.rsrc':assert sa[name]==data,name
os.replace(staged,exe)
result={'icon':'Menino_Cactus_rosto.ico','sizes':[16,24,32,48,64,128,256],
        'executable_code_and_all_non_resource_sections_unchanged':True,
        'window_icon':'data/icon.png','group_name':'A','resource_language':1033}
(ROOT/'verificacao/icone.json').write_text(json.dumps(result,indent=2))
print(json.dumps(result))
