"""
Generate the model parameter CSVs in data/params/ from an explicit, sourced specification.

Every number below carries a source_id (see data/sources.csv) and a confidence grade:
  A   = official page (snippet) / official press release
  B   = specialist media (Aviation Wire, Traicy, トラベルボイス, トラベルWatch) or multiple agreeing sources
  C   = blog / aggregator, not yet cross-checked
  EST = analyst estimate; the derivation is written in `notes`

Prices are JPY per adult. basis = ow (one-way) or rt (round trip); the model doubles ow on load.
Run:  python3 src/build_params.py
"""
from __future__ import annotations

import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
P = ROOT / "data" / "params"
P.mkdir(parents=True, exist_ok=True)


def write(name, header, rows):
    with open(P / name, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(header)
        for r in rows:
            w.writerow(r)
    print(f"{name}: {len(rows)} rows")


# ----------------------------------------------------------------------------
# routes
# ----------------------------------------------------------------------------
routes = [
    # route_id, market, origin, dest, label_ja, group, notes
    ("HND-ITM", "domestic", "HND", "ITM", "羽田-伊丹", "国内幹線", "新幹線（東京-新大阪）が現金代替の主役"),
    ("HND-FUK", "domestic", "HND", "FUK", "羽田-福岡", "国内幹線", ""),
    ("HND-CTS", "domestic", "HND", "CTS", "羽田-新千歳", "国内幹線", ""),
    ("HND-OKA", "domestic", "HND", "OKA", "羽田-那覇", "国内幹線", ""),
    ("TYO-SEL", "international", "TYO", "SEL", "東京-ソウル", "韓国", "ANA Zone2 / JAL 韓国"),
    ("TYO-TPE", "international", "TYO", "TPE", "東京-台北", "東アジア", "ANA Zone3 / JAL 台湾"),
    ("TYO-BKK", "international", "TYO", "BKK", "東京-バンコク", "東南アジア", "ANA Zone4 / JAL タイ"),
    ("TYO-SIN", "international", "TYO", "SIN", "東京-シンガポール", "東南アジア", "ANA Zone4 / JAL シンガポール"),
    ("TYO-HNL", "international", "TYO", "HNL", "東京-ホノルル", "ハワイ", "ANA Zone5 / JAL ハワイ"),
    ("TYO-NYC", "international", "TYO", "NYC", "東京-ニューヨーク", "北米", "ANA Zone6 / JAL 北米"),
    ("TYO-LON", "international", "TYO", "LON", "東京-ロンドン", "欧州", "ANA Zone7 / JAL 欧州"),
    ("TYO-SYD", "international", "TYO", "SYD", "東京-シドニー", "オセアニア", "ANA Zone10 / JAL オセアニア"),
]
write("routes.csv", ["route_id", "market", "origin_code", "dest_code", "label_ja", "group", "notes"], routes)

# ----------------------------------------------------------------------------
# demand bands
# ----------------------------------------------------------------------------
bands = [
    ("D1", "閑散平日昼", "火曜・水曜の10〜16時発・閑散期（国際線は閑散期の平日出発）", "L", "L", "base", "L", 0.15, 0.25, "旅客シェアは分析者の仮定（感応度分析で検証）"),
    ("D2", "通常", "通常期の平日・朝夕ピーク以外（国際線は通常期の平日出発）", "R", "R", "base", "R", 0.35, 0.40, "同上"),
    ("D3", "高需要時間帯", "金曜18〜20時発・月曜7〜8時発・日曜夕方発（国際線は通常期の週末出発）", "R", "R", "base", "R", 0.25, 0.20, "ANAは同じRシーズンのマイルだが特典枠が極端に少ない"),
    ("D4", "繁忙期", "3連休・年末年始・GW・お盆（ANA Hシーズン）", "H", "H", "base", "H", 0.25, 0.15, "ANA国内線の2026年Hシーズンは91日（年の25%）。JALはファーストのみシーズン制"),
]
write("demand_bands.csv", ["band_id", "label_ja", "description_ja", "ana_dom_season", "ana_intl_season", "jal_dom_season", "jal_intl_season", "traveler_weight", "calendar_share", "notes"], bands)

# ----------------------------------------------------------------------------
# award miles
# ----------------------------------------------------------------------------
am = []
def ana_dom(route, L, R, H, conf, note=""):
    for s, m in (("L", L), ("R", R), ("H", H)):
        am.append(("ANA", route, "Y", "ow", s, m, "ANA_DOM_CHART", conf, note))

ana_dom("HND-ITM", 6000, 6500, 9000, "A/C", "0〜300区間マイル帯（帯判定は区間マイル推定）")
ana_dom("HND-FUK", 7000, 8500, 10500, "A/C", "301〜800帯")
ana_dom("HND-CTS", 7000, 8500, 10500, "A/C", "301〜800帯")
ana_dom("HND-OKA", 8000, 9500, 12000, "A/B", "801〜1000帯（早見表で東京-沖縄 8000/9500/12000 を確認）")

am += [
    ("JAL", "HND-ITM", "Y", "ow", "base", 6500, "JAL_DOM_MILES", "C", "ゾーンC推定（公式のゾーン所属は未確認）"),
    ("JAL", "HND-FUK", "Y", "ow", "base", 8500, "JAL_DOM_MILES", "A", "ゾーンE（公式スニペットで東京-福岡=E）"),
    ("JAL", "HND-CTS", "Y", "ow", "base", 8500, "JAL_DOM_MILES", "A", "ゾーンE"),
    ("JAL", "HND-OKA", "Y", "ow", "base", 9500, "JAL_DOM_MILES", "A", "ゾーンF（東京-那覇 9500 を公式スニペットで確認）"),
]

# --- ANA international (RT, ANA-operated, chart effective 2025-06-24). Many cells provisional (EST) pending gap-fill. ---
def ana_intl(route, cabin, L, R, H, conf, note=""):
    for s, m in (("L", L), ("R", R), ("H", H)):
        am.append(("ANA", route, cabin, "rt", s, m, "ANA_INTL_CHART", conf, note))

# Source: two independent unofficial transcriptions of the official chart (ana-mile-calc IZONES "2026/8/29 照合済み",
# award-radar ANAM one-way = exactly half) agree; cells that also match official snippets are marked A/B.
NOTE_B = "非公式転記2件（ana-mile-calc / award-radar）が一致。公式ページ本文は未取得"
ana_intl("TYO-SEL", "Y", 12000, 15000, 24000, "B", "Zone2 韓国。" + NOTE_B)
ana_intl("TYO-SEL", "C", 36000, 41000, 50000, "B", "Zone2 韓国。" + NOTE_B)
ana_intl("TYO-TPE", "Y", 17000, 20000, 30000, "B", "Zone3 アジア1。" + NOTE_B)
ana_intl("TYO-TPE", "C", 48000, 53000, 65000, "A/B", "Zone3 アジア1。L=48,000は東洋経済（改定後）とも一致")
ana_intl("TYO-BKK", "Y", 30000, 35000, 50000, "B", "Zone4 アジア2。" + NOTE_B)
ana_intl("TYO-BKK", "C", 80000, 85000, 95000, "B", "Zone4 アジア2。" + NOTE_B)
ana_intl("TYO-SIN", "Y", 30000, 35000, 50000, "B", "Zone4 アジア2。" + NOTE_B)
ana_intl("TYO-SIN", "C", 80000, 85000, 95000, "B", "Zone4 アジア2。" + NOTE_B)
ana_intl("TYO-HNL", "Y", 35000, 40000, 65000, "B", "Zone5 ハワイ。2026年早見表とも一致")
ana_intl("TYO-HNL", "PY", 53000, 58000, 88000, "B", "Zone5 ハワイ。" + NOTE_B)
ana_intl("TYO-HNL", "C", 80000, 85000, 135000, "A/B", "Zone5 ハワイ。H=135,000はAviation Wire（公式改定告知）とも一致")
ana_intl("TYO-NYC", "Y", 40000, 50000, 72000, "A/B", "Zone6 北米。L/Rは公式旧ページ（据置）とも一致")
ana_intl("TYO-NYC", "PY", 62000, 72000, 101000, "B", "Zone6 北米。" + NOTE_B)
ana_intl("TYO-NYC", "C", 100000, 105000, 165000, "A/B", "Zone6 北米。R=105,000は公式告知断片、H=165,000はブログ複数と一致")
ana_intl("TYO-NYC", "F", 150000, 170000, 300000, "B", "Zone6 北米。" + NOTE_B)
ana_intl("TYO-LON", "Y", 45000, 55000, 78000, "B", "Zone7 欧州。" + NOTE_B)
ana_intl("TYO-LON", "PY", 67000, 77000, 107000, "B", "Zone7 欧州。" + NOTE_B)
ana_intl("TYO-LON", "C", 110000, 115000, 180000, "B", "Zone7 欧州。" + NOTE_B)
ana_intl("TYO-LON", "F", 165000, 190000, 330000, "B/C", "Zone7 欧州。L=165,000は4travel実例（片道82,500）とも一致")
ana_intl("TYO-SYD", "Y", 37000, 45000, 65000, "B", "Zone10 オセアニア。" + NOTE_B)
ana_intl("TYO-SYD", "C", 80000, 90000, 135000, "B", "Zone10 オセアニア。" + NOTE_B)

# --- JAL international (one-way base, chart effective 2025-06-10; PLUS caps separate) ---
jal_intl = [
    ("TYO-SEL", "Y", 7500, "A"), ("TYO-SEL", "C", 18000, "A"),
    ("TYO-TPE", "Y", 11000, "A"), ("TYO-TPE", "C", 24000, "B"),   # Y: 公式スニペット11,000（非公式転記は9,000で不一致→公式を採用）
    ("TYO-BKK", "Y", 13500, "B"), ("TYO-BKK", "C", 40000, "B"),   # award-radar JALM（公式表2026-04-16版の転記）
    ("TYO-SIN", "Y", 13000, "B"), ("TYO-SIN", "C", 40000, "B"),
    ("TYO-HNL", "Y", 20000, "A"), ("TYO-HNL", "PY", 30000, "A"), ("TYO-HNL", "C", 43000, "A"),
    ("TYO-NYC", "Y", 27000, "A"), ("TYO-NYC", "PY", 40000, "A"), ("TYO-NYC", "C", 55000, "A"),
    ("TYO-LON", "Y", 27000, "A"), ("TYO-LON", "PY", 40000, "A"), ("TYO-LON", "C", 57000, "A"),
    ("TYO-SYD", "Y", 23000, "A"), ("TYO-SYD", "C", 45000, "A"),
]
for route, cabin, m, conf in jal_intl:
    am.append(("JAL", route, cabin, "ow", "base", m, "JAL_INTL_MILES", conf, "片道基本マイル（往復=2倍）"))
# JAL F: 3-season (not PLUS)
for route in ("TYO-NYC", "TYO-LON"):
    for s, m in (("L", 110000), ("R", 125000), ("H", 140000)):
        am.append(("JAL", route, "F", "ow", s, m, "JAL_INTL_MILES", "A", "ファーストのみ3シーズン制、PLUS対象外"))

write("award_miles.csv", ["carrier", "route_id", "cabin", "basis", "season", "miles", "source_id", "confidence", "notes"], am)

# JAL First uses L/R/H rows; the model maps a band to JAL seasons via demand_bands.jal_intl_season when no 'base' row exists.

# ----------------------------------------------------------------------------
# award cash costs (RT unless basis=ow)
# ----------------------------------------------------------------------------
ac = []
pfc = {"HND": 580, "ITM": 340, "FUK": 110, "CTS": 530, "OKA": 240}  # CTS 370→530 (2026-10-25以降発券分)
for route, (a, b, conf, note) in {
    "HND-ITM": ("HND", "ITM", "A", "羽田580＋伊丹340"),
    "HND-FUK": ("HND", "FUK", "A/B", "羽田580＋福岡110"),
    "HND-CTS": ("HND", "CTS", "A", "羽田580＋新千歳530（2026-10-25以降発券分）"),
    "HND-OKA": ("HND", "OKA", "A", "羽田580＋那覇240"),
}.items():
    for carrier in ("ANA", "JAL"):
        ac.append((carrier, route, "*", "PFC", "ow", pfc[a] + pfc[b], "2026-09-01以降発券", "ANA_PFC" if carrier == "ANA" else "JAL_PFC_FAQ", conf, note))

# international: fuel surcharge (Nov-Dec 2026 issuance, one-way, same for ANA/JAL), Japan-side fees, destination taxes
fuel = {  # one-way JPY, 2026-11/12 issuance
    "TYO-SEL": (7100, "B"), "TYO-TPE": (15100, "B"), "TYO-BKK": (32000, "B"), "TYO-SIN": (32000, "B"),
    "TYO-HNL": (38500, "B"), "TYO-NYC": (62000, "B"), "TYO-LON": (62000, "B"), "TYO-SYD": (62000, "B"),
}
jp_side = 6160  # NRT T1/T2: PSFC 2,460 + PSSC 700 + 国際観光旅客税 3,000（2026-07-01以降出国分、A）; HND: 2,950 + 3,000 = 5,950
dest_tax = {  # RT-equivalent JPY paid for destination side (arrival/departure taxes, airport charges).
    "TYO-SEL": (2700, "EST", "仁川 国際線旅客サービス料17,000ウォン＋出国納付金7,000ウォン＋1,000ウォン≈25,000ウォン（検証者推定）"),
    "TYO-TPE": (2400, "EST", "台湾 空港サービス料 NT$500 の目安"),
    "TYO-BKK": (5600, "A", "AOT 国際線旅客サービス料 1,120バーツ（2026-06-20以降発券分）"),
    "TYO-SIN": (8000, "EST", "チャンギ空港税の目安"),
    "TYO-HNL": (11300, "A/EST", "米国連邦税・料金：到着/出発税$23.40×2＋APHIS$3.84＋税関$7.39＋入国審査$7.00（＝$65）＋PFC$4.5＋9/11料$5.6 ≈ $75 ≈ 11,300円"),
    "TYO-NYC": (11300, "A/EST", "同上（米国連邦税・料金の積算）"),
    "TYO-LON": (29000, "A/EST", "英国APD 2026-27 Band C reduced £106（エコノミー）≈21,200円＋ヒースロー空港料金の目安約8,000円"),
    "TYO-SYD": (9000, "C", "豪州出国税PMC＋空港使用料の目安 9,000〜11,000円"),
}
jal_fuel_override = {"TYO-TPE": 16000}  # JAL 東アジア（中国・台湾・香港）片道16,000円（ANAは15,100円）
for route, (f, conf) in fuel.items():
    for carrier in ("ANA", "JAL"):
        src = "ANA_FUEL_2611" if carrier == "ANA" else "JAL_FUEL_2611"
        f_c = jal_fuel_override.get(route, f) if carrier == "JAL" else f
        note = "特典航空券にも同額（公式明記）" + ("。JALの東アジア区分は16,000円（ANA 15,100円）" if f_c != f else "")
        ac.append((carrier, route, "*", "fuel_surcharge", "ow", f_c, "2026-11-01〜12-31発券", src, conf, note))
        ac.append((carrier, route, "*", "jp_airport_fees_tax", "rt", jp_side, "2026-07-01以降", "NRT_PSFC", "A", "成田PSFC2,460＋PSSC700＋国際観光旅客税3,000（2026-07-01以降出国分に引き上げ）。羽田は2,950＋3,000=5,950。往復で出発時1回"))
        d, dconf, dnote = dest_tax[route]
        ac.append((carrier, route, "*", "dest_taxes", "rt", d, "2026", "TAX_EST", dconf, dnote))
# London business/first: higher APD band
for carrier in ("ANA", "JAL"):
    for cabin in ("C", "F", "PY"):
        ac.append((carrier, "TYO-LON", cabin, "fuel_surcharge", "ow", 62000, "2026-11-01〜12-31発券", "ANA_FUEL_2611" if carrier == "ANA" else "JAL_FUEL_2611", "B", ""))
        ac.append((carrier, "TYO-LON", cabin, "jp_airport_fees_tax", "rt", jp_side, "2026-07-01以降", "NRT_PSFC", "A", ""))
        ac.append((carrier, "TYO-LON", cabin, "dest_taxes", "rt", 58000, "2026", "UK_APD_2026", "A/EST", "英国APD 2026-27 Band C standard £253（PY/C/F）≈50,600円＋ヒースロー空港料金の目安約8,000円"))
write("award_cash_costs.csv", ["carrier", "route_id", "cabin", "component", "basis", "amount_jpy", "period_label", "source_id", "confidence", "notes"], ac)

# ----------------------------------------------------------------------------
# cash alternatives (price_low/mode/high per band). All JPY, tax-inclusive unless noted in notes.
# ----------------------------------------------------------------------------
ca = []
H = ["route_id", "cabin_equiv", "band_id", "provider", "product", "basis", "price_low_jpy", "price_mode_jpy", "price_high_jpy",
     "extra_fees_rt_jpy", "access_adj_rt_jpy", "equivalence", "own_carrier", "source_id", "confidence", "notes"]

def alt(route, cabin, provider, product, basis, bands_prices, equivalence, own="", extra=0, access=0, src="", conf="", notes=""):
    for band, (lo, mo, hi) in bands_prices.items():
        ca.append((route, cabin, band, provider, product, basis, lo, mo, hi, extra, access, equivalence, own, src, conf, notes))

# ---- domestic (one-way prices) ----
# own-carrier early-bird fares on trunk routes (ANA/JAL). Sources: ANA time sales 2026, sorahapi/travelko calendars Nov 2026, JAL site date-minimums.
trunk_own = {"D1": (9570, 12500, 15000), "D2": (15000, 17500, 21000), "D3": (23000, 27000, 33600), "D4": (24000, 27500, 35000)}
for route in ("HND-FUK", "HND-CTS"):
    for carrier in ("ANA", "JAL"):
        alt(route, "Y", carrier, "早割（タイムセール/セール〜スタンダード）", "ow", trunk_own, "same", own=carrier, src="DOM_FARES_2026", conf="B/EST",
            notes="D1: ANAタイムセール11,220〜11,880円・ソラハピ11/2月12,890円; D2: ソラハピ17,630〜18,890円・ANA往復35,040円; D3: ソラハピ11/20金26,890/28,740円・ANA金曜出発往復67,215円; D4: JAL 8/19 25,130〜28,410円")
oka_own = {"D1": (9500, 13000, 15500), "D2": (15000, 18000, 22000), "D3": (22000, 27000, 32000), "D4": (25000, 29000, 38000)}
for carrier in ("ANA", "JAL"):
    alt("HND-OKA", "Y", carrier, "早割（タイムセール/セール〜スタンダード）", "ow", oka_own, "same", own=carrier, src="DOM_FARES_2026", conf="B/EST",
        notes="D1: ANAタイムセール9,500〜11,880円・トラベルコANA最安13,881円・JAL 4/17土15,230円; D2: 幹線と同構造; D3/D4: JAL 8/19 28,410円・ANA直前往復例")
itm_own = {"D1": (9570, 12000, 14500), "D2": (13000, 15500, 18000), "D3": (19000, 23000, 28000), "D4": (20000, 24500, 30000)}
for carrier in ("ANA", "JAL"):
    alt("HND-ITM", "Y", carrier, "早割", "ow", itm_own, "same", own=carrier, src="DOM_FARES_2026", conf="C/EST",
        notes="D1: ANAタイムセール9,570円; D2: JAL 11/10火（6日前）16,320円; D3/D4: 幹線パターンから推定")
# Skymark (HND-FUK/CTS/OKA): official minima (いま得 7,800〜9,200円) and fare-table upper bands (36,200〜44,100円) are sourced; the band interior is interpolated
sky = {"D1": (7800, 9500, 12000), "D2": (10000, 13000, 17000), "D3": (15000, 20000, 27000), "D4": (18000, 24000, 36200)}
for route in ("HND-FUK", "HND-CTS"):
    alt(route, "Y", "Skymark", "いま得（3日前まで・変更不可）/たす得", "ow", sky, "near", src="SKYMARK_FARES_2026", conf="A/EST",
        notes="いま得最安：羽田–福岡 8,400円（2025冬）、羽田–新千歳 7,800円（2026冬ダイヤ、公式）、期間A下限 9,200円。上限帯 36,200円（第三者）。中間帯は推定")
alt("HND-OKA", "Y", "Skymark", "いま得（3日前まで・変更不可）/たす得", "ow", {"D1": (7200, 9500, 12000), "D2": (10000, 13500, 18000), "D3": (15000, 20500, 27000), "D4": (18000, 24000, 36000)},
    "near", src="SKYMARK_FARES_2026", conf="A/EST", notes="いま得最安 7,200円（2025夏）、期間A下限 9,100円、上限帯 44,100円（普通運賃近傍の疑い）。中間帯は推定")
alt("HND-FUK", "Y", "StarFlyer", "そら旅（28日前まで）/STAR（前日まで）", "ow", {"D1": (10230, 12000, 15000), "D2": (13000, 16500, 21000), "D3": (20000, 27000, 35000), "D4": (25000, 33000, 47300)},
    "near", src="STARFLYER_FARES_2026", conf="A/EST", notes="公式運賃表（2026冬ダイヤ）：そら旅 10,230〜47,300円、STAR 11,440〜59,400円、普通運賃 54,780〜68,310円。需要帯への割り付けは推定")
alt("HND-OKA", "Y", "Solaseed", "バーゲン/ソラシドスペシャル〜通常", "ow", {"D1": (8100, 10010, 12500), "D2": (11000, 14000, 18000), "D3": (16000, 21000, 27000), "D4": (20000, 25000, 35000)},
    "near", src="SOLASEED_2026", conf="A/EST", notes="公式最安 10,010円（〜2027-03-27搭乗、2026-10時点）、ソラシドスペシャル 8,100円（2026-03〜05搭乗）。中間帯は推定")
# LCC via NRT (Peach/Jetstar). fare + fees(640 payment + ~560 PFC + 2,000 bag per ow = ~3,200 ow => 6,400 rt) + access adj (NRT vs HND: ~1,500-2,580 fare + ~60min => ~4,000 ow => 8,000 rt)
# LCC via NRT: Peach total-price display since 2024-10 (no payment fee); extras = checked bag 2,000 + PFC(NRT 390-450 + dest) ≈ 2,500/ow => 5,000/rt;
# access adjustment NRT vs HND ≈ 1,500-2,580 fare + ~60 min ≈ 4,000/ow => 8,000/rt. Peach non-sale ranges 2026-10: CTS 4,990-11,190 / FUK 5,590-12,490 / OKA 6,390-12,090 (C)
lcc_fuk = {"D1": (4790, 6500, 9000), "D2": (5590, 9000, 12490), "D3": (8000, 11500, 16000), "D4": (11000, 15000, 22000)}
alt("HND-FUK", "Y", "Peach/Jetstar", "成田発（運賃のみ。荷物・PFC・アクセス差は別列）", "ow", lcc_fuk, "near", extra=5000, access=8000, src="PEACH_SALE_202610", conf="B/EST",
    notes="セール 4,790〜5,000円（2026）、非セール価格帯 5,590〜12,490円（2026-10、C）、Jetstar Starter最安 5,480円（2026冬）。D3/D4は推定")
lcc_cts = {"D1": (4000, 6000, 8500), "D2": (4990, 8000, 11190), "D3": (7000, 10500, 15000), "D4": (10000, 14000, 21000)}
alt("HND-CTS", "Y", "Peach/Jetstar", "成田発（運賃のみ）", "ow", lcc_cts, "near", extra=5000, access=8000, src="JETSTAR_SALE_202609", conf="B/EST",
    notes="セール 2,990〜4,490円（2026）、非セール価格帯 4,990〜11,190円（C）、Jetstar Starter最安 4,790円（2026冬追加便）。D3/D4は推定")
lcc_oka = {"D1": (5000, 7500, 10000), "D2": (6390, 9500, 12090), "D3": (8500, 12000, 16500), "D4": (11000, 15500, 23000)}
alt("HND-OKA", "Y", "Peach/Jetstar", "成田発（運賃のみ）", "ow", lcc_oka, "near", extra=5000, access=8000, src="PEACH_SALE_202610", conf="B/EST",
    notes="セール 5,000円（火水木限定タイムセール 2026-12〜2027-01搭乗）〜6,290円（Jetstar 2026冬）、非セール価格帯 6,390〜12,090円（C）。D3/D4は推定")
# Shinkansen Tokyo-Shin-Osaka (same price any weekday/time; season only ±200/400)
alt("HND-ITM", "Y", "JR東海", "東海道新幹線のぞみ指定席（EX早特21/EX早特7/正規）", "ow",
    {"D1": (12490, 12980, 14520), "D2": (12980, 13500, 14720), "D3": (12980, 14720, 14920), "D4": (14720, 15000, 15120)},
    "same", src="SHINKANSEN_FARES", conf="B",
    notes="EX早特21 12,980円（21日前・列車限定）、EX早特7 12,490円（ひかり・こだま）、正規指定席 通常期14,720/繁忙期14,920/最繁忙期15,120円。曜日・時間帯で不変")

# ---- international (round-trip prices, tax & fuel inclusive unless noted) ----
# Multipliers for bands relative to the D1 (sale/off-peak) level where only sale evidence exists:
#   D2 x1.35 (ANA/JAL regular display is 1.1-1.4x sale), D3 x1.2 on D2 (weekend departure; note estimate 1.1-1.3), D4 x1.9 on D1 (Hawaii measured 1.9x; JAL year-end 1.8x; range 1.8-2.5)
def scale(d1, d2=None, d3=None, d4=None):
    lo, mo, hi = d1
    d2 = d2 or (round(lo * 1.25), round(mo * 1.35), round(hi * 1.45))
    d3 = d3 or (round(d2[0] * 1.1), round(d2[1] * 1.2), round(d2[2] * 1.3))
    d4 = d4 or (round(mo * 1.8), round(mo * 2.1), round(hi * 2.5))
    return {"D1": d1, "D2": d2, "D3": d3, "D4": d4}

# Korea Y
for c in ("ANA", "JAL"):
    alt("TYO-SEL", "Y", c, "エコノミー（セール〜通常）", "rt", scale((30000, 36000, 45000), d2=(42000, 50000, 60000)), "same", own=c, src="INTL_FARES_2026", conf="EST",
        notes="ANA/JALソウル線の2026年セール実例は未取得。大韓航空公式表示34,790円〜・JAL台北50,000円から推定")
alt("TYO-SEL", "Y", "Peach/T'way/イースター", "LCC（税込目安）", "rt", scale((12000, 16000, 22000), d2=(18000, 24000, 32000), d4=(30000, 38000, 50000)), "near", extra=6000, src="LCC_INTL_2026", conf="B/EST",
    notes="Peach関西→金浦3,190円〜、羽田/成田→仁川5,000円〜（2026-10）、T'way 6,100〜12,600円（燃油諸税込）、イースター1,500円〜。往復税込1〜2万円。受託手荷物別（extra）")
alt("TYO-SEL", "Y", "ZIPAIR", "Standard（税抜8,000〜9,000円＋諸税）", "rt", scale((24000, 30000, 36000), d2=(30000, 36000, 44000)), "near", extra=15000, src="ZIPAIR_SALES_2026", conf="B/EST",
    notes="THANKS SALE 9,000円〜（税抜）、税込表示15,160円〜。受託手荷物7,500円/個")
# Taipei Y
for c in ("ANA", "JAL"):
    alt("TYO-TPE", "Y", c, "エコノミー（セール〜通常）", "rt", scale((50000, 55000, 65000)), "same", own=c, src="INTL_FARES_2026", conf="B/EST",
        notes="JAL台北往復50,000円〜（2026-10セール）。通常期・週末・繁忙期は係数推定")
alt("TYO-TPE", "Y", "チャイナエアライン", "エコノミー セール", "rt", scale((37600, 45000, 55000)), "near", src="INTL_FARES_2026", conf="B/EST", notes="CI 東京–台北 37,600円〜（2026-10）、5万円台（2026-06）")
alt("TYO-TPE", "Y", "Peach/Jetstar", "LCC（運賃＋諸税）", "rt", scale((22000, 28000, 35000), d4=(45000, 55000, 70000)), "near", extra=6000, src="LCC_INTL_2026", conf="B/EST",
    notes="Peach成田→台北7,990円〜（2026-01）、羽田→台北12,000円〜（2026-10）。片道諸税約3,000円")
# Bangkok / Singapore Y and C
for route, cityalt in (("TYO-BKK", ("タイ国際航空/スクート", (60000, 70000, 85000))), ("TYO-SIN", ("シンガポール航空/スクート", (56910, 68000, 85000)))):
    for c in ("ANA", "JAL"):
        alt(route, "Y", c, "エコノミー（セール〜通常）", "rt", scale((60600, 70000, 82000)), "same", own=c, src="INTL_FARES_2026", conf="B/EST",
            notes="ANA 2026-10セール バンコク66,600/シンガポール63,500円〜、JAL 72,400〜78,200円〜。通常期以降は係数推定")
    alt(route, "Y", cityalt[0], "FSC/LCC（税込）", "rt", scale(cityalt[1]), "near", src="INTL_FARES_2026", conf="B/EST",
        notes="SQ 56,910円（2026-03、諸費用込）、TG 82,000〜99,560円、Scoot 片道15,000〜19,000円（諸税込）")
    alt(route, "Y", "ZIPAIR", "Standard（税込2万円台片道）", "rt", scale((46000, 54000, 65000)), "near", extra=15000, src="ZIPAIR_SALES_2026", conf="B/EST",
        notes="THANKS SALE バンコク22,600/シンガポール15,680円（税抜）→税込2万円台。受託手荷物7,500円/個")
    for c in ("ANA", "JAL"):
        alt(route, "C", c, "ビジネス（セール〜通常）", "rt", scale((236600 if route == "TYO-BKK" else 304600, 280000 if route == "TYO-BKK" else 330000, 350000 if route == "TYO-BKK" else 400000)), "same", own=c, src="INTL_FARES_2026", conf="B/EST",
            notes="ANA 2026-10セール ビジネス バンコク236,600/シンガポール304,600円〜。通常期以降は係数推定")
    alt(route, "C", "シンガポール航空/マレーシア航空", "ビジネス セール", "rt", scale((179670, 256420, 311190)), "near", src="INTL_FARES_2026", conf="B/EST",
        notes="マレーシア航空179,670円（2026-10）、SQ 256,420円（2026-03）〜311,190円（2026-02）")
    alt(route, "C", "ZIPAIR", "ZIP Full-Flat（180°フルフラット・1-2-1、機内食・ラウンジ無し）", "rt", {"D1": (118000, 135000, 160000), "D2": (140000, 160000, 190000), "D3": (150000, 175000, 210000), "D4": (190000, 230000, 300000)},
        "near", extra=15000, src="ZIPAIR_FULLFLAT_2026", conf="B/EST", notes="Full-Flat 片道 バンコク 59,000円（2026夏）、シンガポール 58,800円（2026/27冬、税抜）。諸税・手荷物をextraに計上。通常期以降は推定")
# Hawaii Y / PY / C
for c in ("ANA", "JAL"):
    alt("TYO-HNL", "Y", c, "エコノミー（セール〜通常）", "rt", {"D1": (87000, 100000, 115000), "D2": (111400, 125000, 140000), "D3": (120000, 140000, 160000), "D4": (157000, 200000, 272676)}, "same", own=c, src="INTL_FARES_2026", conf="B",
        notes="JAL 87,000（2026-01/02）〜117,800（2026-10）〜136,800（2026-07）、ANA 105,400〜114,600（2026-08〜10）。年末年始：JAL最低157,000、実測272,676円（camptoaloha）")
alt("TYO-HNL", "Y", "ハワイアン航空/ユナイテッド", "エコノミー セール〜通常", "rt", {"D1": (79000, 90000, 105000), "D2": (93800, 115000, 130000), "D3": (105000, 130000, 150000), "D4": (180000, 240000, 310510)}, "near", src="INTL_FARES_2026", conf="B/C",
    notes="ハワイアン79,000〜93,800円（2024-25、総額）、UA目安 セール5.5〜8.5万（燃油別）〜直前13〜20万、年末年始UA 310,510円")
alt("TYO-HNL", "Y", "ZIPAIR", "Standard（税抜＋諸税＋荷物）", "rt", {"D1": (46800, 56000, 70000), "D2": (68900, 75000, 85000), "D3": (72000, 82000, 95000), "D4": (80000, 100000, 130000)}, "near", extra=25000, src="ZIPAIR_SALES_2026", conf="B/EST",
    notes="セール20,000〜23,400円、通常34,450〜35,000円（片道税抜）。諸税約5,000円/片道＋受託手荷物7,500円/個/片道をextraに計上。繁忙期は空席連動で上昇（推定）")
for c in ("ANA", "JAL"):
    alt("TYO-HNL", "PY", c, "プレミアムエコノミー", "rt", scale((200000, 220000, 250000), d4=(330000, 400000, 480000)), "same", own=c, src="INTL_FARES_2026", conf="B/EST", notes="ANAハワイ プレエコ セール200,000円〜（2026-10）")
alt("TYO-HNL", "PY", "ZIPAIR", "Full-Flat（プレエコ代替としては過剰品質）", "rt", {"D1": (160000, 175000, 200000), "D2": (195000, 205000, 220000), "D3": (205000, 215000, 235000), "D4": (230000, 260000, 320000)}, "near", extra=20000, src="ZIPAIR_SALES_2026", conf="B/EST", notes="Full-Flat 94,250〜95,000円（片道税抜）、セール『7万円台』")
for c in ("ANA", "JAL"):
    alt("TYO-HNL", "C", c, "ビジネス（セール〜通常）", "rt", scale((310170, 380000, 450000), d4=(700000, 880000, 1250000)), "same", own=c, src="BIZ_FARES_2026", conf="C/EST",
        notes="成田〜ホノルル往復ビジネス最安 310,170円（2026-06搭乗、キャリア未特定、newt調査）、ハワイアン フルフラット上位クラス目安 375,000〜825,000円。ANA/JAL自身のハワイCセール絶対額は未取得")
alt("TYO-HNL", "C", "ZIPAIR", "ZIP Full-Flat（180°フルフラット・1-2-1）", "rt", {"D1": (160000, 175000, 200000), "D2": (195000, 205000, 220000), "D3": (205000, 215000, 235000), "D4": (230000, 260000, 320000)}, "near", extra=20000, src="ZIPAIR_SALES_2026", conf="B/EST",
    notes="Full-Flat 94,250〜95,000円（片道税抜、通常）、セール実例『7万円台』。諸税＋座席指定料＋手荷物をextraに計上。機内食・ラウンジ無し")
# New York Y / PY / C / F
for c in ("ANA", "JAL"):
    alt("TYO-NYC", "Y", c, "エコノミー（セール〜通常）", "rt", {"D1": (155000, 170000, 190000), "D2": (176320, 201900, 230000), "D3": (195000, 230000, 270000), "D4": (280000, 340000, 420000)}, "same", own=c, src="INTL_FARES_2026", conf="B/EST",
        notes="JAL 155,000（2026-01）、ANA 165,000（2026-04）〜201,900（2026-10 Value）、JAL×AA 217,000、公式表示176,320円〜。繁忙期は係数推定")
alt("TYO-NYC", "Y", "チャイナエアライン/エバー/AA", "エコノミー（経由含む）", "rt", {"D1": (132900, 150000, 172400), "D2": (150000, 172400, 200000), "D3": (165000, 195000, 230000), "D4": (250000, 300000, 380000)}, "near", src="INTL_FARES_2026", conf="B/EST",
    notes="AA表示132,900円、EVA表示136,750〜147,050円、CI台北経由172,400円（燃油込）")
alt("TYO-NYC", "Y", "ZIPAIR", "Standard LAX（NYには就航せず、西海岸で代替）", "rt", {"D1": (90000, 105000, 120000), "D2": (105000, 121000, 140000), "D3": (115000, 135000, 160000), "D4": (150000, 190000, 240000)}, "lower", extra=23000, src="ZIPAIR_SALES_2026", conf="B/EST",
    notes="同等役務ではない（ロサンゼルス）ため equivalence=lower として V_real から除外")
for c in ("ANA", "JAL"):
    alt("TYO-NYC", "PY", c, "プレミアムエコノミー", "rt", scale((280000, 320000, 360000), d4=(500000, 600000, 720000)), "same", own=c, src="EST", conf="EST", notes="ANA/JAL北米プレエコのセール絶対額は未取得。EVA羽田–SFO 322,840円表示、エアプレミア片道58,960円から推定")
alt("TYO-NYC", "PY", "エバー航空/エアプレミア", "プレミアムエコノミー（西海岸：NYと同等役務ではない）", "rt", scale((120000, 200000, 322840), d4=(350000, 420000, 500000)), "lower", src="INTL_FARES_2026", conf="B/EST", notes="エアプレミア成田–LA片道58,960円、EVA羽田–SFO往復322,840円表示。ロサンゼルス線のため equivalence=lower（参考）")
for c in ("ANA", "JAL"):
    alt("TYO-NYC", "C", c, "ビジネス（タイムセール〜通常）", "rt", {"D1": (510000, 560000, 620000), "D2": (620000, 760000, 904000), "D3": (700000, 860000, 1000000), "D4": (950000, 1150000, 1400000)}, "same", own=c, src="BIZ_FARES_2026", conf="B",
        notes="ANA Business Light 東京–NY/LA 560,000円〜（2026-10タイムセール）、JAL 510,000円（2025-10セール）、JAL×AA 592,000円（2026-05）、JAL公式表示 904,000円〜（2026-09）、通常期サンプル858,230〜983,230円")
alt("TYO-NYC", "C", "外資系（AC/UA/AA/CI等）", "ビジネス（直行・経由、フルフラット）", "rt", {"D1": (450000, 500000, 560000), "D2": (520000, 600000, 700000), "D3": (580000, 680000, 800000), "D4": (750000, 900000, 1200000)}, "near", src="BIZ_FARES_2026", conf="C/EST",
    notes="エアカナダ 454,000円（2026-09）、UA 東京–LA 551,000円（旅行会社、2026）、AA 目安 450,000〜1,200,000円（2026-08）、CI台北経由 575,200円（2026-04）。D2以降は推定")
for c in ("ANA", "JAL"):
    alt("TYO-NYC", "F", c, "ファースト（現金）", "rt", {"D1": (1725020, 2200000, 2478610), "D2": (2200000, 2457430, 2800000), "D3": (2300000, 2600000, 3000000), "D4": (2500000, 2900000, 3300000)}, "same", own=c, src="BIZ_FARES_2026", conf="B/C",
        notes="2024-06調査：羽田–ロサンゼルス ファースト往復最安 ANA 2,478,610円／JAL 2,457,430円。ブログ引用：NYファースト 1,725,020円（2020）、2,567,050円、280万円。セールは実質存在しない")
alt("TYO-NYC", "F", "外資系ビジネス（フルフラット）", "ファースト代替＝ビジネス最安（シート同等性は劣る）", "rt", {"D1": (450000, 500000, 560000), "D2": (520000, 600000, 700000), "D3": (580000, 680000, 800000), "D4": (750000, 900000, 1200000)}, "near", src="BIZ_FARES_2026", conf="C/EST",
    notes="ファーストのセール市場は存在しないため、最安追求プロファイル（N）ではフルフラット・ビジネスを現実的代替とみなす（equivalence=near）。同一会社プロファイル（S）では正規Fを分子にする")
# London Y / PY / C / F
for c in ("ANA", "JAL"):
    alt("TYO-LON", "Y", c, "エコノミー（セール〜通常）", "rt", {"D1": (110000, 126000, 150000), "D2": (170000, 200000, 227110), "D3": (190000, 230000, 270000), "D4": (260000, 320000, 400000)}, "same", own=c, src="INTL_FARES_2026", conf="B/EST",
        notes="ANA欧州 11万円台〜126,000（2026-04）〜170,000（2026-10 Value）、JALヘルシンキ表示170,820〜227,110円。繁忙期は係数推定")
alt("TYO-LON", "Y", "エティハド/カタール/KLM", "エコノミー（経由・総額）", "rt", {"D1": (101640, 112330, 133670), "D2": (125000, 150000, 170000), "D3": (140000, 170000, 200000), "D4": (200000, 250000, 320000)}, "near", src="INTL_FARES_2026", conf="B",
    notes="エティハド101,640〜113,750円、カタール110,100〜170,340円、KLM 133,670〜166,470円（2025-11〜2026-09、税燃油込）")
for c in ("ANA", "JAL"):
    alt("TYO-LON", "PY", c, "プレミアムエコノミー", "rt", scale((300000, 340000, 380000), d4=(520000, 620000, 750000)), "same", own=c, src="EST", conf="EST", notes="欧州プレエコのセール絶対額は未取得。北米と同水準＋αの推定")
for c in ("ANA", "JAL"):
    alt("TYO-LON", "C", c, "ビジネス（セール〜通常）", "rt", {"D1": (490000, 540000, 600000), "D2": (600000, 700000, 820000), "D3": (660000, 780000, 920000), "D4": (850000, 1000000, 1250000)}, "same", own=c, src="BIZ_FARES_2026", conf="B/EST",
        notes="ANA 東京–欧州各都市 ビジネス 579,000円〜（2026-08セール）、ストックホルム 540,000円、JAL 東京–ロンドン 490,000円（2025-06セール）・パリ 490,000円（2025-10）、JAL公式表示 649,000円〜（2026-09）。D3/D4は推定")
alt("TYO-LON", "C", "エティハド/カタール/ターキッシュ", "ビジネス（経由・フルフラット）", "rt", {"D1": (311000, 400000, 478000), "D2": (420000, 500000, 580000), "D3": (460000, 560000, 650000), "D4": (600000, 720000, 900000)}, "near", src="BIZ_FARES_2026", conf="B/EST",
    notes="エティハド311,000〜327,000円（2026-05〜06）、カタール 羽田–マドリード 477,620円（総額、2026-08）、ターキッシュ 欧州主要都市 475,000円（総額、2025-11）・基本運賃513,000円（2026-10）。D2以降は推定")
for c in ("ANA", "JAL"):
    alt("TYO-LON", "F", c, "ファースト（現金）", "rt", {"D1": (2400000, 2800000, 2915000), "D2": (2600000, 2915000, 3200000), "D3": (2700000, 3000000, 3400000), "D4": (2900000, 3300000, 3800000)}, "same", own=c, src="VALUATION_NOTE", conf="C",
        notes="ブログ引用：欧州ファースト往復 約295万円／2,915,000円（dietmiler）、ロンドンF片道244万円（Travel Kurarin）")
alt("TYO-LON", "F", "外資系ビジネス（フルフラット）", "ファースト代替＝ビジネス最安", "rt", {"D1": (311000, 400000, 478000), "D2": (420000, 500000, 580000), "D3": (460000, 560000, 650000), "D4": (600000, 720000, 900000)}, "near", src="BIZ_FARES_2026", conf="B/EST", notes="プロファイルNではフルフラット・ビジネスをファーストの現実的代替とみなす")
# Sydney Y / C
for c in ("ANA", "JAL"):
    alt("TYO-SYD", "Y", c, "エコノミー（セール〜通常）", "rt", scale((128000, 145000, 170000)), "same", own=c, src="INTL_FARES_2026", conf="B/EST", notes="ANAシドニー128,000円〜（2026-10セール）")
alt("TYO-SYD", "Y", "外資系/経由", "エコノミー（経由含む）", "rt", scale((110000, 130000, 155000)), "near", src="EST", conf="EST", notes="豪州線の外資系2026年セール実例は未取得。直行セール比0.85の推定")
for c in ("ANA", "JAL"):
    alt("TYO-SYD", "C", c, "ビジネス", "rt", scale((400000, 470000, 550000), d4=(800000, 990000, 1375000)), "same", own=c, src="EST", conf="EST", notes="豪州ビジネスのセール実例未取得。東南アジアC（30万）と北米C（56万）の中間の推定")

# guard: for each (route, cabin, provider, product) the mode price must be non-decreasing D1<=D2<=D3<=D4
_chk = {}
for row in ca:
    _chk.setdefault((row[0], row[1], row[3], row[4]), {})[row[2]] = row[7]
for key, d in _chk.items():
    seq = [d.get(b) for b in ("D1", "D2", "D3", "D4") if d.get(b) is not None]
    if any(a > b_ for a, b_ in zip(seq, seq[1:])):
        raise SystemExit(f"non-monotone demand-band prices for {key}: {seq}")
write("cash_alternatives.csv", H, ca)

# ----------------------------------------------------------------------------
# availability priors: probability that the standard award seat (ANA) / base-mile seat (JAL) is obtainable for the desired flight
# All are analyst priors (EST) grounded in qualitative evidence; the Monte Carlo spans p_low..p_high.
# ----------------------------------------------------------------------------
av = []
def avail(carrier, market, group, probs, src, conf, note):
    for band, (p, lo, hi) in probs.items():
        av.append((carrier, market, group, band, p, lo, hi, src, conf, note))

avail("ANA", "domestic", "*", {"D1": (0.80, 0.60, 0.95), "D2": (0.55, 0.35, 0.75), "D3": (0.25, 0.10, 0.40), "D4": (0.10, 0.03, 0.25)}, "AVAIL_PRIOR", "EST",
      "固定チャート＋特典枠。幹線のL/R期は355日前発売直後に埋まりやすい一方、平日昼は直前まで残るという定性的報告に基づく事前分布")
avail("JAL", "domestic", "*", {"D1": (0.75, 0.55, 0.90), "D2": (0.45, 0.25, 0.65), "D3": (0.15, 0.05, 0.30), "D4": (0.05, 0.01, 0.15)}, "AVAIL_PRIOR", "EST",
      "基本マイル枠は『予測残席』連動で繁忙便は早期からPLUS化。公式『基本マイル数で取れる空席がない日は対象外』等の記述に基づく事前分布")
avail("ANA", "international", "economy", {"D1": (0.60, 0.40, 0.80), "D2": (0.40, 0.25, 0.60), "D3": (0.30, 0.15, 0.45), "D4": (0.08, 0.02, 0.20)}, "AVAIL_PRIOR", "EST", "ブログ群の一致した見解（年末年始・GW・夏休みは最難、平日閑散期は取りやすい）に基づく事前分布")
avail("ANA", "international", "premium", {"D1": (0.45, 0.25, 0.65), "D2": (0.30, 0.15, 0.45), "D3": (0.20, 0.10, 0.35), "D4": (0.05, 0.01, 0.12)}, "AVAIL_PRIOR", "EST", "同上")
avail("ANA", "international", "business", {"D1": (0.30, 0.12, 0.50), "D2": (0.18, 0.06, 0.32), "D3": (0.10, 0.03, 0.22), "D4": (0.03, 0.005, 0.10)}, "AVAIL_PRIOR", "EST", "長距離ビジネスの特典開放席は1便2〜4席程度（2026年解説）、空席待ち成功率は体験談で20〜50%・繁忙期ハワイCは10%以下")
avail("ANA", "international", "first", {"D1": (0.25, 0.10, 0.45), "D2": (0.12, 0.04, 0.25), "D3": (0.08, 0.02, 0.18), "D4": (0.02, 0.003, 0.08)}, "AVAIL_PRIOR", "EST", "ファーストは1機8席程度で特典枠はさらに少ない（mile-bible）")
avail("JAL", "international", "economy", {"D1": (0.30, 0.10, 0.50), "D2": (0.20, 0.05, 0.35), "D3": (0.12, 0.03, 0.25), "D4": (0.03, 0.005, 0.10)}, "JAL_AVAIL_SURVEY_2026", "C/EST", "1年先までの日別検索：東京→シドニーY 基本水準の日 87/365（24%）、東京→ソウルY 15/360（4%）。直前に基本枠が出る分を上乗せした事前分布")
avail("JAL", "international", "premium", {"D1": (0.15, 0.03, 0.30), "D2": (0.08, 0.02, 0.20), "D3": (0.05, 0.01, 0.15), "D4": (0.02, 0.003, 0.06)}, "JAL_AVAIL_SURVEY_2026", "C/EST", "東京→シドニーPY 基本水準の日 9/365")
avail("JAL", "international", "business", {"D1": (0.08, 0.02, 0.20), "D2": (0.04, 0.01, 0.12), "D3": (0.03, 0.005, 0.10), "D4": (0.01, 0.002, 0.05)}, "JAL_AVAIL_SURVEY_2026", "C/EST", "東京→シドニーC 基本水準の日 2/365。The Goal：ホノルルCは遠い日程で上限張り付き、直前に基本枠が出る")
avail("JAL", "international", "first", {"D1": (0.20, 0.08, 0.40), "D2": (0.10, 0.03, 0.22), "D3": (0.06, 0.02, 0.15), "D4": (0.02, 0.003, 0.08)}, "JAL_AVAIL_SURVEY_2026", "C/EST", "東京→シドニーF 最安水準の日 37/365（機材投入期間に集中）。PLUS対象外・キャンセル待ち可")
write("availability.csv", ["carrier", "market", "cabin_group", "band_id", "p_award", "p_low", "p_high", "source_id", "confidence", "notes"], av)

# ----------------------------------------------------------------------------
# JAL PLUS multipliers (k = required miles / base miles when the base tier is gone), by band.
# Caps (ceiling): domestic 4.1-5.4x (2026-10 caps), international 4.4-8.8x. Observations are sparse -> wide priors.
# ----------------------------------------------------------------------------
pm = [
    ("JAL", "domestic", "D1", 1.00, 1.10, 1.50, 2, "PLUS_PRIOR", "EST", "閑散平日昼：基本〜小幅上乗せ。観測：10月初旬平日の羽田-那覇で同日便に9,000（基本）と10,000（1.11倍）が混在"),
    ("JAL", "domestic", "D2", 1.05, 1.40, 2.20, 2, "PLUS_PRIOR", "EST", "通常期：観測 羽田-那覇クラスJ 1か月前にPLUS16,000（基本11,000の1.45倍）"),
    ("JAL", "domestic", "D3", 1.40, 2.20, 3.40, 0, "PLUS_PRIOR", "EST", "金曜夜・月曜朝：予測残席が少なく高倍率（便単位の実測は未取得）"),
    ("JAL", "domestic", "D4", 2.00, 3.00, 4.50, 3, "PLUS_PRIOR", "EST", "繁忙期：解説『お盆は片道2〜3万マイル以上』（9,500の2.1〜3.2倍）、奄美往復60,000（片道基本9,000の3.3倍）。上限 那覇49,000/9,500=5.2倍"),
    ("JAL", "international", "D1", 1.00, 1.30, 2.00, 0, "PLUS_PRIOR", "EST", "基本枠で取れる日は少なく（ソウルY 360日中15日）、小幅PLUSが常態"),
    ("JAL", "international", "D2", 1.10, 1.60, 2.60, 1, "PLUS_PRIOR", "EST", "観測：羽田-NY ビジネス『最少でも75,000』（基本55,000の1.36倍、2025-26）"),
    ("JAL", "international", "D3", 1.40, 2.20, 3.60, 0, "PLUS_PRIOR", "EST", ""),
    ("JAL", "international", "D4", 2.50, 4.00, 7.00, 2, "PLUS_PRIOR", "EST", "観測：ホノルルC お盆 往復367,000（旧基本80,000の4.6倍）、人気日程『54万マイル以上』（6.8倍）。上限 ホノルルC 8.8倍"),
]
write("plus_multipliers.csv", ["carrier", "market", "band_id", "k_p10", "k_p50", "k_p90", "n_obs", "source_id", "confidence", "notes"], pm)

# ----------------------------------------------------------------------------
# JAL PLUS caps (one-way, maximum miles when the base tier is unavailable). k x base is clipped at the cap.
# ----------------------------------------------------------------------------
caps = [
    ("JAL", "HND-ITM", "Y", "ow", 28000, "JAL_DOM_PLUS_202610", "A/C", "ゾーンC上限（公式スニペット）。区間のゾーン所属は推定"),
    ("JAL", "HND-FUK", "Y", "ow", 43500, "JAL_DOM_PLUS_202610", "A", "ゾーンE 普通席 基本8,500→PLUS〜43,500（公式表2026-10-26）"),
    ("JAL", "HND-CTS", "Y", "ow", 43500, "JAL_DOM_PLUS_202610", "A", "同上"),
    ("JAL", "HND-OKA", "Y", "ow", 49000, "JAL_DOM_PLUS_202610", "B", "ゾーンF 普通席 基本9,500→PLUS〜49,000（2026-10-01発券分〜。2024-07-11〜2026-09-30は44,500。51,000はクラスJ）"),
    ("JAL", "TYO-SEL", "Y", "ow", 61000, "JAL_INTL_PLUSCAP", "B", "公式表の大きい方の値／非公式シミュレーター転記と一致"),
    ("JAL", "TYO-SEL", "C", "ow", 79000, "JAL_INTL_PLUSCAP", "B", ""),
    ("JAL", "TYO-TPE", "Y", "ow", 88000, "JAL_INTL_PLUSCAP", "B", "やじり鳥2024-06は87,000"),
    ("JAL", "TYO-TPE", "C", "ow", 121000, "JAL_INTL_PLUSCAP", "B", ""),
    ("JAL", "TYO-BKK", "Y", "ow", 101000, "JAL_INTL_PLUSCAP", "B", ""),
    ("JAL", "TYO-BKK", "C", "ow", 200000, "JAL_INTL_PLUSCAP", "B", ""),
    ("JAL", "TYO-SIN", "Y", "ow", 105000, "JAL_INTL_PLUSCAP", "B", ""),
    ("JAL", "TYO-SIN", "C", "ow", 200000, "JAL_INTL_PLUSCAP", "B", ""),
    ("JAL", "TYO-HNL", "Y", "ow", 137000, "JAL_INTL_PLUSCAP", "A/B", "公式表（2026-04-16）スニペットと一致"),
    ("JAL", "TYO-HNL", "PY", "ow", 181000, "JAL_INTL_PLUSCAP", "B", ""),
    ("JAL", "TYO-HNL", "C", "ow", 377000, "JAL_INTL_PLUSCAP", "A/B", "公式表スニペットと一致"),
    ("JAL", "TYO-NYC", "Y", "ow", 206000, "JAL_INTL_PLUSCAP", "B", "羽田–JFK"),
    ("JAL", "TYO-NYC", "PY", "ow", 240000, "JAL_INTL_PLUSCAP", "B", ""),
    ("JAL", "TYO-NYC", "C", "ow", 502000, "JAL_INTL_PLUSCAP", "B", ""),
    ("JAL", "TYO-LON", "Y", "ow", 171000, "JAL_INTL_PLUSCAP", "A/B", "公式表スニペットと一致"),
    ("JAL", "TYO-LON", "PY", "ow", 181500, "JAL_INTL_PLUSCAP", "A/B", ""),
    ("JAL", "TYO-LON", "C", "ow", 441000, "JAL_INTL_PLUSCAP", "A/B", ""),
    ("JAL", "TYO-SYD", "Y", "ow", 128000, "JAL_INTL_PLUSCAP", "B", ""),
    ("JAL", "TYO-SYD", "C", "ow", 289000, "JAL_INTL_PLUSCAP", "A/B", "公式表（在外版）スニペットと一致"),
]
write("plus_caps.csv", ["carrier", "route_id", "cabin", "basis", "cap_miles", "source_id", "confidence", "notes"], caps)

# ----------------------------------------------------------------------------
# floor rates
# ----------------------------------------------------------------------------
fr = [
    # carrier, instrument, condition, yen/mile, min_miles, representative, kind, source, confidence, notes
    ("ANA", "ANA SKY コイン", "1〜9,999マイル（全会員）", 1.0, 1, 0, "coin", "ANA_SKYCOIN", "B", ""),
    ("ANA", "ANA SKY コイン", "一般会員・10,000マイル以上", 1.2, 10000, 1, "coin", "ANA_SKYCOIN", "C", "代表値：一般会員の実質フロア（公式表の本文は未取得）"),
    ("ANA", "ANA SKY コイン", "ANAゴールド/SFC・50,000マイル以上", 1.6, 50000, 0, "coin", "ANA_SKYCOIN", "B", ""),
    ("ANA", "ANA SKY コイン", "プレミアムメンバー・50,000〜200,000マイル", 1.7, 50000, 0, "coin", "ANA_SKYCOIN", "A", "上限"),
    ("ANA", "他社ポイント交換（楽天等）", "最大80%（年度2口目まで）", 0.8, 1, 1, "cash", "ANA_POINT_EXCH", "B", "現金に近い下限の代表値"),
    ("ANA", "他社ポイント交換（楽天等）", "2026-04-22以降の年度3口目以降（50%）", 0.4, 1, 0, "cash", "ANA_POINT_EXCH", "B", "大量交換時の下限"),
    ("JAL", "e JALポイント", "10,000マイル単位の交換", 1.5, 10000, 1, "coin", "JAL_EJAL", "A", "代表値：航空券・ツアー購入に限定、1年期限"),
    ("JAL", "e JALポイント", "1,000マイル単位の交換", 1.0, 1000, 0, "coin", "JAL_EJAL", "A", ""),
    ("JAL", "JALクーポン", "10,000マイル→12,000円相当", 1.2, 10000, 0, "coin", "JAL_EJAL", "B", ""),
    ("JAL", "Amazonギフト等", "10,000マイル→8,000円相当", 0.8, 10000, 1, "cash", "JAL_AMAZON", "B", "現金に近い下限の代表値"),
    ("JAL", "Amazonギフト等", "少額交換・キャンペーン外", 0.5, 1000, 0, "cash", "JAL_AMAZON", "EST", "下限の幅（推定）"),
]
write("floor_rates.csv", ["carrier", "instrument", "condition_ja", "yen_per_mile", "min_miles", "representative", "kind", "source_id", "confidence", "notes"], fr)

# ----------------------------------------------------------------------------
# anchors: the 'regular fare' numerators used by mileage blogs (recorded, NOT used as value basis)
# ----------------------------------------------------------------------------
an = [
    ("ANA", "HND-OKA", "Y", "フレックス（旧普通運賃）", 61300, "ow", 4.5, "ANCHOR_DOM_2026", "C", "JALフレックス羽田–那覇 61,300円（ローチケ旅行 2026-09更新）をANAにも適用。ANA公式PDF（2026-10-25〜搭乗）の東京=那覇行は最大82,610円の表示あり"),
    ("JAL", "HND-OKA", "Y", "フレックス（旧普通運賃）", 61300, "ow", 5.0, "ANCHOR_DOM_2026", "C", "ローチケ旅行掲載 JALフレックス 羽田–那覇 61,300円（2026-09-09更新）。manekaiは普通運賃基準で4〜6円/マイルと主張"),
    ("ANA", "HND-FUK", "Y", "フレックス", 54890, "ow", 4.0, "ANCHOR_DOM_2026", "C", "ANA新運賃『フレックス』東京–福岡 例示 54,890円〜（2026）。スターフライヤー普通運賃 54,780〜68,310円（公式）と整合"),
    ("JAL", "HND-FUK", "Y", "フレックス", 54000, "ow", 4.0, "ANCHOR_DOM_2026", "C/EST", "JALカード割引 39,270円（フレックス連動、約27%引き）から逆算"),
    ("ANA", "HND-CTS", "Y", "フレックス", 50760, "ow", 4.0, "ANCHOR_DOM_2026", "C", "ローチケ旅行掲載 フレックス 羽田–新千歳 50,760円"),
    ("JAL", "HND-CTS", "Y", "フレックス", 50760, "ow", 4.0, "ANCHOR_DOM_2026", "C", "同上（JALカード割引 37,180円と整合）"),
    ("ANA", "HND-ITM", "Y", "フレックス", 34450, "ow", 3.0, "ANCHOR_DOM_2026", "C", "ローチケ旅行掲載 フレックス 羽田–伊丹 34,450円（2026-09-09更新）"),
    ("JAL", "HND-ITM", "Y", "フレックス", 34450, "ow", 3.0, "ANCHOR_DOM_2026", "C", "同上"),
    ("ANA", "TYO-HNL", "C", "正規ビジネス運賃（ブログ推計）", 700000, "rt", 10.0, "VALUATION_NOTE", "C", "note くまろぅちゃん『60万〜80万円』"),
    ("JAL", "TYO-HNL", "C", "正規ビジネス運賃（ブログ推計）", 700000, "rt", 8.0, "VALUATION_NOTE", "C", "同上"),
    ("ANA", "TYO-NYC", "C", "通常期ビジネス運賃サンプル", 920000, "rt", 10.0, "VALUATION_NOTE", "C", "858,230〜983,230円（2025-12/2026-02サンプル）"),
    ("JAL", "TYO-NYC", "C", "通常期ビジネス運賃サンプル", 920000, "rt", 10.0, "VALUATION_NOTE", "C", "ANAサンプルを流用"),
    ("ANA", "TYO-NYC", "F", "正規ファースト運賃（ブログ分子）", 2800000, "rt", 18.0, "VALUATION_NOTE", "C", "burio 280万円÷15万マイル≒18円、2,567,050円÷165,000＝15.55円"),
    ("JAL", "TYO-NYC", "F", "正規ファースト運賃（ブログ分子）", 2800000, "rt", 16.0, "VALUATION_NOTE", "C", "The Goal：ファースト7〜16円"),
    ("ANA", "TYO-LON", "F", "正規ファースト運賃（ブログ分子）", 2915000, "rt", 17.87, "VALUATION_NOTE", "C", "dietmiler 2,915,000円÷165,000＝17.66〜17.87円"),
    ("JAL", "TYO-LON", "F", "正規ファースト運賃（ブログ分子）", 2915000, "rt", 17.94, "VALUATION_NOTE", "C", "haruwari パリ・ファースト17.94円"),
    ("ANA", "TYO-LON", "C", "通常期ビジネス運賃（推定）", 950000, "rt", 10.0, "EST", "EST", "北米Cサンプルと同水準の推定"),
    ("JAL", "TYO-LON", "C", "通常期ビジネス運賃（推定）", 950000, "rt", 10.0, "VALUATION_NOTE", "C", "価格.com：JAL 11万マイルでパリ往復ビジネス≒10円（現金約100万円）"),
    ("ANA", "TYO-SIN", "C", "正規ビジネス運賃（ブログ分子）", 730000, "rt", 9.12, "VALUATION_NOTE", "C", "haruwari シンガポール ビジネス9.12円（分母80,000マイル想定で逆算）"),
]
write("anchors.csv", ["carrier", "route_id", "cabin", "anchor_type", "anchor_price_jpy", "basis", "blog_claim_yen_per_mile", "source_id", "confidence", "notes"], an)

# representative cases for sensitivity
rep = [
    ("JAL", "HND-OKA", "Y", "D3"),
    ("ANA", "HND-OKA", "Y", "D4"),
    ("ANA", "HND-ITM", "Y", "D2"),
    ("ANA", "TYO-NYC", "C", "D4"),
    ("JAL", "TYO-HNL", "C", "D2"),
    ("ANA", "TYO-LON", "Y", "D1"),
]
write("representative_cases.csv", ["carrier", "route_id", "cabin", "band_id"], rep)
print("done")
