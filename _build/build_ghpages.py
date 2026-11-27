"""GitHub Pages용 정적 사이트 생성기 (신영범세무회계사무소)
사용: python3 _build/build_ghpages.py <BASE_URL> <SRC_DIR> <OUT_DIR> [추가 사이트맵 경로들(쉼표 구분)]
SRC_DIR: claude.ai 홈페이지 아티팩트의 index.html 과 data/*.json 을 내려받은 폴더
OUT_DIR: 생성 결과. 저장소에는 index.html, assets-style.css, logo.png, sitemap.xml, robots.txt, blog/, guide/, data/ 만 복사합니다.
card/, navera*.html, README.md, _build/ 는 생성기가 다루지 않습니다.
본문 HTML은 clean()으로 허용 태그만 남기고, 모든 페이지에 보안 설정(CSP)·저작권 문구를 넣습니다."""
import json, os, re, shutil, sys, html
BASE, SRC, OUT = sys.argv[1].rstrip('/'), sys.argv[2], sys.argv[3]
EXTRA = [p for p in (sys.argv[4].split(',') if len(sys.argv) > 4 else []) if p]
if os.path.exists(OUT): shutil.rmtree(OUT)
os.makedirs(OUT + '/data'); os.makedirs(OUT + '/blog'); os.makedirs(OUT + '/guide')
for f in os.listdir(SRC + '/data'): shutil.copy(f'{SRC}/data/{f}', f'{OUT}/data/{f}')
idx = open(SRC + '/index.html').read()
office = json.load(open(SRC + '/data/office.json')); laws = json.load(open(SRC + '/data/laws.json'))
posts = sorted(json.load(open(SRC + '/data/posts.json'))['items'], key=lambda p: p['date'], reverse=True)
guides = json.load(open(SRC + '/data/guides.json'))
css = re.search(r'<style>(.*?)</style>', idx, re.S).group(1)
logo = re.search(r'class="logo" src="(data:image/png;base64,[^"]+)"', idx).group(1)
e = html.escape
from html.parser import HTMLParser
SAFE_TAGS = {'p','h2','h3','h4','ul','ol','li','strong','b','em','i','br','table','thead','tbody','tfoot','tr','th','td','div','span','small','blockquote','a','sup','sub','hr','caption'}
DROP_TAGS = {'script','style','iframe','object','embed','form','input','button','textarea','select','link','meta','svg','math','img','video','audio','source','template','noscript'}
SAFE_ATTR = {'class','colspan','rowspan','data-lead'}
class _Clean(HTMLParser):
    """본문 HTML 허용 목록 필터: 스크립트·이벤트 속성·외부 삽입 요소를 제거"""
    def __init__(self): super().__init__(convert_charrefs=False); self.out=[]; self.skip=0
    def handle_starttag(self, t, attrs, close=False):
        if t in DROP_TAGS:
            if not close and t not in ('img','input','link','meta','source','br','hr'): self.skip += 1
            return
        if self.skip or t not in SAFE_TAGS: return
        keep = []
        for k, v in attrs:
            v = v or ''
            if t == 'a' and k == 'href':
                if re.match(r'^(https://|#|/)', v.strip(), re.I): keep.append((k, v))
            elif k in SAFE_ATTR: keep.append((k, v))
        if t == 'a' and any(k == 'href' and v.startswith('https://') for k, v in keep): keep += [('target','_blank'),('rel','noopener noreferrer')]
        self.out.append('<' + t + ''.join(f' {k}="{e(v)}"' for k, v in keep) + ('/>' if close else '>'))
    def handle_startendtag(self, t, attrs): self.handle_starttag(t, attrs, True)
    def handle_endtag(self, t):
        if t in DROP_TAGS:
            if t not in ('img','input','link','meta','source','br','hr') and self.skip: self.skip -= 1
            return
        if not self.skip and t in SAFE_TAGS and t not in ('br','hr'): self.out.append(f'</{t}>')
    def handle_data(self, d):
        if not self.skip: self.out.append(d)
    def handle_entityref(self, n):
        if not self.skip: self.out.append(f'&{n};')
    def handle_charref(self, n):
        if not self.skip: self.out.append(f'&#{n};')
def clean(h):
    c = _Clean(); c.feed(h or ''); c.close()
    return ''.join(c.out).replace('<table>', '<div class="tblwrap"><table>').replace('</table>', '</table></div>')
YEAR = __import__('datetime').date.today().year
def rights(d, kind):
    return (f'<p class="rights">© {YEAR} {e(office["name"])}. 이 {kind}은 대표세무사 신영범이 법령·예규를 확인해 직접 작성했습니다. 출처를 밝히지 않은 전재·재배포와 상업적 이용을 금합니다. '
            f'{e(d)} 시행 법령 기준의 일반 정보이며, 개별 사안에 대한 세무 자문을 대신하지 않습니다. 법령 원문: <a href="https://www.law.go.kr" target="_blank" rel="noopener noreferrer">국가법령정보센터</a></p>')
# 정적 페이지 보안 설정: 스크립트 실행 금지, 외부 자원은 글꼴만 허용
CSP_STATIC = "default-src 'self'; script-src 'none'; style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; font-src https://fonts.gstatic.com; img-src 'self' data:; connect-src 'none'; object-src 'none'; base-uri 'self'; form-action 'none'"
CSP_INDEX = "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; font-src https://fonts.gstatic.com; img-src 'self' data:; connect-src 'self'; object-src 'none'; base-uri 'self'; form-action 'self'"
SEC_META = lambda csp: f'<meta http-equiv="Content-Security-Policy" content="{csp}"><meta name="referrer" content="strict-origin-when-cross-origin">'
fonts = '<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin><link href="https://fonts.googleapis.com/css2?family=IBM+Plex+Sans+KR:wght@400;500;600;700&display=swap" rel="stylesheet">'
open(f'{OUT}/assets-style.css', 'w').write(css)
import base64
open(f'{OUT}/logo.png', 'wb').write(base64.b64decode(logo.split(',', 1)[1]))

def page(title, desc, path, body, image=None):
    url = f'{BASE}/{path}'
    og_img = f'<meta property="og:image" content="{BASE}/{image}">' if image else ''
    return f'''<!DOCTYPE html><html lang="ko"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">{SEC_META(CSP_STATIC)}
<title>{e(title)}</title><meta name="description" content="{e(desc)}"><link rel="canonical" href="{url}">
<meta property="og:type" content="article"><meta property="og:title" content="{e(title)}"><meta property="og:description" content="{e(desc)}"><meta property="og:url" content="{url}">{og_img}
{fonts}<link rel="stylesheet" href="/assets-style.css"></head><body>
<header class="top"><div class="wrap"><a class="brand" href="/"><img class="logo" src="/logo.png" alt="{e(office['name'])} 로고"><span><b>{e(office['name'])}</b><small>부산·경남 세무·회계</small></span></a>
<nav class="main" style="display:flex"><a href="/">홈</a><a href="/#guide">세목별 안내</a><a href="/blog/">세무 블로그</a><a href="/column/">세무 칼럼</a><a href="https://blog.naver.com/ctasyb" target="_blank" rel="noopener">네이버 블로그</a><a href="/#contact" class="call">상담 신청</a></nav></div></header>
<main><section class="block"><div class="wrap"><div class="post-wrap">{body}
<div class="cta"><div class="in"><h3>상담 문의</h3><p>{e(office['hours'])}</p><div class="lines num"><span>전화 <b>{e(office['phone'])}</b></span><span>휴대전화 <b>{e(office.get('mobile',''))}</b></span><span>{e(office['email'])}</span></div><div class="btns"><a class="btn foil" href="/#contact">상담 신청</a></div></div></div><div class="band"><i></i><i></i></div>
</div></div></section></main>
<footer><div class="wrap"><b>{e(office['name'])}</b> · {e(office['ceo'])}<br>{e(office['address'])}<br>전화 {e(office['phone'])} · 팩스 {e(office['fax'])} · {e(office['email'])}<br><small>© {YEAR} {e(office['name'])}. 이 사이트의 글·이미지는 사무소가 직접 작성·제작했으며 무단 복제·배포를 금합니다.</small></div><div class="band"><i></i><i></i></div></footer></body></html>'''

def card_img(p):
    if not p.get('card'): return ''
    c = p['card']; alt = e(f"{c['l1']} {c['l2']} {c['l3']}")
    return f'<img class="post-card" src="/cards/{p["id"]}.png" alt="{alt}">'
def thumb(p):
    return f'<img class="pthumb" src="/cards/{p["id"]}.png" alt="" loading="lazy">' if p.get('card') else ''
import shutil
if os.path.isdir(os.path.join(SRC, 'cards')):
    shutil.copytree(os.path.join(SRC, 'cards'), os.path.join(OUT, 'cards'), dirs_exist_ok=True)

urls = [('', '1.0')]
for p in posts:
    body = f'<a class="more" href="/blog/">세무 블로그 목록</a><div class="meta" style="margin-top:22px"><span class="tag">{e(p["category"])}</span><span>{p["date"]}</span><span>대상: {e(p["target"])}</span><span>{e(office["ceo"])}</span></div><h1>{e(p["title"])}</h1>{card_img(p)}<article class="post-body">{clean(p["body"])}<div class="kw">{"".join(f"<span>#{e(k)}</span>" for k in p["keywords"])}</div>{rights(p["date"], "글")}</article>'
    open(f'{OUT}/blog/{p["id"]}.html', 'w').write(page(f'{p["title"]} | {office["name"]}', p['summary'], f'blog/{p["id"]}.html', body, f'cards/{p["id"]}.png' if p.get('card') else None))
    urls.append((f'blog/{p["id"]}.html', '0.8'))
lst = ''.join(f'<a class="post{" has-card" if p.get("card") else ""}" href="/blog/{p["id"]}.html"><div class="pd num">{p["date"]}<br><span class="tag">{e(p["category"])}</span></div><div><h3>{e(p["title"])}</h3><p>{e(p["summary"])}</p></div>{thumb(p)}</a>' for p in posts)
open(f'{OUT}/blog/index.html', 'w').write(page(f'세무 블로그 | {office["name"]}', '부산·경남 신영범세무회계사무소의 세법 해설과 절세 가이드', 'blog/', f'<h1>세무 블로그</h1><div class="posts">{lst}</div>'))
urls.append(('blog/', '0.9'))
_cp = os.path.join(SRC, 'data', 'columns.json')
_allcols = sorted(json.load(open(_cp))['items'], key=lambda c: c['no'], reverse=True) if os.path.exists(_cp) else []
def gcols(g):
    cs = [c for c in _allcols if c['category'] == g['name']]
    if not cs: return ''
    items = ''.join(f'<a href="/column/{c["id"]}.html"><span class="no num">{c["no"]}</span><div><h3>{e(c["title"])}</h3><p>{e(c["summary"])}</p></div></a>' for c in cs)
    return f'<h2 style="font-size:22px;margin-top:40px">{e(g["name"])} 세무 칼럼 ({len(cs)}편)</h2><div class="col-list">{items}</div>'
for g in guides['items']:
    t = g['name'] if g['name'].endswith('안내') else g['name'] + ' 안내'
    rows = ''.join(f'<tr><td>{e(r[0])}</td><td><b>{e(r[1])}</b></td><td>{e(r[2])}</td></tr>' for r in g['deadlines'])
    body = (f'<a class="more" href="/#guide">세목별 안내</a><h1 style="margin-top:18px">{e(t)}</h1><p class="meta">대상: {e(g["who"])}</p>'
            f'<div class="post-body"><p class="lead">{e(g["lead"])}</p><h3>기한·절차</h3><div class="tblwrap"><table><thead><tr><th>구분</th><th>기한</th><th>비고</th></tr></thead><tbody>{rows}</tbody></table></div>'
            f'<h3>준비 서류</h3><ul>{"".join(f"<li>{e(d)}</li>" for d in g["docs"])}</ul><h3>알아두실 점</h3><ul>{"".join(f"<li>{e(n)}</li>" for n in g["notes"])}</ul>'
            + (f'<p><a class="btn outline" href="/#guide-{g["id"]}">모의계산 해 보기</a></p>' if g.get('calc') else '') + '</div>'
            + gcols(g))
    open(f'{OUT}/guide/{g["id"]}.html', 'w').write(page(f'{t} | {office["name"]}', g['lead'], f'guide/{g["id"]}.html', body))
    urls.append((f'guide/{g["id"]}.html', '0.7'))
glst = ''.join(f'<a class="post" href="/guide/{g["id"]}.html"><div><h3>{e(g["name"])}</h3><p>{e(g["lead"])}</p></div></a>' for g in guides['items'])
open(f'{OUT}/guide/index.html', 'w').write(page(f'세목별 안내 | {office["name"]}', '종합소득세·부가가치세·법인세·양도·상속·증여세 신고 기한과 준비 서류 안내', 'guide/', f'<h1>세목별 안내</h1><div class="posts">{glst}</div>'))
urls.append(('guide/', '0.8'))
cols_path = os.path.join(SRC, 'data', 'columns.json')
cols = sorted(json.load(open(cols_path))['items'], key=lambda c: c['no'], reverse=True) if os.path.exists(cols_path) else []
if cols:
    os.makedirs(f'{OUT}/column', exist_ok=True)
    for c in cols:
        same = [x for x in cols if x['category'] == c['category'] and x['id'] != c['id']][:4]
        rel = ''.join(f'<a href="/column/{x["id"]}.html"><span class="no num">{x["no"]}</span><div><h3>{e(x["title"])}</h3><p>{e(x["summary"])}</p></div></a>' for x in same)
        body = (f'<a class="more" href="/column/">세무 칼럼 목록</a><div class="meta" style="margin-top:22px"><span class="tag">{e(c["category"])}</span><span>칼럼 {c["no"]}</span><span>{c["date"]}</span><span>{e(office["ceo"])}</span></div><h1>{e(c["title"])}</h1>'
                f'<article class="post-body">{clean(c["body"])}<div class="kw">{"".join(f"<span>#{e(k)}</span>" for k in c.get("keywords", []))}</div>{rights(c["date"], "칼럼")}</article>'
                + (f'<h2 style="font-size:22px;margin-top:40px">같은 분야 칼럼</h2><div class="col-list">{rel}</div>' if rel else ''))
        open(f'{OUT}/column/{c["id"]}.html', 'w').write(page(f'{c["title"]} | {office["name"]}', c['summary'], f'column/{c["id"]}.html', body))
        urls.append((f'column/{c["id"]}.html', '0.7'))
    ORDER = ['양도소득세','증여세','상속세','종합소득세','법인세','부가가치세','세액공제·감면','재산세·종합부동산세']
    cats = sorted({c['category'] for c in cols}, key=lambda k: ORDER.index(k) if k in ORDER else 99)
    row = lambda c: f'<a href="/column/{c["id"]}.html"><span class="no num">{c["no"]}</span><div><h3><span class="tag">{e(c["category"])}</span>{e(c["title"])}</h3><p>{e(c["summary"])}</p></div></a>'
    chips = '<div class="filters"><span class="flabel">구분</span>' + f'<a class="chip on" href="#all">전체({len(cols)})</a>' + ''.join(f'<a class="chip" href="#cat-{i}">{e(k)}({sum(1 for c in cols if c["category"]==k)})</a>' for i, k in enumerate(cats)) + '</div>'
    secs = ''.join(f'<h2 id="cat-{i}" style="font-size:22px;margin-top:36px">{e(k)}({sum(1 for c in cols if c["category"]==k)})</h2><div class="col-list">' + ''.join(row(c) for c in cols if c['category'] == k) + '</div>' for i, k in enumerate(cats))
    open(f'{OUT}/column/index.html', 'w').write(page(f'세무 칼럼 | {office["name"]}', '양도·증여·상속·종합소득세·법인세 실무 쟁점을 법령 근거와 숫자로 정리한 신영범 세무사의 세무 칼럼', 'column/', f'<h1 id="all">세무 칼럼</h1><p class="meta">총 {len(cols)}편 · 매일 업데이트</p>{chips}{secs}'))
    urls.append(('column/', '0.9'))
for p in EXTRA: urls.append((p, '0.6'))
# index: SEO meta + crawlable link list
links = ('<nav class="sitelinks" aria-label="전체 글 목록" style="max-width:1120px;margin:0 auto;padding:18px 24px 26px;font-size:14px;color:#5b6475">'
         f'전체 글 목록: <a href="/blog/">세무 블로그 {len(posts)}편</a> · <a href="/column/">세무 칼럼 {len(cols)}편</a> · <a href="/guide/">세목별 안내 {len(guides["items"])}개</a> · <a href="/sitemap.xml">사이트맵</a></nav>')
seo = f'<link rel="canonical" href="{BASE}/"><meta property="og:type" content="website"><meta property="og:title" content="{e(office["name"])} | 부산·경남 세무사"><meta property="og:description" content="법인세·부가가치세·종합소득세·양도·상속·증여 상담. 최신 세법 개정 소식 매주 업데이트."><meta property="og:url" content="{BASE}/">'
out_idx = idx.replace('<head>', '<head>' + SEC_META(CSP_INDEX), 1).replace('</head>', seo + '\n</head>', 1)
cut = out_idx.rfind('</body>')
out_idx = out_idx[:cut] + links + '\n' + out_idx[cut:] if cut >= 0 else out_idx + links
open(f'{OUT}/index.html', 'w').write(out_idx)
today = laws['updated']
open(f'{OUT}/sitemap.xml', 'w').write('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + ''.join(f'<url><loc>{BASE}/{u}</loc><lastmod>{today}</lastmod><priority>{pr}</priority></url>\n' for u, pr in urls) + '</urlset>\n')
open(f'{OUT}/robots.txt', 'w').write(f'User-agent: *\nAllow: /\nSitemap: {BASE}/sitemap.xml\n')
print('pages:', len(urls))
