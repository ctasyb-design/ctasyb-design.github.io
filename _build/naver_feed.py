"""네이버 블로그 RSS → feeds/naverblog.json (홈페이지 '네이버 블로그 최신 글' 영역에 사용)
사용: python3 _build/naver_feed.py <RSS_URL> <OUT_JSON>
가져오기에 실패하면 기존 파일을 그대로 둡니다."""
import json, re, sys, html, urllib.request, email.utils, datetime
import xml.etree.ElementTree as ET
RSS, OUT = sys.argv[1], sys.argv[2]
try:
    req = urllib.request.Request(RSS, headers={"User-Agent": "Mozilla/5.0 (ctasyb-design.github.io feed)"})
    raw = urllib.request.urlopen(req, timeout=30).read()
    root = ET.fromstring(raw)
except Exception as e:
    print("RSS 가져오기 실패, 기존 파일 유지:", e); sys.exit(0)
ch = root.find("channel")
items = []
for it in ch.findall("item")[:10]:
    link = (it.findtext("link") or "").split("?")[0]
    desc = re.sub(r"<[^>]+>", " ", html.unescape(it.findtext("description") or ""))
    desc = re.sub(r"\s+", " ", desc).strip()
    try:
        d = email.utils.parsedate_to_datetime(it.findtext("pubDate")).astimezone(datetime.timezone(datetime.timedelta(hours=9))).date().isoformat()
    except Exception:
        d = ""
    items.append({"title": (it.findtext("title") or "").strip(), "link": link, "date": d,
                  "category": (it.findtext("category") or "").strip(), "summary": desc[:140]})
data = {"blog": (ch.findtext("link") or "https://blog.naver.com/ctasyb").split("?")[0], "items": items}
try:
    old = json.load(open(OUT, encoding="utf-8"))
    if old.get("items") == items: print("변경 없음"); sys.exit(0)
except Exception:
    pass
data["updated"] = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9))).date().isoformat()
json.dump(data, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
print("글", len(items), "편 저장")
