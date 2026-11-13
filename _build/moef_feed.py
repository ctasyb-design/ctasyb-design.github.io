"""재정경제부(옛 기획재정부) 보도자료 → feeds/moef.json
사용: python3 _build/moef_feed.py <OUT_JSON>
여러 공식 RSS 후보를 차례로 시도하고, 처음으로 항목을 돌려준 곳을 씁니다. 모두 실패하면 기존 파일을 그대로 둡니다."""
import json, re, sys, html, urllib.request, email.utils, datetime
import xml.etree.ElementTree as ET
OUT = sys.argv[1]
KST = datetime.timezone(datetime.timedelta(hours=9))
MINISTRY = "재정경제부"
CANDIDATES = [
    ("재정경제부 누리집 RSS", "https://www.mofe.go.kr/com/detailRssTagService.do?bbsId=MOSFBBS_000000000028", False),
    ("정책브리핑 부처별 RSS", "https://www.korea.kr/rss/dept_mofe.xml", False),
    ("정책브리핑 보도자료 RSS", "https://www.korea.kr/rss/pressrelease.xml", True),
]
TAX = re.compile(r"세제|세법|조세|과세|비과세|감면|세액|공제|소득세|법인세|부가가치세|부가세|상속세|증여세|종부세|종합부동산|양도세|양도소득|관세|국세|지방세|세수|개별소비세|교통세|증권거래세|가산세|원천징수|세율|탈세|면세")
def text(el, tag):
    v = el.findtext(tag)
    if v is None:
        for c in el:
            if c.tag.split('}')[-1] == tag: return c.text or ""
        return ""
    return v
def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (ctasyb-design.github.io press feed)"})
    return urllib.request.urlopen(req, timeout=40).read()
def parse(raw, need_filter):
    root = ET.fromstring(raw)
    ch = root.find("channel")
    if ch is None: return []
    out = []
    for it in ch.findall("item"):
        title = html.unescape(text(it, "title")).strip()
        desc = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", html.unescape(text(it, "description")))).strip()
        blob = " ".join([title, desc, text(it, "author"), text(it, "creator"), text(it, "category")])
        if need_filter and MINISTRY not in blob and "재경부" not in blob: continue
        d = ""
        for tag in ("pubDate", "date"):
            v = text(it, tag)
            if v:
                try: d = email.utils.parsedate_to_datetime(v).astimezone(KST).date().isoformat()
                except Exception:
                    m = re.search(r"\d{4}-\d{2}-\d{2}", v); d = m.group(0) if m else ""
                break
        link = text(it, "link").strip()
        if not title or not link: continue
        out.append({"title": title, "link": link, "date": d, "summary": desc[:160], "tax": bool(TAX.search(title + " " + desc))})
    return out
items, used = [], None
for name, url, flt in CANDIDATES:
    try:
        got = parse(fetch(url), flt)
        print(f"[{name}] {url} → {len(got)}건")
        if got: items, used = got, name; break
    except Exception as e:
        print(f"[{name}] {url} 실패: {e}")
if not items:
    print("모든 후보 실패, 기존 파일 유지"); sys.exit(0)
try: old = json.load(open(OUT, encoding="utf-8")).get("items", [])
except Exception: old = []
seen, merged = set(), []
for i in items + old:
    if i["link"] in seen: continue
    seen.add(i["link"]); merged.append(i)
merged.sort(key=lambda x: x.get("date", ""), reverse=True)
merged = merged[:40]
if merged == old: print("변경 없음"); sys.exit(0)
json.dump({"ministry": MINISTRY, "source": used, "list": "https://www.mofe.go.kr", "updated": datetime.datetime.now(KST).date().isoformat(), "items": merged},
          open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
print("저장", len(merged), "건 (세제 관련", sum(i["tax"] for i in merged), "건)")
