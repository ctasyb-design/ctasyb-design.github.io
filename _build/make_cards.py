# 블로그 글 대표 이미지(1080x1080) 생성기
# 사용: python3 _build/make_cards.py <posts.json> <출력 폴더>
# posts.json 각 글의 "card": {top, l1, l2, l3, gold, gray} 로 <출력 폴더>/<글 id>.png 를 만듭니다.
import json, os, sys, glob
from PIL import Image, ImageDraw, ImageFont
cand = glob.glob('/usr/share/fonts/**/NotoSansCJK-*.ttc', recursive=True)
DIR = os.path.dirname(cand[0]) if cand else None
def f(w, s): return ImageFont.truetype(os.path.join(DIR, f'NotoSansCJK-{w}.ttc'), s, index=1)
BAND=(122,143,203); BG=(238,242,250); BOX=(255,255,255); BOXLINE=(185,196,228)
IND=(38,47,107); BLUE=(52,104,170); GOLD=(168,123,46); SUB=(96,104,124); WHITE=(255,255,255)
def card(path, c, foot="상담문의: 051-312-3514"):
    W=1080; im=Image.new('RGB',(W,W),BG); d=ImageDraw.Draw(im)
    def fit(t, w, size, maxw):
        s=size
        while d.textlength(t,font=f(w,s))>maxw and s>20: s-=2
        return f(w,s)
    def ct(y, t, font, col):
        d.text(((W-d.textlength(t,font=font))/2,y), t, font=font, fill=col)
    d.rectangle([0,0,W,150], fill=BAND); ct(48, c['top'], f('Bold',44), WHITE)
    d.rectangle([0,W-150,W,W], fill=BAND); ct(W-108, foot, f('Bold',44), WHITE)
    d.rounded_rectangle([90,250,W-90,830], radius=22, fill=BOX, outline=BOXLINE, width=4)
    ct(320, c['l1'], fit(c['l1'],'Black',66,840), BLUE)
    ct(420, c['l2'], fit(c['l2'],'Bold',54,840), IND)
    ct(505, c['l3'], fit(c['l3'],'Black',100,840), IND)
    ct(680, c['gold'], fit(c['gold'],'Medium',34,840), GOLD)
    ct(734, c['gray'], fit(c['gray'],'Medium',34,840), SUB)
    im.save(path, optimize=True)
if __name__ == '__main__':
    posts = json.load(open(sys.argv[1]))['items']; out = sys.argv[2]; os.makedirs(out, exist_ok=True)
    n = 0
    for p in posts:
        if p.get('card'):
            card(os.path.join(out, p['id'] + '.png'), p['card']); n += 1
    print(f'{n} cards -> {out}')
