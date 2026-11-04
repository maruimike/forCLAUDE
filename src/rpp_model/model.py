"""
Real Purchasing Power (RPP) model for ANA / JAL miles.

For a traveller who wants a given trip (carrier x route x cabin x demand band), a mile is worth what it
saves when used in the best available way.  Two explicit consumer profiles are evaluated:

  N  最安追求プロファイル  – would otherwise pay the cheapest realistic alternative (own-carrier early-bird,
     LCC incl. fees/access, Shinkansen, ZIPAIR, foreign-carrier sale).  Alternative value of an unused mile =
     the cash-like exchange floor r_cash (≈0.8 yen: 他社ポイント・Amazon).
  S  同一会社利用プロファイル – would otherwise buy the ANA/JAL fare for the same product.  Alternative value
     of an unused mile = the coin/point floor r_coin (ANA SKY コイン 1.2, e JAL ポイント 1.5).

Paths available when the standard award seat exists (probability p):
    award : M_base miles + C cash
    coins : V_own / r_coin miles, no cash   (buy the own-carrier fare with SKY coins / e JAL points)
    keep  : pay V in cash, keep the miles (each worth r_alt)
When it does not exist (1-p): JAL may add  plus : k * M_base miles (clipped at the published cap) + C cash.

The traveller picks the path with the lowest wealth cost  cash + miles * r_alt.  The realised value per mile
of a miles path is (V - cash) / miles; of 'keep' it is r_alt.  The reported RPP for a band is the
probability-weighted mean of those per-mile values (mean-of-ratios convention), and the naive conditional
value rpp_award = (V - C) / M_base is reported alongside (it can be negative when fees exceed V).

All prices JPY, round trip (one-way inputs are doubled on load).
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np
import pandas as pd

PARAM_FILES = [
    "routes.csv", "demand_bands.csv", "award_miles.csv", "award_cash_costs.csv", "cash_alternatives.csv",
    "availability.csv", "plus_multipliers.csv", "floor_rates.csv", "anchors.csv",
]

PROFILES = {
    "N": dict(label_ja="最安追求（LCC・他社・新幹線・ZIPAIRも代替）", equivalence=("same", "near"), own_only=False, floor_kind="cash"),
    "S": dict(label_ja="同一会社利用（ANA/JALの有償運賃が代替）", equivalence=("same",), own_only=True, floor_kind="coin"),
}

CABIN_GROUP = {"Y": "economy", "PY": "premium", "C": "business", "F": "first", "J": "premium", "P": "premium"}


@dataclass
class Params:
    routes: pd.DataFrame
    bands: pd.DataFrame
    award_miles: pd.DataFrame
    award_cash: pd.DataFrame
    cash_alts: pd.DataFrame
    availability: pd.DataFrame
    plus_mult: pd.DataFrame
    floor_rates: pd.DataFrame
    anchors: pd.DataFrame
    sources: pd.DataFrame = field(default_factory=pd.DataFrame)
    plus_caps: pd.DataFrame = field(default_factory=pd.DataFrame)

    @classmethod
    def load(cls, param_dir: str | Path) -> "Params":
        d = Path(param_dir)
        fr = {f[:-4]: pd.read_csv(d / f, comment="#", skipinitialspace=True) for f in PARAM_FILES}
        sources_path = d.parent / "sources.csv"
        caps_path = d / "plus_caps.csv"
        p = cls(routes=fr["routes"], bands=fr["demand_bands"], award_miles=fr["award_miles"], award_cash=fr["award_cash_costs"],
                cash_alts=fr["cash_alternatives"], availability=fr["availability"], plus_mult=fr["plus_multipliers"],
                floor_rates=fr["floor_rates"], anchors=fr["anchors"],
                sources=pd.read_csv(sources_path) if sources_path.exists() else pd.DataFrame(),
                plus_caps=pd.read_csv(caps_path, comment="#", skipinitialspace=True) if caps_path.exists() else pd.DataFrame())
        p._normalise()
        p._validate()
        return p

    def _normalise(self) -> None:
        am = self.award_miles.copy()
        am["miles_rt"] = np.where(am["basis"].str.lower() == "ow", am["miles"] * 2, am["miles"])
        self.award_miles = am

        ca = self.cash_alts.copy()
        mult = np.where(ca["basis"].str.lower() == "ow", 2.0, 1.0)
        for col in ("extra_fees_rt_jpy", "access_adj_rt_jpy"):
            if col not in ca.columns:
                ca[col] = 0.0
            ca[col] = ca[col].fillna(0.0)
        for lvl in ("low", "mode", "high"):
            ca[f"total_{lvl}_rt"] = ca[f"price_{lvl}_jpy"] * mult + ca["extra_fees_rt_jpy"] + ca["access_adj_rt_jpy"]
        if "own_carrier" not in ca.columns:
            ca["own_carrier"] = ""
        ca["own_carrier"] = ca["own_carrier"].fillna("").astype(str).str.upper()
        self.cash_alts = ca

        ac = self.award_cash.copy()
        ac["amount_rt_jpy"] = ac["amount_jpy"] * np.where(ac["basis"].str.lower() == "ow", 2.0, 1.0)
        self.award_cash = ac

        if not self.plus_caps.empty:
            pc = self.plus_caps.copy()
            pc["cap_rt"] = np.where(pc["basis"].str.lower() == "ow", pc["cap_miles"] * 2, pc["cap_miles"])
            self.plus_caps = pc

        if "kind" not in self.floor_rates.columns:
            self.floor_rates["kind"] = "coin"

    def _validate(self) -> None:
        req = {
            "bands": {"band_id", "label_ja", "ana_dom_season", "ana_intl_season", "jal_dom_season", "jal_intl_season", "traveler_weight"},
            "award_miles": {"carrier", "route_id", "cabin", "basis", "season", "miles"},
            "award_cash": {"carrier", "route_id", "cabin", "component", "basis", "amount_jpy"},
            "cash_alts": {"route_id", "cabin_equiv", "band_id", "provider", "product", "basis", "price_low_jpy", "price_mode_jpy",
                          "price_high_jpy", "equivalence", "own_carrier"},
            "availability": {"carrier", "market", "cabin_group", "band_id", "p_award", "p_low", "p_high"},
            "plus_mult": {"carrier", "market", "band_id", "k_p10", "k_p50", "k_p90"},
            "floor_rates": {"carrier", "instrument", "yen_per_mile", "representative", "kind"},
            "anchors": {"carrier", "route_id", "cabin", "anchor_type", "anchor_price_jpy", "basis"},
        }
        for name, cols in req.items():
            missing = cols - set(getattr(self, name).columns)
            if missing:
                raise ValueError(f"{name}: missing columns {sorted(missing)}")
        if not math.isclose(self.bands["traveler_weight"].sum(), 1.0, abs_tol=1e-6):
            raise ValueError("demand_bands.traveler_weight must sum to 1")
        for carrier in ("ANA", "JAL"):
            for kind in ("coin", "cash"):
                if floor_rate(self, carrier, kind) is None:
                    raise ValueError(f"floor_rates: no representative '{kind}' rate for {carrier}")


# ----------------------------------------------------------------------------------------------------
# lookups
# ----------------------------------------------------------------------------------------------------
def cabin_group(cabin: str) -> str:
    return CABIN_GROUP.get(cabin, "economy")


def band_row(p: Params, band_id: str) -> pd.Series:
    return p.bands.loc[p.bands["band_id"] == band_id].iloc[0]


def seasons_for(p: Params, carrier: str, market: str, band_id: str) -> list[str]:
    """Candidate award-chart seasons for a band, in priority order."""
    row = band_row(p, band_id)
    if carrier == "ANA":
        return [row["ana_dom_season"] if market == "domestic" else row["ana_intl_season"]]
    # JAL: Y/PY/C use a flat 'base' chart; First uses an L/R/H chart
    return ["base", row["jal_dom_season"] if market == "domestic" else row["jal_intl_season"]]


def award_miles_rt(p: Params, carrier: str, route_id: str, cabin: str, seasons: list[str]) -> tuple[float, str] | None:
    am = p.award_miles
    for s in seasons:
        sel = am[(am.carrier == carrier) & (am.route_id == route_id) & (am.cabin == cabin) & (am.season == s)]
        if not sel.empty:
            return float(sel["miles_rt"].iloc[0]), s
    return None


def min_award_miles_rt(p: Params, carrier: str, route_id: str, cabin: str) -> float | None:
    am = p.award_miles
    sel = am[(am.carrier == carrier) & (am.route_id == route_id) & (am.cabin == cabin)]
    return float(sel["miles_rt"].min()) if not sel.empty else None


def award_cash_rt(p: Params, carrier: str, route_id: str, cabin: str) -> tuple[float, dict]:
    """Cash collected on an award: cabin-agnostic ('*') components, overlaid by cabin-specific ones."""
    ac = p.award_cash
    base = ac[(ac.carrier == carrier) & (ac.route_id == route_id) & (ac.cabin == "*")]
    spec = ac[(ac.carrier == carrier) & (ac.route_id == route_id) & (ac.cabin == cabin)]
    comp = base.groupby("component")["amount_rt_jpy"].sum().to_dict()
    comp.update(spec.groupby("component")["amount_rt_jpy"].sum().to_dict())
    return float(sum(comp.values())), comp


def own_carrier_fare(p: Params, carrier: str, route_id: str, cabin: str, band_id: str) -> dict | None:
    ca = p.cash_alts
    sel = ca[(ca.route_id == route_id) & (ca.cabin_equiv == cabin) & (ca.band_id == band_id) & (ca.own_carrier == carrier)]
    if sel.empty:
        return None
    r = sel.sort_values("total_mode_rt").iloc[0]
    return dict(low=float(r.total_low_rt), mode=float(r.total_mode_rt), high=float(r.total_high_rt), provider=r.provider, product=r["product"])


def v_real(p: Params, route_id: str, cabin: str, band_id: str, equivalence=("same", "near")) -> dict | None:
    ca = p.cash_alts
    sel = ca[(ca.route_id == route_id) & (ca.cabin_equiv == cabin) & (ca.band_id == band_id) & (ca.equivalence.isin(equivalence))]
    if sel.empty:
        return None
    r = sel.sort_values("total_mode_rt").iloc[0]
    return dict(low=float(r.total_low_rt), mode=float(r.total_mode_rt), high=float(r.total_high_rt), provider=r.provider,
                product=r["product"], n_alternatives=int(len(sel)))


def availability(p: Params, carrier: str, market: str, cabin: str, band_id: str) -> tuple[float, float, float]:
    av = p.availability
    for g in (cabin_group(cabin), "*"):
        sel = av[(av.carrier == carrier) & (av.market == market) & (av.cabin_group == g) & (av.band_id == band_id)]
        if not sel.empty:
            r = sel.iloc[0]
            return float(r.p_award), float(r.p_low), float(r.p_high)
    raise KeyError(f"availability: {carrier}/{market}/{cabin}/{band_id}")


def plus_applies(carrier: str, market: str, cabin: str) -> bool:
    """JAL 特典航空券PLUS applies to Y/PY/C (and domestic J/F); international First is excluded."""
    return carrier == "JAL" and not (market == "international" and cabin == "F")


def plus_multiplier(p: Params, carrier: str, market: str, band_id: str) -> tuple[float, float, float] | None:
    pm = p.plus_mult
    sel = pm[(pm.carrier == carrier) & (pm.market == market) & (pm.band_id == band_id)]
    if sel.empty:
        return None
    r = sel.iloc[0]
    return float(r.k_p10), float(r.k_p50), float(r.k_p90)


def plus_cap_rt(p: Params, carrier: str, route_id: str, cabin: str) -> float | None:
    pc = p.plus_caps
    if pc.empty:
        return None
    sel = pc[(pc.carrier == carrier) & (pc.route_id == route_id) & (pc.cabin == cabin)]
    return float(sel["cap_rt"].iloc[0]) if not sel.empty else None


def floor_rate(p: Params, carrier: str, kind: str = "coin") -> float | None:
    fr = p.floor_rates
    sel = fr[(fr.carrier == carrier) & (fr.kind == kind) & (fr.representative == 1)]
    return float(sel["yen_per_mile"].iloc[0]) if not sel.empty else None


def floor_range(p: Params, carrier: str, kind: str) -> tuple[float, float]:
    fr = p.floor_rates
    sel = fr[(fr.carrier == carrier) & (fr.kind == kind)]
    return float(sel.yen_per_mile.min()), float(sel.yen_per_mile.max())


# ----------------------------------------------------------------------------------------------------
# core
# ----------------------------------------------------------------------------------------------------
def choose_path(paths: list[tuple[str, float, float]], r_alt: float) -> tuple[str, float, float]:
    """paths: (name, miles, cash). Pick the lowest wealth cost cash + miles * r_alt."""
    return min(paths, key=lambda t: t[2] + t[1] * r_alt)


def per_mile_value(V: float, miles: float, cash: float, r_alt: float) -> float:
    return (V - cash) / miles if miles > 0 else r_alt


def compute_case(p: Params, carrier: str, route_id: str, cabin: str, band_id: str, profile: str = "N",
                 v_override: float | None = None, p_override: float | None = None, k_override: float | None = None,
                 c_override: float | None = None, r_alt_override: float | None = None, r_coin_override: float | None = None,
                 v_own_override: float | None = None) -> dict | None:
    prof = PROFILES[profile]
    route = p.routes.loc[p.routes.route_id == route_id].iloc[0]
    market = route["market"]

    found = award_miles_rt(p, carrier, route_id, cabin, seasons_for(p, carrier, market, band_id))
    if found is None:
        return None
    m_base, season = found

    own = own_carrier_fare(p, carrier, route_id, cabin, band_id)
    if prof["own_only"]:
        if own is None:
            return None
        vr = dict(own)
        vr["n_alternatives"] = 1
    else:
        vr = v_real(p, route_id, cabin, band_id, equivalence=prof["equivalence"])
        if vr is None:
            return None
    V = float(v_override) if v_override is not None else vr["mode"]
    V_own = float(v_own_override) if v_own_override is not None else (own["mode"] if own else None)

    C, comp = award_cash_rt(p, carrier, route_id, cabin)
    if c_override is not None:
        C = float(c_override)
    p_av, p_lo, p_hi = availability(p, carrier, market, cabin, band_id)
    if p_override is not None:
        p_av = float(p_override)
    r_coin = float(r_coin_override) if r_coin_override is not None else floor_rate(p, carrier, "coin")
    r_alt = float(r_alt_override) if r_alt_override is not None else floor_rate(p, carrier, prof["floor_kind"])

    km = plus_multiplier(p, carrier, market, band_id) if plus_applies(carrier, market, cabin) else None
    k = (float(k_override) if k_override is not None else km[1]) if km is not None else None
    cap = plus_cap_rt(p, carrier, route_id, cabin)
    m_plus = None
    if k is not None:
        m_plus = k * m_base
        if cap is not None:
            m_plus = min(m_plus, cap)

    common = [("keep", 0.0, V)]
    if V_own is not None:
        common.append(("coins", V_own / r_coin, 0.0))
    pathA = choose_path([("award", m_base, C)] + common, r_alt)
    pathB = choose_path(([("plus", m_plus, C)] if m_plus is not None else []) + common, r_alt)

    vA = per_mile_value(V, pathA[1], pathA[2], r_alt)
    vB = per_mile_value(V, pathB[1], pathB[2], r_alt)
    rpp = p_av * vA + (1 - p_av) * vB
    rpp_award = (V - C) / m_base
    rpp_plus = (V - C) / m_plus if m_plus else np.nan
    rpp_coins = V / (V_own / r_coin) if V_own else np.nan

    return dict(
        carrier=carrier, route_id=route_id, route_label=route["label_ja"], market=market, group=route.get("group", ""),
        cabin=cabin, band_id=band_id, profile=profile, season=season,
        m_base_rt=m_base, v_real_rt=V, v_real_low=vr["low"], v_real_high=vr["high"], v_real_provider=vr["provider"],
        v_real_product=vr["product"], v_own_rt=V_own if V_own is not None else np.nan,
        v_own_low=own["low"] if own else np.nan, v_own_high=own["high"] if own else np.nan,
        c_cash_rt=C, c_components=comp, p_award=p_av, p_low=p_lo, p_high=p_hi, k_plus=k, plus_cap_rt=cap, m_plus_rt=m_plus,
        r_coin=r_coin, r_alt=r_alt,
        path_if_available=pathA[0], path_if_unavailable=pathB[0], v_if_available=vA, v_if_unavailable=vB,
        award_used=(pathA[0] == "award"), plus_used=(pathB[0] == "plus"),
        m_expected_rt=p_av * pathA[1] + (1 - p_av) * pathB[1], c_expected_rt=p_av * pathA[2] + (1 - p_av) * pathB[2],
        rpp=rpp, rpp_award=rpp_award, rpp_plus=rpp_plus, rpp_coins=rpp_coins,
    )


def enumerate_cases(p: Params) -> list[tuple[str, str, str]]:
    combos = set()
    have_alt = set(map(tuple, p.cash_alts[["route_id", "cabin_equiv"]].drop_duplicates().values))
    for _, r in p.award_miles[["carrier", "route_id", "cabin"]].drop_duplicates().iterrows():
        if (r.route_id, r.cabin) in have_alt:
            combos.add((r.carrier, r.route_id, r.cabin))
    return sorted(combos)


def run_all(p: Params) -> pd.DataFrame:
    """One row per (carrier, route, cabin, band) carrying both profiles (N = main, S = same-carrier)."""
    rows = []
    for carrier, route_id, cabin in enumerate_cases(p):
        for band_id in p.bands["band_id"]:
            n = compute_case(p, carrier, route_id, cabin, band_id, profile="N")
            if n is None:
                continue
            s = compute_case(p, carrier, route_id, cabin, band_id, profile="S")
            row = {k: v for k, v in n.items() if k != "profile"}
            row.update({
                "rpp_N": n["rpp"], "rpp_award_N": n["rpp_award"], "award_used_N": n["award_used"], "plus_used_N": n["plus_used"],
                "path_avail_N": n["path_if_available"], "path_unavail_N": n["path_if_unavailable"], "v_real_N": n["v_real_rt"],
                "rpp_S": s["rpp"] if s else np.nan, "rpp_award_S": s["rpp_award"] if s else np.nan,
                "award_used_S": s["award_used"] if s else np.nan, "path_avail_S": s["path_if_available"] if s else "",
                "path_unavail_S": s["path_if_unavailable"] if s else "", "v_real_S": s["v_real_rt"] if s else np.nan,
            })
            rows.append(row)
    df = pd.DataFrame(rows)
    return df.merge(p.bands[["band_id", "label_ja", "traveler_weight"]].rename(columns={"label_ja": "band_label"}), on="band_id", how="left")


def weighted_summary(df: pd.DataFrame) -> pd.DataFrame:
    """Traveller-weighted mean of per-band RPP (mean-of-ratios), per (carrier, route, cabin)."""
    def agg(g):
        w = g["traveler_weight"] / g["traveler_weight"].sum()
        out = dict(route_label=g["route_label"].iloc[0], market=g["market"].iloc[0], group=g["group"].iloc[0],
                   v_real_N_wavg=(g["v_real_N"] * w).sum(), v_real_S_wavg=(g["v_real_S"] * w).sum(), c_cash_rt=g["c_cash_rt"].iloc[0],
                   m_base_min=g["m_base_rt"].min(), m_base_max=g["m_base_rt"].max())
        for prof in ("N", "S"):
            out[f"rpp_{prof}_wavg"] = (g[f"rpp_{prof}"] * w).sum()
            out[f"rpp_{prof}_min"] = g[f"rpp_{prof}"].min()
            out[f"rpp_{prof}_max"] = g[f"rpp_{prof}"].max()
            out[f"rpp_award_{prof}_wavg"] = (g[f"rpp_award_{prof}"] * w).sum()
            out[f"award_used_share_{prof}"] = (g[f"award_used_{prof}"].astype(float) * w).sum()
        return pd.Series(out)
    return df.groupby(["carrier", "route_id", "cabin"]).apply(agg, include_groups=False).reset_index()


def anchored_values(p: Params, df: pd.DataFrame) -> pd.DataFrame:
    """The mileage-blog valuation: regular fare / lowest-season miles, no cash deduction, no availability."""
    an = p.anchors.copy()
    an["anchor_rt_jpy"] = np.where(an["basis"].str.lower() == "ow", an["anchor_price_jpy"] * 2, an["anchor_price_jpy"])
    out = []
    for _, a in an.iterrows():
        sub = df[(df.carrier == a.carrier) & (df.route_id == a.route_id) & (df.cabin == a.cabin)]
        if sub.empty:
            continue
        m_min = sub["m_base_rt"].min()
        out.append(dict(carrier=a.carrier, route_id=a.route_id, route_label=sub["route_label"].iloc[0], cabin=a.cabin,
                        anchor_type=a.anchor_type, anchor_rt_jpy=a.anchor_rt_jpy, m_min_rt=m_min,
                        anchored_yen_per_mile=a.anchor_rt_jpy / m_min, blog_claim_yen_per_mile=a.get("blog_claim_yen_per_mile", np.nan)))
    return pd.DataFrame(out)


def decomposition(p: Params, df: pd.DataFrame, carrier: str, route_id: str, cabin: str, band_id: str, profile: str = "N") -> list[tuple[str, float]]:
    """Waterfall from the anchored ('見せかけ') value to RPP for one case:
       anchor/m_min -> realistic numerator -> minus cash fees -> band season miles -> availability & rational path."""
    an = anchored_values(p, df)
    a = an[(an.carrier == carrier) & (an.route_id == route_id) & (an.cabin == cabin)]
    res = compute_case(p, carrier, route_id, cabin, band_id, profile=profile)
    if a.empty or res is None:
        raise ValueError("decomposition: anchor or case missing")
    m_min = float(a.m_min_rt.iloc[0])
    s0 = float(a.anchored_yen_per_mile.iloc[0])
    s1 = res["v_real_rt"] / m_min
    s2 = (res["v_real_rt"] - res["c_cash_rt"]) / m_min
    s3 = res["rpp_award"]
    s4 = res["rpp"]
    return [("見せかけ\n（正規運賃÷最低マイル）", s0), ("①分子を現実的な\n代替価格に置換", s1 - s0), ("②現金持ち出し\n（燃油・諸税）を控除", s2 - s1),
            ("③需要帯のマイル\n（シーズン）に置換", s3 - s2), ("④空席確率と\n合理的経路選択", s4 - s3)]
