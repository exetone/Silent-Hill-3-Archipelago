"""Generate the release title from blank artwork and the APWorld version.
Uses the established 512-square -> visible rows 32..479 conversion, RGBA/0..128.
Requires Pillow at build time only. Font is an explicit build input.
"""
from pathlib import Path
import argparse,ast,hashlib,json
from PIL import Image,ImageDraw,ImageFont
p=argparse.ArgumentParser();p.add_argument('--image',type=Path,required=True);p.add_argument('--font',type=Path,required=True);p.add_argument('--stage',type=Path,required=True);p.add_argument('--preview',type=Path,required=True);a=p.parse_args()
version=next(ast.literal_eval(n.value) for n in ast.parse((a.stage/'data.py').read_text()).body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='CLIENT_VERSION' for t in n.targets))
im=Image.open(a.image).convert('RGBA');w,h=im.size
font=ImageFont.truetype(str(a.font),round(h*24/1080));draw=ImageDraw.Draw(im)
label='SH3AP v'+version;x=round(w*18/1440);bottom=round(h*14/1080);box=draw.textbbox((0,0),label,font=font);y=h-bottom-box[3]
draw.text((x+1,y+1),label,font=font,fill=(0,0,0,255));draw.text((x,y),label,font=font,fill=(255,255,255,255))
a.preview.parent.mkdir(parents=True,exist_ok=True);im.save(a.preview)
scale=512/min(w,h);stage1=im.resize((round(w*scale),round(h*scale)),Image.Resampling.BICUBIC)
fit=stage1.resize((512,512),Image.Resampling.BICUBIC)
tex=Image.new('RGBA',(512,512),(0,0,0,255));tex.paste(fit.resize((512,448),Image.Resampling.BICUBIC),(0,32))
raw=bytearray(tex.tobytes())
for i in range(3,len(raw),4):raw[i]=min(128,round(raw[i]*128/255))
dest=a.stage/'defaults';(dest/'ap_title.rgba').write_bytes(raw)
(dest/'title_manifest.json').write_text(json.dumps({'version':version,'label':label,'sha256':hashlib.sha256(raw).hexdigest(),'image_sha256':hashlib.sha256(a.image.read_bytes()).hexdigest(),'font_sha256':hashlib.sha256(a.font.read_bytes()).hexdigest(),'source_label':{'x':x,'y':y,'size':round(h*24/1080)},'texture':'512x512 RGBA; alpha 0..128; visible rows32..479'},indent=2)+'\n')
