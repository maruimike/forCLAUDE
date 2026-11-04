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
    ("D1", "閑散平日昼", "火曜・水曜の10〜16時発・閑散期（国際線は閑散期の平日出発）", "L", "L", 0.15, 0.25, "旅客シェアは分析者の仮定（感応度分析で検証）"),
    ("D2", "通常", "通常期の平日・朝夕ピーク以外（国際線は通常期の平日出発）", "R", "R", 0.35, 0.40, "同上"),
    ("D3", "高需要時間帯", "金曜18〜20時発・月曜7〜8時発・日曜夕方発（国際線は通常期の週末出発）", "R", "R", 0.25, 0.20, "ANAは同じRシーズンのマイルだが特典枠が極端に少ない"),
    ("D4", "繁忙期", "3連休・年末年始・GW・お盆（ANA Hシーズン）", "H", "H", 0.25, 0.15, "ANA国内線の2026年Hシーズンは91日（年の25%）"),
]
write("demand_bands.csv", ["band_id", "label_ja", "description_ja", "ana_dom_season", "ana_intl_season", "traveler_weight", "calendar_share", "notes"], bands)

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

# JAL season mapping for F: the model maps JAL seasons as 'base'; F rows use L/R/H so we also add a 'base' alias = R for safety
# (handled in model via season_for: JAL -> 'base'; F cabins are evaluated with explicit season in run_analysis if present)

# ----------------------------------------------------------------------------
# award cash costs (RT unless basis=ow)
# ----------------------------------------------------------------------------
ac = []
pfc = {"HND": 580, "ITM": 340, "FUK": 110, "CTS": 370, "OKA": 240}
for route, (a, b, conf, note) in {
    "HND-ITM": ("HND", "ITM", "A", "羽田580＋伊丹340"),
    "HND-FUK": ("HND", "FUK", "A/B", "羽田580＋福岡110"),
    "HND-CTS": ("HND", "CTS", "A/C", "羽田580＋新千歳370（2026-10-25改定後額は未取得）"),
    "HND-OKA": ("HND", "OKA", "A", "羽田580＋那覇240"),
}.items():
    for carrier in ("ANA", "JAL"):
        ac.append((carrier, route, "*", "PFC", "ow", pfc[a] + pfc[b], "2026-09-01以降発券", "ANA_PFC" if carrier == "ANA" else "JAL_PFC_FAQ", conf, note))

# international: fuel surcharge (Nov-Dec 2026 issuance, one-way, same for ANA/JAL), Japan-side fees, destination taxes
fuel = {  # one-way JPY, 2026-11/12 issuance
    "TYO-SEL": (7100, "B"), "TYO-TPE": (15100, "B"), "TYO-BKK": (32000, "B"), "TYO-SIN": (32000, "B"),
    "TYO-HNL": (38500, "B"), "TYO-NYC": (62000, "B"), "TYO-LON": (62000, "B"), "TYO-SYD": (62000, "B"),
}
jp_side = 4100  # NRT: 2,460+700+1,000 ; HND: 2,950(+230)+1,000  -> ~4,100 per departure
dest_tax = {  # RT-equivalent JPY paid for destination side (arrival/departure taxes, airport charges). EST unless noted.
    "TYO-SEL": (4500, "EST", "韓国出国税1万ウォン＋空港施設使用料の目安"),
    "TYO-TPE": (3500, "EST", "台湾空港税の目安"),
    "TYO-BKK": (4500, "EST", "タイ空港使用料の目安"),
    "TYO-SIN": (8000, "EST", "チャンギ空港税の目安"),
    "TYO-HNL": (11500, "C", "ブログ実例：ハワイ往復エコ 諸税11,000〜12,000円（燃油除く、日本側含む可能性）"),
    "TYO-NYC": (13000, "C/EST", "米国 国際到着税・税関・入国審査・APHIS・PFC の目安。ZIPAIR LA往復諸税15,910円（日本側含む）と整合"),
    "TYO-LON": (30000, "EST", "英国APD（エコノミー）＋ヒースロー空港料金の目安。ビジネス以上はAPD高率で約2倍"),
    "TYO-SYD": (9000, "EST", "豪州出国税＋空港料金の目安"),
}
for route, (f, conf) in fuel.items():
    for carrier in ("ANA", "JAL"):
        src = "ANA_FUEL_2611" if carrier == "ANA" else "JAL_FUEL_2611"
        ac.append((carrier, route, "*", "fuel_surcharge", "ow", f, "2026-11-01〜12-31発券", src, conf, "特典航空券にも同額（公式明記）"))
        ac.append((carrier, route, "*", "jp_airport_fees_tax", "rt", jp_side, "2026", "NRT_PSFC", "A/C", "成田PSFC2,460＋PSSC700＋国際観光旅客税1,000（羽田は2,950＋230＋1,000）。往復で出発時1回"))
        d, dconf, dnote = dest_tax[route]
        ac.append((carrier, route, "*", "dest_taxes", "rt", d, "2026", "TAX_EST", dconf, dnote))
# London business/first: higher APD band
for carrier in ("ANA", "JAL"):
    for cabin in ("C", "F", "PY"):
        ac.append((carrier, "TYO-LON", cabin, "fuel_surcharge", "ow", 62000, "2026-11-01〜12-31発券", "ANA_FUEL_2611" if carrier == "ANA" else "JAL_FUEL_2611", "B", ""))
        ac.append((carrier, "TYO-LON", cabin, "jp_airport_fees_tax", "rt", jp_side, "2026", "NRT_PSFC", "A/C", ""))
        ac.append((carrier, "TYO-LON", cabin, "dest_taxes", "rt", 55000, "2026", "TAX_EST", "EST", "英国APD上位クラス料率（エコノミーの約2倍）＋空港料金。ブログ実例『欧州ビジネス往復 諸税4〜6.5万円』と整合"))
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
# Skymark (HND-FUK/CTS/OKA): 2026 fares not retrieved -> estimates at ~70-75% of ANA/JAL, flagged EST (gap-fill may update)
sky = {"D1": (7500, 9500, 12000), "D2": (10000, 13000, 17000), "D3": (15000, 19500, 25000), "D4": (17000, 22000, 28000)}
for route in ("HND-FUK", "HND-CTS"):
    alt(route, "Y", "Skymark", "いま得/たす得/通常", "ow", sky, "near", src="EST", conf="EST", notes="2026年実額未取得。ANA/JAL早割の約70〜75%と仮定（旧『いま得』10,000円等と整合）")
alt("HND-OKA", "Y", "Skymark", "いま得/たす得/通常", "ow", {"D1": (8000, 10500, 13000), "D2": (11000, 14500, 18000), "D3": (16000, 21000, 26000), "D4": (19000, 24000, 30000)},
    "near", src="EST", conf="EST", notes="同上")
# LCC via NRT (Peach/Jetstar). fare + fees(640 payment + ~560 PFC + 2,000 bag per ow = ~3,200 ow => 6,400 rt) + access adj (NRT vs HND: ~1,500-2,580 fare + ~60min => ~4,000 ow => 8,000 rt)
lcc_fuk = {"D1": (5000, 7500, 10000), "D2": (7000, 10000, 14000), "D3": (10000, 15000, 22000), "D4": (14000, 20000, 28000)}
alt("HND-FUK", "Y", "Peach/Jetstar", "成田発（運賃のみ。手数料・荷物・アクセス差は別列）", "ow", lcc_fuk, "near", extra=6400, access=8000, src="PEACH_SALE_202610", conf="A/EST",
    notes="D1セール5,000円はtabiris 2026-10（Peach成田→福岡）。非セール・直前・繁忙期は推定")
lcc_cts = {"D1": (4490, 7000, 10000), "D2": (7000, 9500, 13000), "D3": (10000, 14500, 21000), "D4": (13000, 19000, 27000)}
alt("HND-CTS", "Y", "Peach/Jetstar", "成田発（運賃のみ）", "ow", lcc_cts, "near", extra=6400, access=8000, src="JETSTAR_SALE_202609", conf="A/EST",
    notes="D1セール4,490円（Jetstar 2026-09）・4,000円（Peach 2026-10）。非セールは推定")
lcc_oka = {"D1": (6000, 8500, 11000), "D2": (8000, 11000, 15000), "D3": (12000, 16500, 23000), "D4": (16000, 22000, 30000)}
alt("HND-OKA", "Y", "Peach/Jetstar", "成田発（運賃のみ）", "ow", lcc_oka, "near", extra=6400, access=8000, src="PEACH_SALE_202610", conf="A/EST",
    notes="D1セール6,000円（Peach）・6,090円（Jetstar）。非セールは推定")
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
        alt(route, "C", c, "ビジネス（セール〜通常）", "rt", scale((236600 if route == "TYO-BKK" else 304600, 280000 if route == "TYO-BKK" else 330000, 350000 if route == "TYO-BKK" else 400000), d4=(400000, 460000, 550000)), "same", own=c, src="INTL_FARES_2026", conf="B/EST",
            notes="ANA 2026-10セール ビジネス バンコク236,600/シンガポール304,600円〜")
    alt(route, "C", "シンガポール航空/マレーシア航空", "ビジネス セール", "rt", scale((179670, 256420, 311190), d4=(400000, 460000, 550000)), "near", src="INTL_FARES_2026", conf="B/EST",
        notes="マレーシア航空179,670円（2026-10）、SQ 256,420円（2026-03）〜311,190円（2026-02）")
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
    alt("TYO-HNL", "C", c, "ビジネス（セール〜通常）", "rt", scale((350000, 420000, 500000), d4=(650000, 750000, 900000)), "same", own=c, src="EST", conf="EST",
        notes="ANA/JALハワイ ビジネスの2026年セール絶対額は未取得。ブログ推計の正規60〜80万円・東南アジアC実例から推定（要ギャップ調査）")
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
alt("TYO-NYC", "PY", "エバー航空/エアプレミア", "プレミアムエコノミー（西海岸）", "rt", scale((120000, 200000, 322840), d4=(350000, 420000, 500000)), "near", src="INTL_FARES_2026", conf="B/EST", notes="エアプレミア成田–LA片道58,960円、EVA羽田–SFO往復322,840円表示")
for c in ("ANA", "JAL"):
    alt("TYO-NYC", "C", c, "ビジネス（タイムセール〜通常）", "rt", {"D1": (560000, 620000, 700000), "D2": (700000, 858230, 983230), "D3": (800000, 950000, 1100000), "D4": (1000000, 1200000, 1500000)}, "same", own=c, src="VALUATION_NOTE", conf="B/C",
        notes="ANA東京–NYビジネス タイムセール560,000円〜（tabiris 2026-10-20）、通常期サンプル858,230〜983,230円（比較記事）")
alt("TYO-NYC", "C", "外資系（EVA/CI/大韓/UA等）", "ビジネス（経由含む・フルフラット）", "rt", {"D1": (420000, 500000, 600000), "D2": (500000, 600000, 720000), "D3": (560000, 680000, 820000), "D4": (750000, 900000, 1100000)}, "near", src="EST", conf="EST",
    notes="2026年の北米ビジネス セール絶対額は未取得（ギャップ調査中）。欧州ビジネス（エティハド31〜33万）・東南アジアC実例からの推定")
for c in ("ANA", "JAL"):
    alt("TYO-NYC", "F", c, "ファースト（現金）", "rt", {"D1": (1500000, 1725020, 2000000), "D2": (1800000, 2200000, 2567050), "D3": (2000000, 2400000, 2800000), "D4": (2400000, 2800000, 3200000)}, "same", own=c, src="VALUATION_NOTE", conf="C",
        notes="ブログ引用：NYファースト 1,725,020円（happy-mi-life 2020）、2,567,050円、280万円（burio）。セールは存在しない")
alt("TYO-NYC", "F", "外資系ビジネス（フルフラット）", "ファースト代替＝ビジネス最安（シート同等性は劣る）", "rt", {"D1": (420000, 500000, 600000), "D2": (500000, 600000, 720000), "D3": (560000, 680000, 820000), "D4": (750000, 900000, 1100000)}, "lower", src="EST", conf="EST",
    notes="ファーストの『同等役務』は定義困難。equivalence=lower で参考のみ")
# London Y / PY / C / F
for c in ("ANA", "JAL"):
    alt("TYO-LON", "Y", c, "エコノミー（セール〜通常）", "rt", {"D1": (110000, 126000, 150000), "D2": (170000, 200000, 227110), "D3": (190000, 230000, 270000), "D4": (260000, 320000, 400000)}, "same", own=c, src="INTL_FARES_2026", conf="B/EST",
        notes="ANA欧州 11万円台〜126,000（2026-04）〜170,000（2026-10 Value）、JALヘルシンキ表示170,820〜227,110円。繁忙期は係数推定")
alt("TYO-LON", "Y", "エティハド/カタール/KLM", "エコノミー（経由・総額）", "rt", {"D1": (101640, 112330, 133670), "D2": (125000, 150000, 170000), "D3": (140000, 170000, 200000), "D4": (200000, 250000, 320000)}, "near", src="INTL_FARES_2026", conf="B",
    notes="エティハド101,640〜113,750円、カタール110,100〜170,340円、KLM 133,670〜166,470円（2025-11〜2026-09、税燃油込）")
for c in ("ANA", "JAL"):
    alt("TYO-LON", "PY", c, "プレミアムエコノミー", "rt", scale((300000, 340000, 380000), d4=(520000, 620000, 750000)), "same", own=c, src="EST", conf="EST", notes="欧州プレエコのセール絶対額は未取得。北米と同水準＋αの推定")
for c in ("ANA", "JAL"):
    alt("TYO-LON", "C", c, "ビジネス（セール〜通常）", "rt", {"D1": (550000, 620000, 700000), "D2": (700000, 800000, 950000), "D3": (780000, 900000, 1050000), "D4": (950000, 1150000, 1400000)}, "same", own=c, src="EST", conf="EST",
        notes="ANA/JAL欧州ビジネスの2026年セール絶対額は未取得。北米C（56万〜98万円）と同構造の推定")
alt("TYO-LON", "C", "エティハド/カタール/ターキッシュ", "ビジネス（経由・フルフラット）", "rt", {"D1": (311000, 327000, 400000), "D2": (400000, 480000, 560000), "D3": (450000, 540000, 640000), "D4": (600000, 720000, 900000)}, "near", src="INTL_FARES_2026", conf="B/EST",
    notes="エティハド311,000〜327,000円（2026-05〜06）、ターキッシュ基本運賃513,000円（税燃油別）、カタール通常比15〜20%引き（絶対額未取得）")
for c in ("ANA", "JAL"):
    alt("TYO-LON", "F", c, "ファースト（現金）", "rt", {"D1": (2400000, 2800000, 2915000), "D2": (2600000, 2915000, 3200000), "D3": (2700000, 3000000, 3400000), "D4": (2900000, 3300000, 3800000)}, "same", own=c, src="VALUATION_NOTE", conf="C",
        notes="ブログ引用：欧州ファースト往復 約295万円／2,915,000円（dietmiler）、ロンドンF片道244万円（Travel Kurarin）")
alt("TYO-LON", "F", "外資系ビジネス（フルフラット）", "ファースト代替＝ビジネス最安", "rt", {"D1": (311000, 327000, 400000), "D2": (400000, 480000, 560000), "D3": (450000, 540000, 640000), "D4": (600000, 720000, 900000)}, "lower", src="INTL_FARES_2026", conf="B/EST", notes="参考のみ（lower）")
# Sydney Y / C
for c in ("ANA", "JAL"):
    alt("TYO-SYD", "Y", c, "エコノミー（セール〜通常）", "rt", scale((128000, 145000, 170000)), "same", own=c, src="INTL_FARES_2026", conf="B/EST", notes="ANAシドニー128,000円〜（2026-10セール）")
alt("TYO-SYD", "Y", "外資系/経由", "エコノミー（経由含む）", "rt", scale((110000, 130000, 155000)), "near", src="EST", conf="EST", notes="豪州線の外資系2026年セール実例は未取得。直行セール比0.85の推定")
for c in ("ANA", "JAL"):
    alt("TYO-SYD", "C", c, "ビジネス", "rt", scale((400000, 470000, 550000), d4=(650000, 780000, 950000)), "same", own=c, src="EST", conf="EST", notes="豪州ビジネスのセール実例未取得。東南アジアC（30万）と北米C（56万）の中間の推定")

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
avail("ANA", "international", "business", {"D1": (0.35, 0.15, 0.55), "D2": (0.20, 0.08, 0.35), "D3": (0.12, 0.05, 0.25), "D4": (0.03, 0.005, 0.10)}, "AVAIL_PRIOR", "EST", "ハワイ・北米ビジネスは『半年先でも取れない』『全席空席待ち』という報告")
avail("JAL", "international", "economy", {"D1": (0.55, 0.35, 0.75), "D2": (0.35, 0.20, 0.55), "D3": (0.25, 0.10, 0.40), "D4": (0.05, 0.01, 0.15)}, "AVAIL_PRIOR", "EST", "note集計『エコノミーの基本マイル日は存在するがビジネスは限られる』『基本マイル日は月の半分、全てGW後』")
avail("JAL", "international", "premium", {"D1": (0.40, 0.20, 0.60), "D2": (0.25, 0.10, 0.40), "D3": (0.15, 0.05, 0.30), "D4": (0.03, 0.005, 0.10)}, "AVAIL_PRIOR", "EST", "")
avail("JAL", "international", "business", {"D1": (0.30, 0.10, 0.50), "D2": (0.15, 0.05, 0.30), "D3": (0.10, 0.03, 0.20), "D4": (0.02, 0.003, 0.08)}, "AVAIL_PRIOR", "EST", "The Goal：ホノルルCは遠い日程で上限張り付き、直前に基本枠が出る")
write("availability.csv", ["carrier", "market", "cabin_group", "band_id", "p_award", "p_low", "p_high", "source_id", "confidence", "notes"], av)

# ----------------------------------------------------------------------------
# JAL PLUS multipliers (k = required miles / base miles when the base tier is gone), by band.
# Caps (ceiling): domestic 4.1-5.4x (2026-10 caps), international 4.4-8.8x. Observations are sparse -> wide priors.
# ----------------------------------------------------------------------------
pm = [
    ("JAL", "domestic", "D1", 1.00, 1.15, 1.60, 0, "PLUS_PRIOR", "EST", "閑散平日昼：基本〜小幅上乗せ"),
    ("JAL", "domestic", "D2", 1.15, 1.60, 2.40, 0, "PLUS_PRIOR", "EST", "通常期：段階的上乗せ"),
    ("JAL", "domestic", "D3", 1.60, 2.40, 3.50, 0, "PLUS_PRIOR", "EST", "金曜夜・月曜朝：予測残席が少なく高倍率。上限4.1〜4.7倍"),
    ("JAL", "domestic", "D4", 2.40, 3.30, 4.10, 0, "PLUS_PRIOR", "EST", "繁忙期：上限（那覇39,000/9,500=4.1倍）近傍に張り付く"),
    ("JAL", "international", "D1", 1.00, 1.30, 2.00, 0, "PLUS_PRIOR", "EST", ""),
    ("JAL", "international", "D2", 1.20, 1.80, 3.00, 0, "PLUS_PRIOR", "EST", ""),
    ("JAL", "international", "D3", 1.50, 2.30, 3.60, 0, "PLUS_PRIOR", "EST", ""),
    ("JAL", "international", "D4", 2.50, 3.60, 6.00, 0, "PLUS_PRIOR", "EST", "The Goal：ホノルルC 遠い日程で往復289,000（当時上限、基本の3.6倍）に張り付き"),
]
write("plus_multipliers.csv", ["carrier", "market", "band_id", "k_p10", "k_p50", "k_p90", "n_obs", "source_id", "confidence", "notes"], pm)

# ----------------------------------------------------------------------------
# JAL PLUS caps (one-way, maximum miles when the base tier is unavailable). k x base is clipped at the cap.
# ----------------------------------------------------------------------------
caps = [
    ("JAL", "HND-ITM", "Y", "ow", 28000, "JAL_DOM_PLUS_202610", "A/C", "ゾーンC上限（公式スニペット）。区間のゾーン所属は推定"),
    ("JAL", "HND-FUK", "Y", "ow", 37000, "EST", "EST", "ゾーンE上限は未取得。D 35,500とF 39,000の間と推定"),
    ("JAL", "HND-CTS", "Y", "ow", 37000, "EST", "EST", "同上"),
    ("JAL", "HND-OKA", "Y", "ow", 39000, "JAL_DOM_MILES", "A/C", "公式スニペット『東京–那覇 PLUS最大39,000』（クラスJ値混入の可能性あり）"),
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
    ("ANA", "ANA SKY コイン", "1〜9,999マイル（全会員）", 1.0, 1, 0, "ANA_SKYCOIN", "B", ""),
    ("ANA", "ANA SKY コイン", "一般会員・10,000マイル以上", 1.2, 10000, 1, "ANA_SKYCOIN", "C", "代表値：一般会員の実質フロア（公式表の本文は未取得）"),
    ("ANA", "ANA SKY コイン", "ANAゴールド/SFC・50,000マイル以上", 1.6, 50000, 0, "ANA_SKYCOIN", "B", ""),
    ("ANA", "ANA SKY コイン", "プレミアムメンバー・50,000〜200,000マイル", 1.7, 50000, 0, "ANA_SKYCOIN", "A", "上限"),
    ("ANA", "他社ポイント交換（楽天等）", "最大80%・2026-04-22以降は年度3口目から50%", 0.8, 1, 0, "ANA_POINT_EXCH", "B", "現金に近い下限（上限・逓減あり）"),
    ("JAL", "e JALポイント", "10,000マイル単位の交換", 1.5, 10000, 1, "JAL_EJAL", "A", "代表値：航空券・ツアー購入に限定、1年期限"),
    ("JAL", "e JALポイント", "1,000マイル単位の交換", 1.0, 1000, 0, "JAL_EJAL", "A", ""),
    ("JAL", "JALクーポン", "10,000マイル→12,000円相当", 1.2, 10000, 0, "JAL_EJAL", "B", ""),
    ("JAL", "Amazonギフト等", "10,000マイル→8,000円相当", 0.8, 10000, 0, "JAL_AMAZON", "B", "現金に近い下限"),
]
write("floor_rates.csv", ["carrier", "instrument", "condition_ja", "yen_per_mile", "min_miles", "representative", "source_id", "confidence", "notes"], fr)

# ----------------------------------------------------------------------------
# anchors: the 'regular fare' numerators used by mileage blogs (recorded, NOT used as value basis)
# ----------------------------------------------------------------------------
an = [
    ("ANA", "HND-OKA", "Y", "フレックス（旧普通運賃）", 52000, "ow", 4.5, "ANCHOR_DOM_EST", "EST", "2026年公式運賃表PDFは取得不能。2024〜25年の普通運賃水準（約5〜5.7万円）からの推定。manekaiは普通運賃基準で4〜6円/マイルと主張"),
    ("JAL", "HND-OKA", "Y", "フレックス（旧普通運賃）", 52000, "ow", 5.0, "ANCHOR_DOM_EST", "EST", "同上"),
    ("ANA", "HND-FUK", "Y", "フレックス", 46000, "ow", 4.0, "ANCHOR_DOM_EST", "EST", "推定"),
    ("JAL", "HND-FUK", "Y", "フレックス", 46000, "ow", 4.0, "ANCHOR_DOM_EST", "EST", "推定"),
    ("ANA", "HND-CTS", "Y", "フレックス", 42000, "ow", 4.0, "ANCHOR_DOM_EST", "EST", "推定"),
    ("JAL", "HND-CTS", "Y", "フレックス", 42000, "ow", 4.0, "ANCHOR_DOM_EST", "EST", "推定"),
    ("ANA", "HND-ITM", "Y", "フレックス", 30000, "ow", 3.0, "ANCHOR_DOM_EST", "EST", "推定"),
    ("JAL", "HND-ITM", "Y", "フレックス", 30000, "ow", 3.0, "ANCHOR_DOM_EST", "EST", "推定"),
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
