#!/bin/sh
# 생성 결과(OUT)를 저장소(REPO)에 반영합니다. 명함(card/), 네이버 확인 파일, README 등은 건드리지 않습니다.
# 사용: sh _build/sync.sh <OUT_DIR> <REPO_DIR>
set -e
OUT="$1"; REPO="$2"
for f in index.html assets-style.css logo.png sitemap.xml robots.txt; do cp "$OUT/$f" "$REPO/$f"; done
for d in blog guide data; do rm -rf "$REPO/$d"; cp -r "$OUT/$d" "$REPO/$d"; done
# 블로그 대표 이미지(cards/)는 덮어쓰기만 합니다(지우지 않음).
if [ -d "$OUT/cards" ]; then mkdir -p "$REPO/cards"; cp "$OUT"/cards/*.png "$REPO/cards/"; fi
