"""
Real Purchasing Power Parity (RPP) model for ANA / JAL miles.

Core identity (per carrier x route x cabin x demand band):

    RPP_eff [yen/mile] = (V_real - E[C_cash]) / M_effective

where
    V_real        : realistic cash alternative price for the same service
                    (early-bird, LCC incl. access adjustment, Shinkansen,
                    ZIPAIR, foreign-carrier sale fare ...), round-trip basis.
    C_cash        : cash collected on an award ticket (fuel surcharge, airport
                    fees, taxes).  Only paid on the award path.
    M_effective   : expected miles actually consumed, mixing the "standard
                    award seat available" path with the fallback path
                    (JAL: 特典航空券PLUS or e JALポイント; ANA: ANA SKY コイン).

All prices are JPY, round-trip (one-way inputs are doubled on load).
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np
import pandas as pd

PARAM_FILES = [
    "routes.csv",
    "demand_bands.csv",
    "award_miles.csv",
    "award_cash_costs.csv",
    "cash_alternatives.csv",
    "availability.csv",
    "plus_multipliers.csv",
    "floor_rates.csv",
    "anchors.csv",
]
OPTIONAL_FILES = ["plus_caps.csv"]


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
        frames = {}
        for f in PARAM_FILES:
            frames[f[:-4]] = pd.read_csv(d / f, comment="#", skipinitialspace=True)
        sources_path = d.parent / "sources.csv"
        sources = pd.read_csv(sources_path) if sources_path.exists() else pd.DataFrame()
        caps_path = d / "plus_caps.csv"
        plus_caps = pd.read_csv(caps_path, comment="#", skipinitialspace=True) if caps_path.exists() else pd.DataFrame()
        p = cls(
            routes=frames["routes"],
            bands=frames["demand_bands"],
            award_miles=frames["award_miles"],
            award_cash=frames["award_cash_costs"],
            cash_alts=frames["cash_alternatives"],
            availability=frames["availability"],
            plus_mult=frames["plus_multipliers"],
            floor_rates=frames["floor_rates"],
            anchors=frames["anchors"],
            sources=sources,
            plus_caps=plus_caps,
        )
        p._normalise()
        p._validate()
        return p

    # ------------------------------------------------------------------
    def _normalise(self) -> None:
        """Bring every money / mileage figure onto a round-trip basis."""
        am = self.award_miles.copy()
        am["miles_rt"] = np.where(am["basis"].str.lower() == "ow", am["miles"] * 2, am["miles"])
        self.award_miles = am

        ca = self.cash_alts.copy()
        mult = np.where(ca["basis"].str.lower() == "ow", 2.0, 1.0)
        for col in ("price_low_jpy", "price_mode_jpy", "price_high_jpy"):
            ca[col + "_rt"] = ca[col] * mult
        # extra fees (baggage etc.) and access adjustments are entered per
        # round trip already (they are small and route-level).
        for col in ("extra_fees_rt_jpy", "access_adj_rt_jpy"):
            if col not in ca.columns:
                ca[col] = 0.0
            ca[col] = ca[col].fillna(0.0)
        ca["total_low_rt"] = ca["price_low_jpy_rt"] + ca["extra_fees_rt_jpy"] + ca["access_adj_rt_jpy"]
        ca["total_mode_rt"] = ca["price_mode_jpy_rt"] + ca["extra_fees_rt_jpy"] + ca["access_adj_rt_jpy"]
        ca["total_high_rt"] = ca["price_high_jpy_rt"] + ca["extra_fees_rt_jpy"] + ca["access_adj_rt_jpy"]
        if "own_carrier" not in ca.columns:
            ca["own_carrier"] = ""
        ca["own_carrier"] = ca["own_carrier"].fillna("").astype(str)
        self.cash_alts = ca

        ac = self.award_cash.copy()
        mult = np.where(ac["basis"].str.lower() == "ow", 2.0, 1.0)
        ac["amount_rt_jpy"] = ac["amount_jpy"] * mult
        self.award_cash = ac

        if not self.plus_caps.empty:
            pc = self.plus_caps.copy()
            pc["cap_rt"] = np.where(pc["basis"].str.lower() == "ow", pc["cap_miles"] * 2, pc["cap_miles"])
            self.plus_caps = pc

    def _validate(self) -> None:
        required = {
            "routes": {"route_id", "market", "label_ja"},
            "bands": {"band_id", "label_ja", "ana_dom_season", "ana_intl_season", "traveler_weight"},
            "award_miles": {"carrier", "route_id", "cabin", "basis", "season", "miles"},
            "award_cash": {"carrier", "route_id", "cabin", "component", "basis", "amount_jpy"},
            "cash_alts": {"route_id", "cabin_equiv", "band_id", "provider", "product", "basis",
                           "price_low_jpy", "price_mode_jpy", "price_high_jpy", "equivalence"},
            "availability": {"carrier", "market", "cabin_group", "band_id", "p_award", "p_low", "p_high"},
            "plus_mult": {"carrier", "market", "band_id", "k_p10", "k_p50", "k_p90"},
            "floor_rates": {"carrier", "instrument", "yen_per_mile", "representative"},
            "anchors": {"carrier", "route_id", "cabin", "anchor_type", "anchor_price_jpy", "basis"},
        }
        for name, cols in required.items():
            df = getattr(self, name)
            missing = cols - set(df.columns)
            if missing:
                raise ValueError(f"{name}.csv missing columns: {sorted(missing)}")
        w = self.bands["traveler_weight"].sum()
        if not math.isclose(w, 1.0, abs_tol=1e-6):
            raise ValueError(f"demand_bands.traveler_weight must sum to 1 (got {w})")


# ----------------------------------------------------------------------
# helpers
# ----------------------------------------------------------------------
CABIN_GROUP = {"Y": "economy", "PY": "premium", "C": "business", "F": "business",
               "J": "premium", "P": "premium"}


def cabin_group(cabin: str) -> str:
    return CABIN_GROUP.get(cabin, "economy")


def season_for(p: Params, carrier: str, market: str, band_id: str) -> str:
    row = p.bands.loc[p.bands["band_id"] == band_id].iloc[0]
    if carrier == "ANA":
        return row["ana_dom_season"] if market == "domestic" else row["ana_intl_season"]
    return "base"


def award_miles_rt(p: Params, carrier: str, route_id: str, cabin: str, season: str) -> float | None:
    am = p.award_miles
    sel = am[(am.carrier == carrier) & (am.route_id == route_id) & (am.cabin == cabin) & (am.season == season)]
    if sel.empty:
        return None
    return float(sel["miles_rt"].iloc[0])


def award_cash_rt(p: Params, carrier: str, route_id: str, cabin: str) -> tuple[float, dict]:
    ac = p.award_cash
    sel = ac[(ac.carrier == carrier) & (ac.route_id == route_id) & (ac.cabin == cabin)]
    if sel.empty:  # fall back to cabin-agnostic rows
        sel = ac[(ac.carrier == carrier) & (ac.route_id == route_id) & (ac.cabin == "*")]
    comp = sel.groupby("component")["amount_rt_jpy"].sum().to_dict()
    return float(sum(comp.values())), comp


def own_carrier_fare(p: Params, carrier: str, route_id: str, cabin: str, band_id: str) -> dict | None:
    """Cheapest cash fare on the *same* carrier (used for the coin / point fallback)."""
    ca = p.cash_alts
    sel = ca[(ca.route_id == route_id) & (ca.cabin_equiv == cabin) & (ca.band_id == band_id)
             & (ca.own_carrier.str.upper() == carrier)]
    if sel.empty:
        return None
    r = sel.sort_values("total_mode_rt").iloc[0]
    return dict(low=r.total_low_rt, mode=r.total_mode_rt, high=r.total_high_rt,
                provider=r.provider, product=r["product"])


def v_real(p: Params, route_id: str, cabin: str, band_id: str, equivalence=("same", "near")) -> dict | None:
    """Realistic cash alternative: the cheapest alternative of acceptable equivalence."""
    ca = p.cash_alts
    sel = ca[(ca.route_id == route_id) & (ca.cabin_equiv == cabin) & (ca.band_id == band_id)
             & (ca.equivalence.isin(equivalence))]
    if sel.empty:
        return None
    r = sel.sort_values("total_mode_rt").iloc[0]
    return dict(low=float(r.total_low_rt), mode=float(r.total_mode_rt), high=float(r.total_high_rt),
                provider=r.provider, product=r["product"], n_alternatives=int(len(sel)))


def availability(p: Params, carrier: str, market: str, cabin: str, band_id: str) -> tuple[float, float, float]:
    av = p.availability
    g = cabin_group(cabin)
    sel = av[(av.carrier == carrier) & (av.market == market) & (av.cabin_group == g) & (av.band_id == band_id)]
    if sel.empty:
        sel = av[(av.carrier == carrier) & (av.market == market) & (av.cabin_group == "*") & (av.band_id == band_id)]
    if sel.empty:
        raise KeyError(f"no availability row for {carrier}/{market}/{g}/{band_id}")
    r = sel.iloc[0]
    return float(r.p_award), float(r.p_low), float(r.p_high)


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


def plus_applies(carrier: str, market: str, cabin: str) -> bool:
    """JAL 特典航空券PLUS applies to Y/PY/C (and domestic J/F); international First is excluded."""
    if carrier != "JAL":
        return False
    if market == "international" and cabin == "F":
        return False
    return True


def floor_rate(p: Params, carrier: str) -> tuple[float, str]:
    fr = p.floor_rates
    sel = fr[(fr.carrier == carrier) & (fr.representative == 1)]
    if sel.empty:
        raise KeyError(f"no representative floor rate for {carrier}")
    r = sel.iloc[0]
    return float(r.yen_per_mile), f"{r.instrument}"


# ----------------------------------------------------------------------
# core computation
# ----------------------------------------------------------------------
def compute_case(p: Params, carrier: str, route_id: str, cabin: str, band_id: str,
                 v_override: float | None = None, p_override: float | None = None,
                 k_override: float | None = None, c_override: float | None = None,
                 r_override: float | None = None, equivalence=("same", "near")) -> dict | None:
    route = p.routes.loc[p.routes.route_id == route_id].iloc[0]
    market = route["market"]
    season = season_for(p, carrier, market, band_id)
    m_base = award_miles_rt(p, carrier, route_id, cabin, season)
    if m_base is None and carrier == "JAL":
        row = p.bands.loc[p.bands["band_id"] == band_id].iloc[0]
        season = row["ana_intl_season"] if market == "international" else row["ana_dom_season"]
        m_base = award_miles_rt(p, carrier, route_id, cabin, season)
    if m_base is None:
        return None
    vr = v_real(p, route_id, cabin, band_id, equivalence=equivalence)
    if vr is None:
        return None
    V = float(v_override) if v_override is not None else vr["mode"]
    C, comp = award_cash_rt(p, carrier, route_id, cabin)
    if c_override is not None:
        C = float(c_override)
    p_av, p_lo, p_hi = availability(p, carrier, market, cabin, band_id)
    if p_override is not None:
        p_av = float(p_override)
    r_floor, instrument = floor_rate(p, carrier)
    if r_override is not None:
        r_floor = float(r_override)
    own = own_carrier_fare(p, carrier, route_id, cabin, band_id)
    V_own = own["mode"] if own else V  # if no own-carrier fare known, assume = V_real

    # ---- rational path choice -------------------------------------------------
    # Costs are expressed in miles-equivalent: cash is converted at the floor rate r_floor
    # (the yen a mile is guaranteed to fetch via SKY coins / e JAL points).
    cost_points_me = V_own / r_floor                       # buy the cash fare with coins/points, no award needed
    cost_award_me = m_base + C / r_floor                   # standard award seat + cash fees
    award_dominated = cost_award_me > cost_points_me       # award is worse than simply buying with coins/points
    if award_dominated:
        mA, cA, pathA = cost_points_me, 0.0, "points"
    else:
        mA, cA, pathA = m_base, C, "award"
    km = plus_multiplier(p, carrier, market, band_id) if plus_applies(carrier, market, cabin) else None
    k = None
    if km is not None:
        k = float(k_override) if k_override is not None else km[1]
    cap = plus_cap_rt(p, carrier, route_id, cabin)
    mB, cB, pathB = cost_points_me, 0.0, "points"
    m_plus = None
    if k is not None:
        m_plus = k * m_base
        if cap is not None:
            m_plus = min(m_plus, cap)
        if m_plus + C / r_floor < cost_points_me:
            mB, cB, pathB = m_plus, C, "plus"
    m_eff = p_av * mA + (1 - p_av) * mB
    c_exp = p_av * cA + (1 - p_av) * cB
    rpp_base = (V - C) / m_base                            # naive: seat obtained and taken regardless
    rpp_eff = (V - c_exp) / m_eff                          # expected realised value with rational path choice
    rpp_fb = (V - cB) / mB
    m_fb, c_fb, fallback = mB, cB, pathB
    return dict(
        carrier=carrier, route_id=route_id, route_label=route["label_ja"], market=market,
        group=route.get("group", ""), cabin=cabin, band_id=band_id, season=season,
        m_base_rt=m_base, v_real_rt=V, v_real_low=vr["low"], v_real_high=vr["high"],
        v_real_provider=vr["provider"], v_real_product=vr["product"],
        v_own_rt=V_own, c_cash_rt=C, c_components=comp,
        p_award=p_av, p_low=p_lo, p_high=p_hi, k_plus=k, plus_cap_rt=cap, m_plus_rt=m_plus,
        path_if_available=pathA, path_if_unavailable=pathB, award_dominated=award_dominated, fallback=fallback,
        m_fallback_rt=m_fb, m_eff_rt=m_eff, c_expected_rt=c_exp,
        cost_award_me=cost_award_me, cost_points_me=cost_points_me,
        rpp_base=rpp_base, rpp_eff=rpp_eff, rpp_fallback=rpp_fb,
        floor_rate=r_floor, floor_instrument=instrument,
    )


def enumerate_cases(p: Params) -> list[tuple[str, str, str]]:
    """All (carrier, route, cabin) combos that have both an award chart and a cash alternative."""
    combos = set()
    am = p.award_miles[["carrier", "route_id", "cabin"]].drop_duplicates()
    have_alt = set(map(tuple, p.cash_alts[["route_id", "cabin_equiv"]].drop_duplicates().values))
    for _, r in am.iterrows():
        if (r.route_id, r.cabin) in have_alt:
            combos.add((r.carrier, r.route_id, r.cabin))
    return sorted(combos)


def run_all(p: Params) -> pd.DataFrame:
    rows = []
    for carrier, route_id, cabin in enumerate_cases(p):
        for band_id in p.bands["band_id"]:
            res = compute_case(p, carrier, route_id, cabin, band_id)
            if res is None:
                continue
            strict = compute_case(p, carrier, route_id, cabin, band_id, equivalence=("same",))
            if strict is not None:
                res["v_real_strict_rt"] = strict["v_real_rt"]
                res["rpp_base_strict"] = strict["rpp_base"]
                res["rpp_eff_strict"] = strict["rpp_eff"]
                res["award_dominated_strict"] = strict["award_dominated"]
            rows.append(res)
    df = pd.DataFrame(rows)
    df = df.merge(p.bands[["band_id", "label_ja", "traveler_weight"]].rename(columns={"label_ja": "band_label"}),
                  on="band_id", how="left")
    return df


def weighted_summary(df: pd.DataFrame) -> pd.DataFrame:
    """Traveler-weighted RPP per (carrier, route, cabin) across demand bands."""
    def agg(g):
        w = g["traveler_weight"] / g["traveler_weight"].sum()
        # expected value / expected miles, weighted by traveler share
        v = (g["v_real_rt"] * w).sum()
        c = (g["c_expected_rt"] * w).sum()
        m = (g["m_eff_rt"] * w).sum()
        return pd.Series(dict(
            route_label=g["route_label"].iloc[0], market=g["market"].iloc[0], group=g["group"].iloc[0],
            v_real_wavg=v, c_expected_wavg=c, m_eff_wavg=m,
            rpp_eff_weighted=(v - c) / m,
            rpp_eff_min=g["rpp_eff"].min(), rpp_eff_max=g["rpp_eff"].max(),
            rpp_base_min=g["rpp_base"].min(), rpp_base_max=g["rpp_base"].max(),
            rpp_base_wavg=(g["rpp_base"] * w).sum(),
        ))
    return df.groupby(["carrier", "route_id", "cabin"]).apply(agg, include_groups=False).reset_index()


def anchored_values(p: Params, df: pd.DataFrame) -> pd.DataFrame:
    """The 'mileage-blog' valuation: regular fare / lowest-season miles, no cash deduction."""
    an = p.anchors.copy()
    an["anchor_rt_jpy"] = np.where(an["basis"].str.lower() == "ow", an["anchor_price_jpy"] * 2, an["anchor_price_jpy"])
    out = []
    for _, a in an.iterrows():
        sub = df[(df.carrier == a.carrier) & (df.route_id == a.route_id) & (df.cabin == a.cabin)]
        if sub.empty:
            continue
        m_min = sub["m_base_rt"].min()
        anchored = a.anchor_rt_jpy / m_min
        out.append(dict(carrier=a.carrier, route_id=a.route_id, route_label=sub["route_label"].iloc[0],
                        cabin=a.cabin, anchor_type=a.anchor_type, anchor_rt_jpy=a.anchor_rt_jpy,
                        m_min_rt=m_min, anchored_yen_per_mile=anchored,
                        blog_claim_yen_per_mile=a.get("blog_claim_yen_per_mile", np.nan)))
    return pd.DataFrame(out)
