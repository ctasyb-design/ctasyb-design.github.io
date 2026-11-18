// 세법 개정 소식 PowerPoint 자동 생성기
// 사용법: node _build/tax_deck.js <data 폴더> <출력 pptx 경로>
// data/laws.json, data/calendar.json, data/office.json 을 읽어 슬라이드를 만듭니다.
// GitHub Actions(.github/workflows/tax-deck.yml)가 자료가 바뀔 때마다 실행합니다.
const fs = require("fs");
const path = require("path");
const pptxgen = require("pptxgenjs");

const DATA = process.argv[2] || "data";
const OUT = process.argv[3] || "files/tax-law-update.pptx";
const read = (f) => JSON.parse(fs.readFileSync(path.join(DATA, f), "utf8"));
const laws = read("laws.json");
const cal = read("calendar.json");
const office = read("office.json");

const FONT = "맑은 고딕";
const K = { indigo: "262F6B", foil: "B8924A", foilLt: "E6CD93", blue: "2A6EA6", soft: "8A93B8", text: "1F2433", sub: "5A6070", card: "F2F3F8", line: "D9DCE8", white: "FFFFFF" };
const STATUS_COLOR = { "시행": K.indigo, "시행예정": K.blue, "국회심사": K.foil, "정부안": K.blue };
const BASE = laws.updated; // 기준일 YYYY-MM-DD
const d2k = (d) => { const [y, m, dd] = d.split("-").map(Number); return `${y}.${m}.${dd}.`; };
const d2kLong = (d) => { const [y, m, dd] = d.split("-").map(Number); return `${y}년 ${m}월 ${dd}일`; };
const strip = (s) => String(s || "").replace(/<br\s*\/?>/gi, " · ").replace(/<[^>]+>/g, "");

const pres = new pptxgen();
pres.layout = "LAYOUT_WIDE"; // 13.33 x 7.5 in
pres.theme = { headFontFace: FONT, bodyFontFace: FONT };
pres.author = strip(office.ceo) + " (" + strip(office.name) + ")";
pres.company = strip(office.name).replace(/&/g, "&amp;");
pres.title = `세법 개정 소식 (${d2k(BASE)} 기준)`;

const FOOT = `${strip(office.name)}  ·  ${d2k(BASE)} 기준`;
pres.defineSlideMaster({ title: "DARK", background: { color: K.indigo }, objects: [] });
pres.defineSlideMaster({ title: "BODY", background: { color: K.white }, objects: [
  { text: { text: FOOT, options: { x: 0.6, y: 7.0, w: 7, h: 0.3, fontSize: 10, color: K.soft, fontFace: FONT, margin: 0 } } },
], slideNumber: { x: 12.2, y: 7.0, w: 0.5, h: 0.3, fontSize: 10, color: K.soft, fontFace: FONT, align: "right" } });

const T = (s, text, o) => s.addText(text, Object.assign({ fontFace: FONT, margin: 0, isTextBox: true, valign: "top", color: K.text }, o));
const title = (s, text) => T(s, text, { x: 0.6, y: 0.35, w: 10.6, h: 0.8, fontSize: 28, bold: true, color: K.indigo, valign: "middle", fit: "shrink", objectName: "제목" });
const card = (s, x, y, w, h, fill, name) => s.addShape(pres.ShapeType.roundRect, { x, y, w, h, rectRadius: 0.12, fill: { color: fill || K.card }, line: { color: fill || K.card, width: 0.5 }, objectName: name || "카드" });
const chip = (s, x, y, st, w) => T(s, st, { x, y, w: w || 1.15, h: 0.34, shape: pres.ShapeType.roundRect, rectRadius: 0.17, fill: { color: STATUS_COLOR[st] || K.soft }, color: K.white, fontSize: 12, bold: true, align: "center", valign: "middle", objectName: "상태 " + st });
const shortTitle = (t) => { let s = t.split(" — ")[0].replace(/\s*\([^)]*\)\s*$/, "").trim(); return s.length > 34 ? s.slice(0, 33) + "…" : s; };

// 정렬: 최근 소식 먼저
const items = [...laws.items].sort((a, b) => (a.date < b.date ? 1 : -1));
const pending = items.filter((x) => x.status !== "시행");
const inForce = items.filter((x) => x.status === "시행");

// 1. 표지
let s = pres.addSlide({ masterName: "DARK" });
T(s, "세법 개정 소식", { x: 0.8, y: 1.9, w: 11.7, h: 1.2, fontSize: 48, bold: true, color: K.white, valign: "bottom", objectName: "표지 제목" });
T(s, `국회 심사 중인 개정안과 이미 시행된 변화, 다가오는 신고 일정\n${d2kLong(BASE)} 기준`, { x: 0.8, y: 3.3, w: 11.7, h: 1.0, fontSize: 20, color: K.foilLt, objectName: "표지 부제" });
T(s, `${strip(office.name)}  |  ${strip(office.ceo)}`, { x: 0.8, y: 6.3, w: 11, h: 0.4, fontSize: 14, color: K.white, objectName: "표지 사무소" });

// 2. 한눈에 보기
s = pres.addSlide({ masterName: "BODY" });
title(s, "한눈에 보는 세법 개정");
const groups = [
  ["국회 심사·정부안", pending, K.foil],
  ["이미 시행 중", inForce, K.indigo],
];
groups.forEach(([label, list, color], i) => {
  const x = 0.6 + i * 6.15, y = 1.4, w = 5.95, h = 5.0;
  card(s, x, y, w, h, K.card, "요약 카드 " + (i + 1));
  T(s, [{ text: String(list.length), options: { fontSize: 54, bold: true, color } }, { text: "건", options: { fontSize: 28, bold: true, color } }], { x: x + 0.35, y: y + 0.25, w: 2.4, h: 1.0, valign: "bottom", objectName: "요약 건수 " + (i + 1) });
  T(s, label, { x: x + 0.35, y: y + 1.35, w: w - 0.7, h: 0.45, fontSize: 20, bold: true, objectName: "요약 제목 " + (i + 1) });
  const top = list.slice(0, 5).map((it, j, a) => ({ text: shortTitle(it.title), options: { bullet: true, breakLine: j < a.length - 1 } }));
  if (top.length) T(s, top, { x: x + 0.35, y: y + 1.95, w: w - 0.6, h: 2.85, fontSize: 15, paraSpaceAfter: 6, objectName: "요약 목록 " + (i + 1) });
});
T(s, "‘정부안’·‘국회심사’ 항목은 국회 의결 과정에서 바뀔 수 있습니다.", { x: 0.6, y: 6.55, w: 12, h: 0.3, fontSize: 11, color: K.soft, objectName: "요약 안내" });

// 3. 세법개정안 진행 단계
if (laws.pipeline && laws.pipeline.steps && laws.pipeline.steps.length) {
  s = pres.addSlide({ masterName: "BODY" });
  title(s, laws.pipeline.title || "세법개정안 진행 상황");
  const st = laws.pipeline.steps, n = st.length;
  let now = -1; st.forEach((p, i) => { if (p.date && p.date <= BASE) now = i; });
  const x0 = 1.3, x1 = 12.0, gap = n > 1 ? (x1 - x0) / (n - 1) : 0;
  s.addShape(pres.ShapeType.line, { x: x0, y: 2.65, w: x1 - x0, h: 0, line: { color: K.line, width: 3 }, objectName: "단계 연결선" });
  st.forEach((p, i) => {
    const cx = x0 + i * gap, done = i < now, cur = i === now;
    const fill = done ? K.indigo : cur ? K.foil : K.white;
    s.addShape(pres.ShapeType.ellipse, { x: cx - 0.4, y: 2.25, w: 0.8, h: 0.8, fill: { color: fill }, line: { color: done ? K.indigo : K.foil, width: 2 }, objectName: "단계 " + (i + 1) });
    T(s, String(i + 1), { x: cx - 0.4, y: 2.25, w: 0.8, h: 0.8, fontSize: 20, bold: true, align: "center", valign: "middle", color: done || cur ? K.white : K.foil, objectName: "단계 번호 " + (i + 1) });
    const when = p.date ? d2k(p.date) : (p.note || "예정");
    T(s, [{ text: p.label, options: { bold: true, fontSize: 16, breakLine: true } }, { text: when + (cur ? "  진행 중" : ""), options: { fontSize: 14, color: cur ? K.foil : K.sub, bold: cur, breakLine: !!(p.date && p.note) } }, ...(p.date && p.note ? [{ text: p.note, options: { fontSize: 12, color: K.sub } }] : [])],
      { x: cx - 1.25, y: 3.25, w: 2.5, h: 1.3, align: "center", objectName: "단계 이름 " + (i + 1) });
  });
  const guide = Object.entries(laws.statusGuide || {});
  card(s, 0.6, 4.85, 12.1, 1.6, K.card, "상태 설명 카드");
  guide.slice(0, 4).forEach(([k, v], i) => {
    const x = 0.9 + (i % 2) * 6.0, y = 5.0 + Math.floor(i / 2) * 0.65;
    chip(s, x, y, k, 1.3);
    T(s, v, { x: x + 1.45, y: y - 0.02, w: 4.3, h: 0.5, fontSize: 13, valign: "middle", objectName: "상태 설명 " + k });
  });
}

// 4. 항목 슬라이드
function sectionSlide(label, n, color, desc) {
  const d = pres.addSlide({ masterName: "DARK" });
  T(d, label, { x: 0.8, y: 2.4, w: 11.7, h: 1.0, fontSize: 40, bold: true, color: K.white, valign: "bottom", objectName: "구분 제목" });
  T(d, `${n}건 · ${desc}`, { x: 0.8, y: 3.55, w: 11.7, h: 0.6, fontSize: 20, color: color, objectName: "구분 설명" });
}
function summaryRuns(sum) {
  const parts = String(sum).split(/(?=[①②③④⑤⑥⑦⑧⑨⑩])/).map((x) => x.trim()).filter(Boolean);
  if (parts.length <= 1) return { runs: [{ text: sum }], len: sum.length };
  const runs = parts.map((p, i) => {
    const isNum = /^[①-⑩]/.test(p);
    return { text: isNum ? p.replace(/^[①-⑩]\s*/, "") : p, options: Object.assign({ breakLine: i < parts.length - 1 }, isNum ? { bullet: true } : {}) };
  });
  return { runs, len: sum.length };
}
function itemSlide(it) {
  const sl = pres.addSlide({ masterName: "BODY" });
  chip(sl, 0.6, 0.45, it.status);
  T(sl, it.category || "", { x: 1.9, y: 0.45, w: 4, h: 0.34, fontSize: 13, bold: true, color: K.sub, valign: "middle", objectName: "분류" });
  T(sl, it.title, { x: 0.6, y: 0.95, w: 12.1, h: 1.1, fontSize: 26, bold: true, color: K.indigo, fit: "shrink", objectName: "항목 제목" });
  card(sl, 0.6, 2.3, 7.75, 4.2, K.card, "요약 카드");
  const { runs, len } = summaryRuns(it.summary);
  const fs_ = len > 330 ? 14 : len > 250 ? 15 : len > 170 ? 16 : 18;
  T(sl, runs, { x: 0.9, y: 2.55, w: 7.15, h: 3.75, fontSize: fs_, paraSpaceAfter: 6, lineSpacingMultiple: 1.1, fit: "shrink", objectName: "항목 요약" });
  sl.addShape(pres.ShapeType.roundRect, { x: 8.6, y: 2.3, w: 4.1, h: 4.2, rectRadius: 0.12, fill: { color: K.white }, line: { color: K.line, width: 1 }, objectName: "정보 테두리" });
  const rows = [["시행 시기", it.effective || "-"], ["대상", (it.impact || []).join(" · ") || "-"], ["발표·확인일", it.date ? d2k(it.date) : "-"]];
  rows.forEach((r, i) => {
    T(sl, r[0], { x: 8.9, y: 2.55 + i * 1.05, w: 3.5, h: 0.3, fontSize: 12, bold: true, color: K.foil, objectName: "정보 항목 " + (i + 1) });
    T(sl, r[1], { x: 8.9, y: 2.88 + i * 1.05, w: 3.5, h: 0.65, fontSize: 14, fit: "shrink", objectName: "정보 내용 " + (i + 1) });
  });
  if (it.source && it.source.name) {
    T(sl, "출처", { x: 8.9, y: 5.7, w: 3.5, h: 0.25, fontSize: 11, bold: true, color: K.foil, objectName: "출처 제목" });
    const run = it.source.url ? [{ text: it.source.name, options: { hyperlink: { url: it.source.url }, color: K.blue } }] : it.source.name;
    T(sl, run, { x: 8.9, y: 5.97, w: 3.5, h: 0.45, fontSize: 11, fit: "shrink", objectName: "출처" });
  }
}
if (pending.length) { sectionSlide("국회 심사·정부안", pending.length, K.foilLt, "국회 의결 전으로, 내용이 바뀔 수 있습니다"); pending.forEach(itemSlide); }
if (inForce.length) { sectionSlide("이미 시행 중", inForce.length, K.foilLt, "현재 적용되는 개정 사항입니다"); inForce.forEach(itemSlide); }

// 5. 일정
const upcoming = (cal.items || []).filter((e) => e.date >= BASE).sort((a, b) => (a.date < b.date ? -1 : 1)).slice(0, 6);
if (upcoming.length) {
  s = pres.addSlide({ masterName: "BODY" });
  title(s, "다가오는 신고·납부 일정");
  const by = BASE.slice(0, 4);
  upcoming.forEach((e, i) => {
    const y = 1.35 + i * 0.88, [yy, m, d] = e.date.split("-").map(Number), nextYear = e.date.slice(0, 4) !== by;
    s.addShape(pres.ShapeType.roundRect, { x: 0.6, y, w: 1.8, h: 0.72, rectRadius: 0.1, fill: { color: nextYear ? K.foil : K.indigo }, line: { color: nextYear ? K.foil : K.indigo }, objectName: "일정 날짜 배경 " + (i + 1) });
    T(s, `${nextYear ? yy + "." : ""}${m}.${d}.`, { x: 0.6, y, w: 1.8, h: 0.72, fontSize: nextYear ? 16 : 20, bold: true, color: K.white, align: "center", valign: "middle", objectName: "일정 날짜 " + (i + 1) });
    T(s, e.title, { x: 2.65, y, w: 4.3, h: 0.72, fontSize: 16, bold: true, color: K.indigo, valign: "middle", fit: "shrink", objectName: "일정 이름 " + (i + 1) });
    T(s, e.desc || e.who || "", { x: 7.1, y, w: 5.6, h: 0.72, fontSize: 12, valign: "middle", fit: "shrink", objectName: "일정 설명 " + (i + 1) });
  });
  T(s, "기한이 토·일·공휴일이면 다음 영업일로 늦춰집니다.", { x: 0.6, y: 6.6, w: 12, h: 0.3, fontSize: 11, color: K.soft, objectName: "일정 안내" });
}

// 6. 상담 안내
s = pres.addSlide({ masterName: "DARK" });
T(s, "내 상황에 어떻게 적용되는지 확인해 드립니다", { x: 0.8, y: 0.6, w: 11.7, h: 0.9, fontSize: 34, bold: true, color: K.white, valign: "middle", objectName: "마무리 제목" });
const prof = office.profile && office.profile.rows ? office.profile.rows.map((r) => strip(r[1])).join(" · ") : "";
T(s, [{ text: strip(office.ceo), options: { fontSize: 22, bold: true, color: K.white, breakLine: !!prof } }, ...(prof ? [{ text: prof, options: { fontSize: 14, color: K.foilLt } }] : [])],
  { x: 0.8, y: 1.8, w: 11.7, h: 1.3, objectName: "대표 약력" });
[["전화", office.phone], ["휴대전화", office.mobile], ["이메일", office.email], ["홈페이지", "ctasyb-design.github.io"]].filter((c) => c[1]).forEach((c, i) => {
  const x = 0.8 + (i % 2) * 5.9, y = 3.45 + Math.floor(i / 2) * 1.0;
  T(s, [{ text: c[0] + "  ", options: { fontSize: 15, color: K.foilLt } }, { text: strip(c[1]), options: { fontSize: 22, bold: true, color: K.white } }], { x, y, w: 5.6, h: 0.7, valign: "middle", objectName: "연락처 " + c[0] });
});
T(s, `${strip(office.address)} · ${strip(office.hours)}`, { x: 0.8, y: 5.5, w: 11.7, h: 0.4, fontSize: 14, color: K.white, objectName: "주소와 상담시간" });
T(s, `이 자료는 ${d2kLong(BASE)} 기준의 일반 안내이며 개별 사안에 대한 세무 자문을 대신하지 않습니다. ‘정부안’·‘국회심사’ 항목은 국회 의결 과정에서 바뀔 수 있습니다.`, { x: 0.8, y: 6.3, w: 11.7, h: 0.6, fontSize: 11, color: K.soft, objectName: "면책 안내" });

fs.mkdirSync(path.dirname(OUT), { recursive: true });
pres.writeFile({ fileName: OUT }).then(() => console.log("written " + OUT + ""));
