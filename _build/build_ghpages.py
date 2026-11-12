"""GitHub Pages용 정적 사이트 생성기 (신영범세무회계사무소)
사용: python3 _build/build_ghpages.py <BASE_URL> <SRC_DIR> <OUT_DIR> [추가 사이트맵 경로들(쉼표 구분)]
SRC_DIR: claude.ai 홈페이지 아티팩트의 index.html 과 data/*.json 을 내려받은 폴더
OUT_DIR: 생성 결과. 저장소에는 index.html, assets-style.css, logo.png, sitemap.xml, robots.txt, blog/, guide/, data/ 만 복사합니다.
card/, navera*.html, README.md, _build/ 는 생성기가 다루지 않습니다."""
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
fonts = '<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin><link href="https://fonts.googleapis.com/css2?family=IBM+Plex+Sans+KR:wght@400;500;600;700&display=swap" rel="stylesheet">'
open(f'{OUT}/assets-style.css', 'w').write(css)
import base64
open(f'{OUT}/logo.png', 'wb').write(base64.b64decode(logo.split(',', 1)[1]))

def page(title, desc, path, body):
    url = f'{BASE}/{path}'
    return f'''<!DOCTYPE html><html lang="ko"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(title)}</title><meta name="description" content="{e(desc)}"><link rel="canonical" href="{url}">
<meta property="og:type" content="article"><meta property="og:title" content="{e(title)}"><meta property="og:description" content="{e(desc)}"><meta property="og:url" content="{url}">
{fonts}<link rel="stylesheet" href="/assets-style.css"></head><body>
<header class="top"><div class="wrap"><a class="brand" href="/"><img class="logo" src="/logo.png" alt="{e(office['name'])} 로고"><span><b>{e(office['name'])}</b><small>부산·경남 세무·회계</small></span></a>
<nav class="main" style="display:flex"><a href="/">홈</a><a href="/#guide">세목별 안내</a><a href="/blog/">세무 블로그</a><a href="/#contact" class="call">상담 신청</a></nav></div></header>
<main><section class="block"><div class="wrap"><div class="post-wrap">{body}
<div class="cta"><div class="in"><h3>상담 문의</h3><p>{e(office['hours'])}</p><div class="lines num"><span>전화 <b>{e(office['phone'])}</b></span><span>휴대전화 <b>{e(office.get('mobile',''))}</b></span><span>{e(office['email'])}</span></div><div class="btns"><a class="btn foil" href="/#contact">상담 신청</a></div></div></div><div class="band"><i></i><i></i></div>
</div></div></section></main>
<footer><div class="wrap"><b>{e(office['name'])}</b> · {e(office['ceo'])}<br>{e(office['address'])}<br>전화 {e(office['phone'])} · 팩스 {e(office['fax'])} · {e(office['email'])}</div><div class="band"><i></i><i></i></div></footer></body></html>'''

urls = [('', '1.0')]
for p in posts:
    body = f'<a class="more" href="/blog/">세무 블로그 목록</a><div class="meta" style="margin-top:22px"><span class="tag">{e(p["category"])}</span><span>{p["date"]}</span><span>대상: {e(p["target"])}</span><span>{e(office["ceo"])}</span></div><h1>{e(p["title"])}</h1><article class="post-body">{p["body"].replace("<table>","<div class=\"tblwrap\"><table>").replace("</table>","</table></div>")}<div class="kw">{"".join(f"<span>#{e(k)}</span>" for k in p["keywords"])}</div></article>'
    open(f'{OUT}/blog/{p["id"]}.html', 'w').write(page(f'{p["title"]} | {office["name"]}', p['summary'], f'blog/{p["id"]}.html', body))
    urls.append((f'blog/{p["id"]}.html', '0.8'))
lst = ''.join(f'<a class="post" href="/blog/{p["id"]}.html"><div class="pd num">{p["date"]}<br><span class="tag">{e(p["category"])}</span></div><div><h3>{e(p["title"])}</h3><p>{e(p["summary"])}</p></div></a>' for p in posts)
open(f'{OUT}/blog/index.html', 'w').write(page(f'세무 블로그 | {office["name"]}', '부산·경남 신영범세무회계사무소의 세법 해설과 절세 가이드', 'blog/', f'<h1>세무 블로그</h1><div class="posts">{lst}</div>'))
urls.append(('blog/', '0.9'))
for g in guides['items']:
    t = g['name'] if g['name'].endswith('안내') else g['name'] + ' 안내'
    rows = ''.join(f'<tr><td>{e(r[0])}</td><td><b>{e(r[1])}</b></td><td>{e(r[2])}</td></tr>' for r in g['deadlines'])
    body = (f'<a class="more" href="/#guide">세목별 안내</a><h1 style="margin-top:18px">{e(t)}</h1><p class="meta">대상: {e(g["who"])}</p>'
            f'<div class="post-body"><p class="lead">{e(g["lead"])}</p><h3>기한·절차</h3><div class="tblwrap"><table><thead><tr><th>구분</th><th>기한</th><th>비고</th></tr></thead><tbody>{rows}</tbody></table></div>'
            f'<h3>준비 서류</h3><ul>{"".join(f"<li>{e(d)}</li>" for d in g["docs"])}</ul><h3>알아두실 점</h3><ul>{"".join(f"<li>{e(n)}</li>" for n in g["notes"])}</ul>'
            + (f'<p><a class="btn outline" href="/#guide-{g["id"]}">모의계산 해 보기</a></p>' if g.get('calc') else '') + '</div>')
    open(f'{OUT}/guide/{g["id"]}.html', 'w').write(page(f'{t} | {office["name"]}', g['lead'], f'guide/{g["id"]}.html', body))
    urls.append((f'guide/{g["id"]}.html', '0.7'))
for p in EXTRA: urls.append((p, '0.6'))
# index: SEO meta + crawlable link list
links = '<nav aria-label="전체 페이지" style="position:absolute;left:-9999px">' + ''.join(f'<a href="/blog/{p["id"]}.html">{e(p["title"])}</a>' for p in posts) + ''.join(f'<a href="/guide/{g["id"]}.html">{e(g["name"])}</a>' for g in guides['items']) + '</nav>'
seo = f'<link rel="canonical" href="{BASE}/"><meta property="og:type" content="website"><meta property="og:title" content="{e(office["name"])} | 부산·경남 세무사"><meta property="og:description" content="법인세·부가가치세·종합소득세·양도·상속·증여 상담. 최신 세법 개정 소식 매주 업데이트."><meta property="og:url" content="{BASE}/">'
out_idx = idx.replace('</head>', seo + '\n</head>', 1).replace('<main id="app">', links + '\n<main id="app">', 1)
open(f'{OUT}/index.html', 'w').write(out_idx)
today = laws['updated']
open(f'{OUT}/sitemap.xml', 'w').write('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + ''.join(f'<url><loc>{BASE}/{u}</loc><lastmod>{today}</lastmod><priority>{pr}</priority></url>\n' for u, pr in urls) + '</urlset>\n')
open(f'{OUT}/robots.txt', 'w').write(f'User-agent: *\nAllow: /\nSitemap: {BASE}/sitemap.xml\n')
print('pages:', len(urls))
