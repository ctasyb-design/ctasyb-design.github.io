"""세무 칼럼 원문 대조 점검 (저작권 보호용)
다른 세무사 칼럼과 문장이 겹치지 않는지 확인합니다. 참고 원문은 저장소에 올리지 않고 /tmp 에서만 씁니다.
사용:
  git clone --depth 1 https://github.com/recaro79/recaro79.github.io /tmp/ref
  python3 -I _build/check_originality.py <columns.json> /tmp/ref [N=25] [번호,번호...]
결과: 공백·문장부호를 뺀 연속 N글자 이상이 겹치는 칼럼을 표시합니다. 법령 조문·숫자 요건 외의 겹침은 고쳐 씁니다.
종료 코드 1 = 겹침 비율 3% 이상 칼럼 있음."""
import sys, json, re, html, glob, os
cols = json.load(open(sys.argv[1])); cols = cols["items"] if isinstance(cols, dict) else cols
refdir = sys.argv[2]; N = int(sys.argv[3]) if len(sys.argv) > 3 else 25
only = set(int(x) for x in sys.argv[4].split(",")) if len(sys.argv) > 4 and sys.argv[4] else None
norm = lambda s: re.sub(r"[\s·,.\-—()「」'\"“”‘’:;!?%~/]", "", html.unescape(re.sub("<[^>]+>", " ", s)))
idx = set()
for p in glob.glob(os.path.join(refdir, "column", "*.html")):
    t = open(p, encoding="utf-8", errors="replace").read()
    t = norm(re.sub(r"<(script|style)[^>]*>.*?</\1>", "", t, flags=re.S))
    idx.update(t[i:i + N] for i in range(len(t) - N + 1))
bad = 0
for c in sorted(cols, key=lambda c: c["no"]):
    if only and c["no"] not in only: continue
    t = norm(c["title"] + c["summary"] + c["body"]); runs = []; i = 0
    while i <= len(t) - N:
        if t[i:i + N] in idx:
            j = i + N
            while j < len(t) and t[j - N + 1:j + 1] in idx: j += 1
            runs.append(t[i:j]); i = j
        else: i += 1
    share = sum(map(len, runs)) / max(1, len(t))
    if runs:
        print(f"{c['no']:>3} {share*100:4.1f}% {c['title'][:40]}")
        for r in runs[:6]: print("     ·", r[:80])
    if share >= 0.03: bad += 1
print(f"점검 {len(cols) if not only else len(only)}편, 기준 {N}글자, 3% 이상 겹침 {bad}편")
sys.exit(1 if bad else 0)
